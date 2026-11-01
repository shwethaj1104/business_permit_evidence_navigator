import logging

import pytest
from fastapi.testclient import TestClient

from app.core.logging import ContextFilter, log_context, log_failure, logged_operation
from app.main import create_app


def test_failure_logs_include_location_without_exception_text(caplog):
    # Preserve stack locations while excluding secret-like exception content.
    with caplog.at_level(logging.INFO):

        @logged_operation("test.operation")
        def fail():
            # Raise a sentinel to prove the exception body never reaches logs.
            raise RuntimeError("SECRET_SENTINEL mongodb+srv://user:password@host")

        with pytest.raises(RuntimeError):
            fail()
    assert "stage=test.operation" in caplog.text
    assert "test_logging.py" in caplog.text
    assert "SECRET_SENTINEL" not in caplog.text
    assert "password@host" not in caplog.text


def test_context_restores_request_and_job_ids():
    # Correlation data must not leak from one request/job into the next.
    filter = ContextFilter()
    with log_context(request_id="request-1", job_id="job-1"):
        record = logging.makeLogRecord({})
        filter.filter(record)
        assert record.request_id == "request-1"
        assert record.job_id == "job-1"
    record = logging.makeLogRecord({})
    filter.filter(record)
    assert record.request_id == "-"
    assert record.job_id == "-"


def test_http_errors_have_correlated_safe_logs(monkeypatch, settings, caplog):
    # Log endpoint, status and validation location without submitted message content.
    monkeypatch.setattr("app.main.get_settings", lambda: settings)
    from app.api.dependencies import chat_controller

    application = create_app()
    application.dependency_overrides[chat_controller] = lambda: object()
    with caplog.at_level(logging.INFO), TestClient(application) as client:
        response = client.post("/api/v1/chat", json={"message": "SECRET_QUESTION_SENTINEL", "profile_id": []})
        assert response.status_code == 422
        assert response.headers["x-request-id"]
        assert "route=/api/v1/chat status=422" in caplog.text
        assert "SECRET_QUESTION_SENTINEL" not in caplog.text
        response = client.get("/api/v1/knowledge/jobs", params={"profile_id": "test"})
        assert response.status_code == 503
        assert response.headers["x-request-id"]
        assert "stage=http.application" in caplog.text


def test_failure_cause_chain_preserves_safe_codes(caplog):
    # Keep MongoDB/provider error codes without printing their response bodies.
    from pymongo.errors import OperationFailure

    from app.core.errors import AppError

    try:
        try:
            raise OperationFailure("SECRET_PROVIDER_BODY", code=13)
        except OperationFailure as cause:
            raise AppError("Safe hint") from cause
    except AppError as exc:
        with caplog.at_level(logging.ERROR):
            log_failure("test.database", exc)
    assert "code=13" in caplog.text
    assert "SECRET_PROVIDER_BODY" not in caplog.text


def test_application_error_hint_redacts_configured_credentials(monkeypatch, caplog):
    # Keep controlled application hints useful without echoing a configured credential.
    from app.core.errors import AppError

    monkeypatch.setenv("OPENAI_API_KEY", "SECRET_KEY_SENTINEL")
    with caplog.at_level(logging.ERROR):
        log_failure("test.hint", AppError("Configuration failed SECRET_KEY_SENTINEL"))
    assert "Configuration failed" in caplog.text
    assert "SECRET_KEY_SENTINEL" not in caplog.text
    assert "[redacted]" in caplog.text
