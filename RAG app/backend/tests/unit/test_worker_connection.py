from unittest.mock import Mock

import pytest
from pymongo.errors import AutoReconnect, OperationFailure

from app.core.errors import AppError
from app.db.client import database_connection
from app.workers.sync_worker import claim_next_job


def test_context_does_not_relabel_queue_failure(monkeypatch, settings):
    # Keep errors inside a connected session distinct from initial connection errors.
    from dataclasses import replace

    client = Mock()
    client.__getitem__ = Mock(return_value="database")
    monkeypatch.setattr("app.db.client.MongoClient", lambda *args, **kwargs: client)
    original = OperationFailure("Queue permission denied", code=13)
    with (
        pytest.raises(OperationFailure) as caught,
        database_connection(replace(settings, mongodb_uri="mongodb://test-only")),
    ):
        raise original
    assert caught.value is original
    client.close.assert_called_once()


def test_initial_connection_failure_is_translated(monkeypatch, settings):
    # Translate failed startup pings and always close the client.
    from dataclasses import replace

    client = Mock()
    client.admin.command.side_effect = AutoReconnect("Temporary test disconnection")
    monkeypatch.setattr("app.db.client.MongoClient", lambda *args, **kwargs: client)
    with (
        pytest.raises(AppError, match="connection failed"),
        database_connection(replace(settings, mongodb_uri="mongodb://test-only")),
    ):
        pytest.fail("Must not enter a failed connection")
    client.close.assert_called_once()


def test_worker_retries_temporary_queue_disconnection():
    # A transient queue network failure must not terminate the worker.
    jobs = Mock()
    jobs.claim.side_effect = [AutoReconnect("Temporary test disconnection"), None]
    assert claim_next_job(jobs, "worker") is None
    assert claim_next_job(jobs, "worker") is None
    assert jobs.claim.call_count == 2


def test_worker_reports_permission_failure_without_secret_details():
    # Preserve the useful error code without echoing arbitrary provider text.
    jobs = Mock()
    jobs.claim.side_effect = OperationFailure("sensitive provider detail", code=13)
    with pytest.raises(AppError, match="readWrite") as caught:
        claim_next_job(jobs, "worker")
    assert "13" in caught.value.message
    assert "sensitive" not in caught.value.message
