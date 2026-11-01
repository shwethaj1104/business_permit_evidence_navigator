from app.core.errors import AppError
from app.core.logging import logged_operation
from app.schemas.api import AnswerResponse, Citation


class ChatService:
    """Answer only from currently approved MongoDB evidence without web dependencies."""

    def __init__(self, profiles, knowledge, conversations, model):
        # Inject only retrieval, persistence, and tool-free generation boundaries.
        self.profiles, self.knowledge = profiles, knowledge
        self.conversations, self.model = conversations, model

    @logged_operation("chat.history")
    def history(self, conversation_id, before=None):
        # Retrieve a bounded conversation without making a model call.
        return self.conversations.get(conversation_id, before)

    @logged_operation("chat.list")
    def list_conversations(self, profile_id, before=None):
        # Scope saved-chat navigation to the validated business profile.
        if profile_id is not None:
            self.profiles.require(profile_id)
        return self.conversations.list(profile_id, before)

    @logged_operation("chat.rename")
    def rename(self, conversation_id, title):
        # Reject blank titles before updating persisted navigation metadata.
        title = title.strip()
        if not title:
            raise AppError("Enter a chat title.", 422)
        self.conversations.rename(conversation_id, title)

    @logged_operation("chat.delete")
    def delete(self, conversation_id):
        # Remove one saved conversation and its separately stored messages.
        self.conversations.delete(conversation_id)

    @logged_operation("chat.answer")
    def send(self, request):
        # Validate context and evidence before any paid generation.
        if not request.message.strip():
            raise AppError("Enter a question before sending.", 422)
        if request.profile_id is None:
            answer = AnswerResponse(
                kind="follow_up",
                message="Hello! Welcome to Permit Navigator, your UAE business setup assistant. "
                "I can help prepare a checklist using reviewed official evidence. "
                "Please choose the five business options below, then select Generate my checklist. "
                "Our current pilot covers a new Dubai mainland IT/software company with an LLC structure.",
                items=[],
                gaps=[],
                citations=[],
            )
            return self.conversations.append(None, request.conversation_id, request.message, answer)
        profile = self.profiles.require(request.profile_id)
        history = []
        if request.conversation_id:
            previous = self.conversations.get(request.conversation_id)
            if previous.profile_id is not None and previous.profile_id != profile.id:
                raise AppError("Start a new conversation when the business profile changes.", 409)
            history = [{"role": row["role"], "text": row["text"]} for row in previous.messages[-8:]]
        if not self.knowledge.active_versions(profile.id):
            answer = AnswerResponse(
                kind="gap",
                message="No approved evidence is available for this profile yet. "
                "Open Knowledge Updates, sync official sources, and review a version first.",
                items=[],
                gaps=["No approved source versions."],
                citations=[],
            )
        else:
            question = request.message.strip()
            if not question:
                raise AppError("Enter a question before sending.", 422)
            vector = self.model.embed([question])[0]
            evidence = self.knowledge.retrieve(profile.id, vector, question)
            if not evidence:
                answer = AnswerResponse(
                    kind="gap",
                    message="No relevant active evidence was retrieved.",
                    items=[],
                    gaps=["The current collection cannot support this answer."],
                    citations=[],
                )
            else:
                passages = [{"id": row.id, "text": row.text, "locator": row.locator} for row in evidence]
                generated = self.model.answer(profile, question, passages, history)
                answer = validate_answer(generated, evidence, self.knowledge)
        return self.conversations.append(profile.id, request.conversation_id, request.message, answer)


def validate_answer(generated, evidence, knowledge):
    # Reject unsupported citation IDs and recheck active versions after generation.
    by_id = {row.id: row for row in evidence}
    used = {citation for item in generated.items for citation in item.evidence_ids}
    if generated.kind == "checklist" and (
        not generated.items
        or any(not item.evidence_ids for item in generated.items)
        or not used <= by_id.keys()
    ):
        raise AppError("The generated checklist failed evidence validation. Please retry.", 502)
    if generated.kind != "checklist" and generated.items:
        raise AppError("The model returned inconsistent answer content. Please retry.", 502)
    active = set(knowledge.active_versions(evidence[0].profile_id))
    if any(by_id[key].version_id not in active for key in used):
        raise AppError("Source versions changed while answering. Please resend your question.", 409)
    sources = {row.id: row for row in knowledge.sources(evidence[0].profile_id)}
    citations = []
    for key in sorted(used):
        chunk = by_id[key]
        version = knowledge.version(chunk.version_id)
        source = sources[chunk.source_id]
        citations.append(
            Citation(
                id=key,
                source_id=source.id,
                version_id=version.id,
                title=version.title,
                url=version.url,
                locator=chunk.locator,
                excerpt=chunk.text,
                fetched_at=version.fetched_at.isoformat(),
                last_checked_at=source.last_successful_fetch_at.isoformat()
                if source.last_successful_fetch_at
                else None,
                source_published_at=version.source_published_at,
                source_updated_at=version.source_updated_at,
                newer_version_available=source.latest_version_id != version.id,
            )
        )
    return AnswerResponse(**generated.model_dump(), citations=citations)
