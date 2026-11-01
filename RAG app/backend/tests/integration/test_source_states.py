from app.models.domain import PROFILE, SEED_SOURCES, utcnow
from app.repositories.knowledge_repository import KnowledgeRepository


def test_failed_registered_source_has_no_reviewable_version(db, settings):
    # Reconstruct failures from old job outcomes without inventing pending versions.
    repository = KnowledgeRepository(db, settings)
    repository.seed(PROFILE, SEED_SOURCES[:1])
    db.update_runs.insert_one(
        {
            "id": "job",
            "profile_id": PROFILE.id,
            "created_at": utcnow(),
            "outcomes": [{"url": SEED_SOURCES[0]["url"], "status": "failed", "summary": "Extraction failed"}],
        }
    )
    source = repository.sources(PROFILE.id)[0]
    assert source.last_capture_status == "failed"
    assert source.last_capture_error == "Extraction failed"
    assert source.latest_version_status is None
    assert source.latest_version_id is None


def test_pending_version_and_capture_recovery_are_exposed(db, settings):
    # A successful retry clears its earlier capture error and exposes the version awaiting review.
    repository = KnowledgeRepository(db, settings)
    repository.seed(PROFILE, SEED_SOURCES[:1])
    source = repository.sources(PROFILE.id)[0]
    repository.capture_result(source.id, {"status": "failed", "summary": "Extraction failed"})
    db.document_versions.insert_one({"id": "pending", "status": "pending"})
    db.sources.update_one({"id": source.id}, {"$set": {"latest_version_id": "pending"}})
    repository.capture_result(source.id, {"status": "new"})
    source = repository.sources(PROFILE.id)[0]
    assert source.last_capture_error is None
    assert source.latest_version_status == "pending"
