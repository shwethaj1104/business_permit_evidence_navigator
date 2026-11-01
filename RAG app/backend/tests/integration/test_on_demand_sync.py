from contextlib import nullcontext
from dataclasses import replace
from types import SimpleNamespace
from unittest.mock import Mock

import httpx
import pytest

from app.core.errors import AppError
from app.integrations.azure_jobs import AzureJobDispatcher, build_dispatcher
from app.models.domain import PROFILE
from app.repositories.job_repository import JobRepository
from app.schemas.api import SyncRequest
from app.services.ingestion.sync_service import SyncService
from app.services.profile_service import ProfileService
from app.workers import sync_worker


def queue(db):
    # Initialize the production exclusivity constraint in the isolated test database.
    db.update_runs.create_index("profile_id", unique=True, partialFilterExpression={"active": True})
    return JobRepository(db)


def test_click_saves_then_dispatches_once_and_claims_only_target(db, model):
    # Racing clicks reuse a durable job and cannot claim another profile's work.
    model.settings = replace(model.settings, openai_key="test-key")
    jobs, dispatcher = queue(db), Mock()
    dispatcher.start.side_effect = lambda job_id: jobs.get(job_id) or pytest.fail("Not saved first")
    service = SyncService(ProfileService(), Mock(), jobs, Mock(), model, Mock(), Mock(), dispatcher)
    first = service.start(SyncRequest(profile_id=PROFILE.id))
    assert service.start(SyncRequest(profile_id=PROFILE.id)).id == first.id
    dispatcher.start.assert_called_once_with(first.id)
    assert jobs.claim("worker", "unrelated") is None
    assert jobs.claim("worker", first.id).id == first.id
    assert jobs.claim("duplicate", first.id) is None


def test_dispatch_failure_leaves_retriable_job(db, model):
    # Release the launch reservation on failure so a later click can retry the same job.
    model.settings = replace(model.settings, openai_key="test-key")
    jobs, dispatcher = queue(db), Mock()
    dispatcher.start.side_effect = RuntimeError("Unavailable")
    service = SyncService(ProfileService(), Mock(), jobs, Mock(), model, Mock(), Mock(), dispatcher)
    with pytest.raises(AppError, match="saved"):
        service.start(SyncRequest(profile_id=PROFILE.id))
    row = jobs.list(PROFILE.id)[0]
    assert row.status == "queued" and row.error
    dispatcher.start.side_effect = None
    assert service.start(SyncRequest(profile_id=PROFILE.id)).id == row.id
    assert dispatcher.start.call_count == 2


def test_azure_override_preserves_secrets_and_targets_job(settings):
    # Preserve the full deployed template rather than replacing secret-bearing environment entries.
    settings = replace(
        settings,
        sync_dispatch_mode="azure",
        azure_sync_job_resource_id="/subscriptions/sub/resourceGroups/rg/providers/Microsoft.App/jobs/sync",
    )
    requests = []

    def handle(request):
        # Capture ARM requests locally without calling Azure or acquiring real tokens.
        requests.append(request)
        if request.method == "GET":
            return httpx.Response(
                200,
                json={
                    "properties": {
                        "template": {
                            "containers": [
                                {
                                    "name": "worker",
                                    "image": "image:v1",
                                    "env": [{"name": "MONGODB_URI", "secretRef": "mongo"}],
                                }
                            ]
                        }
                    }
                },
            )
        return httpx.Response(202)

    credential = Mock()
    credential.get_token.return_value.token = "test-token"
    factory = Mock(return_value=nullcontext(credential))
    AzureJobDispatcher(settings, factory, httpx.MockTransport(handle)).start("saved-job")
    import json

    body = json.loads(requests[1].content)
    assert body["containers"][0]["args"] == ["--job-id", "saved-job"]
    assert body["containers"][0]["env"][0]["secretRef"] == "mongo"
    assert body["containers"][0]["image"] == "image:v1"
    assert requests[1].url.path.endswith("/start")
    assert build_dispatcher(replace(settings, sync_dispatch_mode="local")) is None


@pytest.mark.parametrize("has_job", [True, False])
def test_targeted_worker_exits_and_closes_model(monkeypatch, settings, has_job):
    # A one-shot execution makes one claim and never enters the idle polling loop.
    services = SimpleNamespace(jobs=Mock(), sync=Mock(), model=Mock())
    services.jobs.claim.return_value = SimpleNamespace(id="target", attempts=1) if has_job else None
    services.jobs.get.return_value = SimpleNamespace(status="completed")
    monkeypatch.setattr(sync_worker, "get_settings", lambda: settings)
    monkeypatch.setattr(sync_worker, "database_connection", lambda _: nullcontext(object()))
    monkeypatch.setattr(sync_worker, "build_services", lambda _: services)
    monkeypatch.setattr(sync_worker.signal, "signal", lambda *_: None)
    assert sync_worker.run("target") == 0
    assert services.jobs.claim.call_count == 1
    assert services.sync.process.call_count == int(has_job)
    services.model.close.assert_called_once()
