from typing import Literal

from pydantic import Field, create_model

from app.models.domain import ChecklistItem, GeneratedAnswer


def evidence_answer_schema(evidence_ids):
    # Constrain each response to this retrieval's IDs and keep answer kinds structurally consistent.
    allowed = tuple(sorted(set(evidence_ids)))
    if not allowed:
        raise ValueError("Grounded generation requires retrieved evidence IDs.")
    citation = Literal[allowed]
    item = create_model(
        "CitedChecklistItem",
        __base__=ChecklistItem,
        evidence_ids=(list[citation], Field(min_length=1)),
    )
    checklist = create_model(
        "CitedChecklist",
        __base__=GeneratedAnswer,
        kind=(Literal["checklist"], ...),
        items=(list[item], Field(min_length=1)),
    )
    no_checklist = create_model(
        "EvidenceLimitation",
        __base__=GeneratedAnswer,
        kind=(Literal["follow_up", "gap"], ...),
        items=(list[item], Field(max_length=0)),
    )
    # Keep the union nested: Structured Outputs requires an object at the schema root.
    return create_model("EvidenceAnswer", answer=(checklist | no_checklist, ...))
