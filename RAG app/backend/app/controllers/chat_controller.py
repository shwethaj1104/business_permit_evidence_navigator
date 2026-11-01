from fastapi.encoders import jsonable_encoder

from app.schemas.api import ConversationPage, ConversationResponse


class ChatController:
    """Map conversation use cases into public response contracts."""

    def __init__(self, service):
        # Keep HTTP mapping separate from retrieval business rules.
        self.service = service

    def send(self, request):
        # Serialize only the fields declared by the public conversation contract.
        return ConversationResponse.model_validate(jsonable_encoder(self.service.send(request).model_dump()))

    def history(self, conversation_id, before=None):
        # Return stored history without invoking the model.
        return ConversationResponse.model_validate(
            jsonable_encoder(self.service.history(conversation_id, before).model_dump())
        )

    def list(self, profile_id, before=None):
        # Map history summaries without exposing stored message bodies.
        return ConversationPage.model_validate(
            jsonable_encoder(self.service.list_conversations(profile_id, before))
        )

    def rename(self, conversation_id, request):
        # Delegate title updates without returning message bodies.
        self.service.rename(conversation_id, request.title)

    def delete(self, conversation_id):
        # Delegate conversation removal without making provider calls.
        self.service.delete(conversation_id)
