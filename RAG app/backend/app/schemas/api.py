from typing import Literal

from pydantic import BaseModel, Field

from app.models.domain import ChecklistItem, Profile


class ChatRequest(BaseModel):
    """Validate a question and optional anonymous conversation reference."""

    profile_id: str | None = None
    message: str = Field(min_length=1, max_length=4000)
    conversation_id: str | None = Field(default=None, max_length=64)


class SyncRequest(BaseModel):
    """Start a manual sync, optionally discovering additional official sources."""

    profile_id: str
    discover: bool = False


class ReviewRequest(BaseModel):
    """Record a deliberate publication or rejection decision."""

    action: Literal["approve", "reject"]


class Citation(BaseModel):
    """Expose provenance without relying on model-generated URLs."""

    id: str
    source_id: str
    version_id: str
    title: str
    url: str
    locator: str
    excerpt: str
    fetched_at: str
    last_checked_at: str | None
    source_published_at: str | None
    source_updated_at: str | None
    newer_version_available: bool = False


class AnswerResponse(BaseModel):
    """Return the validated answer with server-resolved citations."""

    kind: Literal["checklist", "follow_up", "gap"]
    message: str
    items: list[ChecklistItem]
    gaps: list[str]
    citations: list[Citation]
    profile_questions: bool = False
    offers_setup: bool = False


class MessageResponse(BaseModel):
    """Keep user messages distinct from structured assistant answers."""

    id: str
    order: int
    role: Literal["user", "assistant"]
    text: str
    answer: AnswerResponse | None = None


class ConversationResponse(BaseModel):
    """Return bounded conversation history for one selected profile."""

    id: str
    profile_id: str | None
    messages: list[MessageResponse]
    has_older: bool = False
    oldest_order: int | None = None


class ConversationSummary(BaseModel):
    """Expose chat navigation without loading message bodies."""

    id: str
    profile_id: str | None
    title: str
    preview: str
    created_at: str
    updated_at: str


class ConversationPage(BaseModel):
    """Return a stable cursor for older saved conversations."""

    conversations: list[ConversationSummary]
    next_cursor: str | None


class ProfileResponse(BaseModel):
    """Share one authoritative profile definition between both tabs."""

    profiles: list[Profile]


class SyncResponse(BaseModel):
    """Return durable job state and bounded per-source outcomes."""

    id: str
    profile_id: str
    status: str
    discover: bool
    created_at: str
    attempts: int
    outcomes: list[dict]
    error: str | None = None


class SourceResponse(BaseModel):
    """Show source freshness and active evidence references."""

    id: str
    title: str
    url: str
    profile_id: str
    active_version_id: str | None = None
    latest_version_id: str | None = None
    latest_version_status: str | None = None
    registered_at: str | None = None
    last_capture_at: str | None = None
    last_capture_status: str | None = None
    last_capture_error: str | None = None
    last_checked_at: str | None = None
    last_successful_fetch_at: str | None = None


class VersionSummary(BaseModel):
    """Expose review content and version dates without embedding vectors."""

    id: str
    source_id: str
    title: str
    url: str
    profile_id: str
    status: str
    summary: str
    previous_version_id: str | None
    fetched_at: str
    change_detected_at: str
    source_published_at: str | None
    source_updated_at: str | None
    effective_from: str | None
    reviewed_at: str | None = None
    activated_at: str | None = None


class VersionResponse(VersionSummary):
    """Load full source text only when a user opens a particular version."""

    section_changes: list[dict] = Field(default_factory=list)
    diff: str
    text: str


class RenameConversationRequest(BaseModel):
    """Validate a concise user-defined saved chat title."""

    title: str = Field(min_length=1, max_length=80)
