from unittest.mock import Mock

import pytest

from app.core.errors import AppError
from app.models.domain import PROFILE
from app.repositories.conversation_repository import ConversationRepository
from app.schemas.api import ChatRequest, ConversationResponse
from app.services.profile_service import ProfileService
from app.services.retrieval.chat_service import ChatService


def test_welcome_persists_and_profile_binds_without_losing_messages(db, model):
    # Retain welcome history when a complete profile unlocks evidence retrieval.
    repository = ConversationRepository(db)
    knowledge = Mock()
    knowledge.active_versions.return_value = []
    service = ChatService(ProfileService(), knowledge, repository, model)
    welcome = service.send(ChatRequest(message="Hello, how do I start a business?"))
    assert welcome.profile_id is None
    assert welcome.messages[-1]["answer"]["kind"] == "follow_up"
    assert "five business options" in welcome.messages[-1]["text"]
    model.embed.assert_not_called()
    model.answer.assert_not_called()
    knowledge.active_versions.assert_not_called()
    assert repository.list(None)["conversations"][0]["id"] == welcome.id
    response = service.send(
        ChatRequest(profile_id=PROFILE.id, conversation_id=welcome.id, message="Generate checklist")
    )
    assert response.id == welcome.id
    assert response.profile_id == PROFILE.id
    assert len(response.messages) == 4
    assert ConversationResponse.model_validate(response.model_dump()).profile_id == PROFILE.id
    assert repository.list(PROFILE.id)["conversations"][0]["id"] == welcome.id
    with pytest.raises(AppError):
        service.send(ChatRequest(conversation_id=welcome.id, message="Change profile"))


def test_all_chat_history_paginates_across_profiles(db):
    # Include unconfigured and configured chats in the same stable navigation cursor.
    repository = ConversationRepository(db)
    from app.schemas.api import AnswerResponse

    answer = AnswerResponse(kind="follow_up", message="Welcome", items=[], gaps=[], citations=[])
    for index in range(22):
        repository.append(None if index % 2 else PROFILE.id, None, f"Question {index}", answer)
    first = repository.list(None)
    second = repository.list(None, first["next_cursor"])
    assert len(first["conversations"]) == 20
    assert len(second["conversations"]) == 2
    assert len({row["id"] for row in first["conversations"] + second["conversations"]}) == 22


def test_rename_and_delete_preserve_other_chats(db, model):
    # Persist title edits and remove only the selected chat and its message records.
    repository = ConversationRepository(db)
    service = ChatService(ProfileService(), Mock(), repository, model)
    first = service.send(ChatRequest(message="Hello"))
    other = service.send(ChatRequest(message="Another business"))
    service.rename(first.id, "  My IT company  ")
    assert repository.require(first.id)["title"] == "My IT company"
    assert len(repository.get(first.id).messages) == 2
    with pytest.raises(AppError):
        service.rename(first.id, "   ")
    service.delete(first.id)
    assert db.conversation_messages.count_documents({"conversation_id": first.id}) == 0
    assert len(repository.get(other.id).messages) == 2
    with pytest.raises(AppError):
        repository.get(first.id)
    with pytest.raises(AppError):
        service.delete(first.id)
