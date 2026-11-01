from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response

from app.api.dependencies import chat_controller
from app.controllers.chat_controller import ChatController
from app.schemas.api import ChatRequest, ConversationPage, ConversationResponse, RenameConversationRequest

router = APIRouter(prefix="/chat", tags=["chat"])
Controller = Annotated[ChatController, Depends(chat_controller)]


@router.post("", response_model=ConversationResponse)
def send_message(request: ChatRequest, controller: Controller):
    # Answer a question using approved database evidence only.
    return controller.send(request)


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
def get_conversation(
    conversation_id: str, controller: Controller, before: int | None = Query(default=None, ge=0)
):
    # Restore anonymous conversation history without generating a new answer.
    return controller.history(conversation_id, before)


@router.get("/conversations", response_model=ConversationPage)
def list_conversations(
    controller: Controller,
    profile_id: str | None = None,
    before: str | None = Query(default=None, max_length=64),
):
    # List saved chats with a cursor rather than fetching every message at once.
    return controller.list(profile_id, before)


@router.patch("/conversations/{conversation_id}", status_code=204)
def rename_conversation(conversation_id: str, request: RenameConversationRequest, controller: Controller):
    # Rename a saved conversation in MongoDB.
    controller.rename(conversation_id, request)
    return Response(status_code=204)


@router.delete("/conversations/{conversation_id}", status_code=204)
def delete_conversation(conversation_id: str, controller: Controller):
    # Delete one conversation and its messages from MongoDB.
    controller.delete(conversation_id)
    return Response(status_code=204)
