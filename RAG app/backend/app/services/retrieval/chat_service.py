import logging
import re

from app.core.errors import AppError
from app.core.logging import logged_operation
from app.schemas.api import AnswerResponse, Citation

logger = logging.getLogger(__name__)


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
        # Enforce scope before retrieval and collect a complete profile inside one assistant turn.
        question = request.message.strip()
        if not question:
            raise AppError("Enter a question before sending.", 422)
        previous = self.conversations.get(request.conversation_id) if request.conversation_id else None
        profile_id = request.profile_id or (previous.profile_id if previous else None)
        profile = self.profiles.require(profile_id) if profile_id else None
        if previous and previous.profile_id and previous.profile_id != profile_id:
            raise AppError("Start a new conversation when the business profile changes.", 409)
        history = (
            [{"role": row["role"], "text": row["text"]} for row in previous.messages[-8:]] if previous else []
        )
        normalized = re.sub(r"[^a-z ]", "", question.lower()).strip()
        greetings = {
            "hi",
            "hello",
            "hey",
            "hi there",
            "hello there",
            "good morning",
            "good afternoon",
            "good evening",
            "thank you",
            "thanks",
            "how are you",
        }
        last_answer = previous.messages[-1].get("answer") or {} if previous and previous.messages else {}
        offered_setup = last_answer.get("offers_setup", False) or (
            "Would you like help preparing a business setup checklist?" in last_answer.get("message", "")
        )
        accepted_setup = offered_setup and normalized in {
            "yes",
            "yes please",
            "sure",
            "sure please",
            "okay",
            "ok",
            "please",
            "lets do it",
            "lets start",
            "absolutely",
        }
        declined_setup = offered_setup and normalized in {"no", "no thanks", "not now", "no thank you"}
        if accepted_setup:
            intent = "business_setup"
        elif declined_setup:
            intent = "decline"
        elif normalized in greetings:
            intent = "greeting"
        else:
            intent = self.model.classify_intent(
                question, history, [row.model_dump() for row in self.profiles.list()]
            )
        if intent == "greeting":
            answer = AnswerResponse(
                kind="follow_up",
                message="Hello! Welcome to Permit Navigator. I’m your UAE business permit assistant. "
                "How can I help with your business setup today?",
                items=[],
                gaps=[],
                citations=[],
                offers_setup=True,
            )
        elif intent == "decline":
            answer = AnswerResponse(
                kind="follow_up",
                message="No problem. I’m here whenever you need help with a UAE business permit or setup checklist.",
                items=[],
                gaps=[],
                citations=[],
            )
        elif intent not in {"business_setup", "permit_question"}:
            answer = AnswerResponse(
                kind="gap",
                message="I can’t assist with that request. I’m a business permit assistant and can only "
                "help with UAE business setup, licensing and requirements supported by our reviewed "
                "evidence collection. Would you like help preparing a business setup checklist?",
                items=[],
                gaps=[],
                citations=[],
                offers_setup=True,
            )
        elif profile is None:
            answer = AnswerResponse(
                kind="follow_up",
                message="I’d be happy to help with your business setup. Please answer these five questions "
                "so I can prepare a relevant checklist. Our current pilot covers a new mainland "
                "IT/software company in any of the seven emirates with a provisional LLC structure; other setups are not supported yet.",
                items=[],
                gaps=[],
                citations=[],
                profile_questions=True,
            )
        else:
            evidence_question = (
                "Prepare an evidence-backed business setup checklist for my selected profile and identify missing evidence."
                if accepted_setup
                else question
            )
            answer = self.answer_from_evidence(profile, evidence_question, history)
        return self.conversations.append(profile_id, request.conversation_id, question, answer)

    def answer_from_evidence(self, profile, question, history):
        # Generate licensing guidance only when relevant currently approved evidence exists.
        if not self.knowledge.active_versions(profile.id):
            return AnswerResponse(
                kind="gap",
                message="No approved evidence is available for this profile yet. "
                "Open Knowledge Updates, sync official sources, and review a version first.",
                items=[],
                gaps=["No approved source versions."],
                citations=[],
            )
        # OpenAI embeddings request: app/integrations/openai/client.py -> LanguageModel.embed.
        vector = self.model.embed([question])[0]
        # Atlas hybrid retrieval: app/repositories/knowledge_repository.py -> KnowledgeRepository.retrieve.
        evidence = self.knowledge.retrieve(profile.id, vector, question)
        if not evidence:
            return AnswerResponse(
                kind="gap",
                message="I can’t answer that from the approved evidence currently available.",
                items=[],
                gaps=["The current collection cannot support this answer."],
                citations=[],
            )
        passages = [{"id": row.id, "text": row.text, "locator": row.locator} for row in evidence]
        # LLM generation: app/integrations/openai/client.py -> LanguageModel.answer -> structured.
        generated = self.model.answer(profile, question, passages, history)
        return validate_answer(generated, evidence, self.knowledge)


# Require citations on checklist items, match IDs to retrieved chunks, and recheck cited versions are active.
def validate_answer(generated, evidence, knowledge):
    # Reject unsupported citation IDs and recheck active versions after generation.
    by_id = {row.id: row for row in evidence}
    used = {citation for item in generated.items for citation in item.evidence_ids}
    uncited = sum(not item.evidence_ids for item in generated.items)
    unknown = len(used - by_id.keys())
    if generated.kind == "checklist" and (not generated.items or uncited or unknown):
        reasons = []
        if not generated.items:
            reasons.append("empty_checklist")
        if uncited:
            reasons.append("uncited_items")
        if unknown:
            reasons.append("unknown_evidence_ids")
        logger.warning(
            "event=evidence_validation_failed reasons=%s item_count=%d uncited_item_count=%d "
            "unknown_id_count=%d retrieved_count=%d",
            ",".join(reasons),
            len(generated.items),
            uncited,
            unknown,
            len(evidence),
        )
        raise AppError("The generated checklist failed evidence validation. Please retry.", 502)
    if generated.kind != "checklist" and generated.items:
        logger.warning(
            "event=evidence_validation_failed reasons=inconsistent_kind item_count=%d", len(generated.items)
        )
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
