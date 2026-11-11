from dataclasses import replace

from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.main import create_app


def test_unconfigured_app_is_usable_without_login(monkeypatch):
    # Verify setup/profile endpoints work while data endpoints fail actionably without credentials.
    settings = replace(get_settings(), mongodb_uri="", openai_key="")
    monkeypatch.setattr("app.main.get_settings", lambda: settings)
    with TestClient(create_app()) as client:
        assert client.get("/api/v1/health").json()["status"] == "setup_required"
        profiles = client.get("/api/v1/profiles").json()["profiles"]
        assert len(profiles) == 7
        response = client.post("/api/v1/knowledge/sync", json={"profile_id": profiles[0]["id"]})
        assert response.status_code == 503
        assert "MONGODB_URI" in response.json()["detail"]
        assert client.get("/openapi.json").status_code == 200


def test_manual_job_and_gap_round_trip_without_provider_calls(monkeypatch, db, settings):
    # Exercise controller serialization and persisted jobs using a fake database, never a paid provider.
    from contextlib import contextmanager

    configured = replace(settings, openai_key="test-only-not-a-real-key")
    monkeypatch.setattr(
        "app.integrations.openai.client.LanguageModel.classify_intent", lambda *_: "permit_question"
    )

    @contextmanager
    def connection(_settings):
        # Inject a test database instead of opening Atlas.
        yield db

    monkeypatch.setattr("app.main.get_settings", lambda: configured)
    monkeypatch.setattr("app.api.dependencies.get_settings", lambda: configured)
    monkeypatch.setattr("app.main.database_connection", connection)
    db.update_runs.create_index("profile_id", unique=True, partialFilterExpression={"active": True})
    with TestClient(create_app()) as client:
        profile = client.get("/api/v1/profiles").json()["profiles"][0]["id"]
        first = client.post("/api/v1/knowledge/sync", json={"profile_id": profile})
        assert first.status_code == 202, first.text
        assert first.json()["status"] == "queued"
        assert (
            client.post("/api/v1/knowledge/sync", json={"profile_id": profile}).json()["id"]
            == first.json()["id"]
        )
        assert client.get("/api/v1/knowledge/jobs", params={"profile_id": profile}).status_code == 200
        assert client.get("/api/v1/knowledge/sources", params={"profile_id": profile}).status_code == 200
        answer = client.post("/api/v1/chat", json={"profile_id": profile, "message": "Prepare a checklist"})
        assert answer.status_code == 200, answer.text
        assert answer.json()["messages"][-1]["answer"]["kind"] == "gap"
        saved_id = answer.json()["id"]
        history = client.get("/api/v1/chat/conversations", params={"profile_id": profile})
        assert history.status_code == 200, history.text
        assert history.json()["conversations"][0]["id"] == saved_id
        restored = client.get(f"/api/v1/chat/conversations/{saved_id}")
        assert restored.status_code == 200, restored.text
        assert len(restored.json()["messages"]) == 2
        assert restored.json()["messages"][0]["order"] == 0
        assert "_id" not in first.json()

        from app.models.domain import utcnow

        now = utcnow()
        db.document_versions.insert_one(
            {
                "id": "test-version",
                "source_id": "source",
                "profile_id": profile,
                "title": "Synthetic test source",
                "url": "https://u.ae/test",
                "status": "pending",
                "summary": "Test",
                "previous_version_id": None,
                "text": "Full test text",
                "diff": "+ Full test text",
                "section_changes": [],
                "fetched_at": now,
                "change_detected_at": now,
                "source_published_at": None,
                "source_updated_at": None,
                "effective_from": None,
            }
        )
        summaries = client.get("/api/v1/knowledge/versions", params={"profile_id": profile})
        assert summaries.status_code == 200, summaries.text
        assert "text" not in summaries.json()[0]
        detail = client.get("/api/v1/knowledge/versions/test-version")
        assert detail.status_code == 200, detail.text
        assert detail.json()["text"] == "Full test text"
