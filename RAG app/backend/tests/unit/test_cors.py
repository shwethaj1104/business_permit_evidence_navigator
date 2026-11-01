from dataclasses import replace

from fastapi.testclient import TestClient

from app.main import create_app


def test_cors_allows_only_configured_frontend(monkeypatch, settings):
    # Allow the deployed browser origin without opening cross-origin access to other sites.
    monkeypatch.setattr(
        "app.main.get_settings", lambda: replace(settings, cors_origins=("https://demo.example",))
    )
    client = TestClient(create_app())
    headers = {
        "Origin": "https://demo.example",
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "content-type",
    }
    response = client.options("/api/v1/chat", headers=headers)
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "https://demo.example"
    response = client.options("/api/v1/chat", headers={**headers, "Origin": "https://other.example"})
    assert response.status_code == 400
    assert "access-control-allow-origin" not in response.headers
