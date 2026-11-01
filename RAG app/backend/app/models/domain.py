from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, model_validator


class Profile(BaseModel):
    """Describe one supported development scope, not a verified licensing classification."""

    id: str
    emirate: str
    jurisdiction: str
    activity: str
    application_type: str
    legal_structure: str
    coverage_note: str


PROFILE = Profile(
    id="dubai-mainland-software-new-llc",
    emirate="Dubai",
    jurisdiction="Mainland",
    activity="IT / Software development",
    application_type="New application",
    legal_structure="LLC (provisional)",
    coverage_note="Pilot scope. Exact activity code and activity-specific requirements need official verification.",
)
ALLOWED_DOMAINS = ("investindubai.gov.ae", "u.ae")
SEED_SOURCES = [
    {
        "url": "https://www.investindubai.gov.ae/business-setup/business-set-up-steps",
        "title": "Dubai business setup steps",
    },
    {
        "url": "https://u.ae/en/information-and-services/business/doing-business/doing-business-on-the-mainland",
        "title": "UAE mainland business setup overview",
    },
]


class ChecklistItem(BaseModel):
    """Bind a proposed requirement to exact retrieved evidence IDs."""

    title: str
    detail: str
    condition: str
    evidence_ids: list[str]


class GeneratedAnswer(BaseModel):
    """Constrain model output before it becomes an application answer."""

    kind: Literal["checklist", "follow_up", "gap"]
    message: str
    items: list[ChecklistItem]
    gaps: list[str]


class GeneratedSummary(BaseModel):
    """Require a short factual summary of observed source differences."""

    summary: str


class Record(BaseModel):
    """Represent internal Mongo records without exposing persistence IDs."""

    model_config = ConfigDict(extra="allow")
    id: str

    @model_validator(mode="before")
    @classmethod
    def strip_storage_id(cls, data):
        # Keep BSON ObjectIds out of domain serialization and public response mapping.
        return {key: value for key, value in data.items() if key != "_id"}


@dataclass
class ExtractedDocument:
    """Preserve source text and explicit dates separately from fetch time."""

    title: str
    text: str
    sections: list[dict]
    published: str | None = None
    updated: str | None = None


def utcnow() -> datetime:
    # Use timezone-aware timestamps for all application events.
    return datetime.now(UTC)
