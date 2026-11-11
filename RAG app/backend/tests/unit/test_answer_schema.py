import json
from dataclasses import replace
from types import SimpleNamespace
from unittest.mock import Mock

import httpx
import pytest
from openai import OpenAI
from pydantic import ValidationError

from app.core.errors import AppError
from app.integrations.openai.answer_schema import evidence_answer_schema
from app.integrations.openai.client import LanguageModel
from app.models.domain import PROFILE, GeneratedAnswer
from app.services.retrieval.chat_service import validate_answer


def answer_payload(kind="checklist", evidence_ids=None):
    # Build an output fixture independently of the provider-specific wrapper schema.
    return {
        "kind": kind,
        "message": "Preparation guidance",
        "items": [
            {
                "title": "Identify activity",
                "detail": "Confirm the proposed business activity.",
                "condition": "As stated in the source",
                "evidence_ids": ["retrieved-1"] if evidence_ids is None else evidence_ids,
            }
        ],
        "gaps": ["Confirm the exact activity code."],
    }


@pytest.mark.parametrize("kind", ["gap", "follow_up"])
def test_limitations_still_work_without_checklist_items(kind):
    # Strong citation requirements must not force invented requirements when evidence is insufficient.
    payload = answer_payload(kind)
    payload["items"] = []
    result = evidence_answer_schema(["retrieved-1"]).model_validate({"answer": payload})
    assert result.answer.kind == kind
    assert result.answer.items == []


@pytest.mark.parametrize("evidence_ids", [[], ["invented"], ["old-history-id"], ["retrieved-1", "invented"]])
def test_generation_schema_rejects_missing_or_non_retrieved_citations(evidence_ids):
    # An older conversation citation must not enter this retrieval's generated checklist.
    schema = evidence_answer_schema(["retrieved-1", "retrieved-2"])
    with pytest.raises(ValidationError):
        schema.model_validate({"answer": answer_payload(evidence_ids=evidence_ids)})


@pytest.mark.parametrize("kind,has_items", [("checklist", False), ("gap", True), ("follow_up", True)])
def test_generation_schema_rejects_inconsistent_answer_kinds(kind, has_items):
    # The provider must choose either a non-empty cited checklist or an item-free limitation.
    payload = answer_payload(kind)
    if not has_items:
        payload["items"] = []
    with pytest.raises(ValidationError):
        evidence_answer_schema(["retrieved-1"]).model_validate({"answer": payload})


def test_language_model_sends_strict_evidence_schema_and_unwraps_one_response(settings):
    # Exercise the real SDK request/parse boundary without network access or paid calls.
    requests = []

    def provider(request):
        # Inspect the wire schema and return one realistic structured provider response.
        body = json.loads(request.content)
        requests.append(body)
        format_ = body["text"]["format"]
        assert format_["strict"] is True
        schema = format_["schema"]
        assert schema["type"] == "object"
        assert "anyOf" not in schema
        assert "anyOf" in schema["properties"]["answer"]
        item = schema["$defs"]["CitedChecklistItem"]["properties"]["evidence_ids"]
        assert item["minItems"] == 1
        assert item["items"]["enum"] == ["retrieved-1", "retrieved-2"]
        assert schema["$defs"]["CitedChecklist"]["properties"]["items"]["minItems"] == 1
        assert schema["$defs"]["EvidenceLimitation"]["properties"]["items"]["maxItems"] == 0
        assert not body.get("tools")
        return httpx.Response(
            200,
            json={
                "id": "resp_test",
                "object": "response",
                "created_at": 1,
                "status": "completed",
                "model": settings.model,
                "output": [
                    {
                        "id": "msg_test",
                        "type": "message",
                        "role": "assistant",
                        "status": "completed",
                        "content": [
                            {
                                "type": "output_text",
                                "text": json.dumps({"answer": answer_payload()}),
                                "annotations": [],
                            }
                        ],
                    }
                ],
                "usage": {"input_tokens": 1, "output_tokens": 1, "total_tokens": 2},
            },
        )

    model = LanguageModel(replace(settings, openai_key="test-only"))
    model._client = OpenAI(
        api_key="test-only", http_client=httpx.Client(transport=httpx.MockTransport(provider))
    )
    try:
        result = model.answer(
            PROFILE,
            "Prepare a checklist",
            [
                {"id": "retrieved-2", "text": "Second passage", "locator": "Requirements"},
                {
                    "id": "retrieved-1",
                    "text": "Confirm the proposed business activity.",
                    "locator": "Activity",
                },
            ],
            [],
        )
    finally:
        model.close()
    assert len(requests) == 1
    assert isinstance(result, GeneratedAnswer)
    assert result.items[0].evidence_ids == ["retrieved-1"]
    assert set(result.model_dump()) == {"kind", "message", "items", "gaps"}


def test_validator_logs_only_reason_and_counts_for_rejected_ids(caplog):
    # Explain a rejected response without logging model text, evidence content or arbitrary IDs.
    generated = GeneratedAnswer.model_validate(answer_payload(evidence_ids=["SECRET_MODEL_ID"]))
    generated.message = "SECRET_GENERATION_TEXT"
    knowledge = Mock()
    with pytest.raises(AppError, match="evidence validation"):
        validate_answer(generated, [SimpleNamespace(id="retrieved-1")], knowledge)
    assert "reasons=unknown_evidence_ids" in caplog.text
    assert "unknown_id_count=1" in caplog.text
    assert "retrieved_count=1" in caplog.text
    assert "SECRET_MODEL_ID" not in caplog.text
    assert "SECRET_GENERATION_TEXT" not in caplog.text
    knowledge.active_versions.assert_not_called()


def test_schema_does_not_generate_without_retrieved_ids():
    # An empty retrieval must be handled as a gap before contacting the provider.
    with pytest.raises(ValueError, match="retrieved evidence"):
        evidence_answer_schema([])
