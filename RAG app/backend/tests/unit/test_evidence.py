from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from app.core.errors import AppError
from app.models.domain import PROFILE, GeneratedAnswer
from app.schemas.api import ChatRequest
from app.services.profile_service import ProfileService
from app.services.retrieval.chat_service import ChatService, validate_answer


@pytest.mark.parametrize("evidence_ids", [[], ["invented"]])
def test_reject_unsupported_checklist_citations(evidence_ids):
    # Never emit a checklist whose item lacks retrieved supporting IDs.
    generated = GeneratedAnswer(
        kind="checklist",
        message="Checklist",
        gaps=[],
        items=[
            {
                "title": "Requirement",
                "detail": "Detail",
                "condition": "Applicable",
                "evidence_ids": evidence_ids,
            }
        ],
    )
    with pytest.raises(AppError):
        validate_answer(generated, [], Mock())


def test_publication_change_during_generation_is_rejected():
    # Prevent an answer from citing a version replaced while the model was running.
    generated = GeneratedAnswer(
        kind="checklist",
        message="Checklist",
        gaps=[],
        items=[
            {"title": "Requirement", "detail": "Detail", "condition": "Applicable", "evidence_ids": ["chunk"]}
        ],
    )
    knowledge = Mock()
    knowledge.active_versions.return_value = ["new"]
    chunk = SimpleNamespace(id="chunk", version_id="old", profile_id=PROFILE.id)
    with pytest.raises(AppError, match="changed"):
        validate_answer(generated, [chunk], knowledge)


def test_empty_database_skips_embeddings_and_answer_generation(model):
    # Return an explicit gap without embeddings or evidence-answer generation.
    knowledge, conversations = Mock(), Mock()
    knowledge.active_versions.return_value = []
    chat = ChatService(ProfileService(), knowledge, conversations, model)
    chat.send(ChatRequest(profile_id=PROFILE.id, message="Generate checklist"))
    model.embed.assert_not_called()
    model.answer.assert_not_called()
    assert conversations.append.call_args.args[-1].kind == "gap"


def test_profile_change_rejects_conversation_before_paid_call(model):
    # Keep another profile's history out of the selected business context.
    conversations = Mock()
    conversations.get.return_value = SimpleNamespace(profile_id="other")
    chat = ChatService(ProfileService(), Mock(), conversations, model)
    with pytest.raises(AppError):
        chat.send(ChatRequest(profile_id=PROFILE.id, conversation_id="conversation", message="Checklist"))
    model.embed.assert_not_called()


def test_valid_citations_preserve_version_dates_and_newer_version_warning():
    # Resolve URLs and provenance from stored records, not model output.
    from app.models.domain import utcnow

    now = utcnow()
    knowledge = Mock()
    knowledge.active_versions.return_value = ["approved"]
    knowledge.sources.return_value = [
        SimpleNamespace(id="source", latest_version_id="new-pending", last_successful_fetch_at=now)
    ]
    knowledge.version.return_value = SimpleNamespace(
        id="approved",
        title="Official guide",
        url="https://u.ae/guide",
        fetched_at=now,
        source_published_at=None,
        source_updated_at=None,
    )
    evidence = [
        SimpleNamespace(
            id="chunk",
            version_id="approved",
            profile_id=PROFILE.id,
            source_id="source",
            locator="Documents",
            text="Source passage",
        )
    ]
    generated = GeneratedAnswer(
        kind="checklist",
        message="Supported preparation item",
        gaps=[],
        items=[
            {
                "title": "Requirement",
                "detail": "Source passage",
                "condition": "As stated",
                "evidence_ids": ["chunk"],
            }
        ],
    )
    answer = validate_answer(generated, evidence, knowledge)
    assert answer.citations[0].url == "https://u.ae/guide"
    assert answer.citations[0].source_published_at is None
    assert answer.citations[0].newer_version_available
