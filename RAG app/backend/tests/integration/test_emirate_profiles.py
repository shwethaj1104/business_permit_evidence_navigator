from hashlib import sha256

from app.models.domain import PROFILE, PROFILES, SEED_SOURCES, sources_for_profile
from app.repositories.knowledge_repository import KnowledgeRepository
from app.services.profile_service import ProfileService


def test_all_seven_profiles_have_two_official_references():
    # Expose every emirate with the same explicitly limited business scope.
    service = ProfileService()
    assert {p.emirate for p in service.list()} == {
        "Dubai",
        "Abu Dhabi",
        "Sharjah",
        "Ajman",
        "Umm Al Quwain",
        "Ras Al Khaimah",
        "Fujairah",
    }
    for profile in service.list():
        assert service.require(profile.id) == profile
        assert len(sources_for_profile(profile)) == 2


def test_seeding_is_idempotent_and_isolates_shared_guidance(db, settings):
    # Shared URLs must never share approval state across emirates or reset Dubai evidence.
    repository = KnowledgeRepository(db, settings)
    for profile in PROFILES:
        repository.seed(profile, sources_for_profile(profile))
    dubai_id = sha256(SEED_SOURCES[0]["url"].encode()).hexdigest()[:24]
    db.sources.update_one({"id": dubai_id}, {"$set": {"active_version_id": "approved-dubai"}})
    for profile in PROFILES:
        repository.seed(profile, sources_for_profile(profile))
        rows = repository.sources(profile.id)
        assert len(rows) == 2
        if profile.id != PROFILE.id:
            assert all(row.active_version_id is None for row in rows)
    assert db.sources.count_documents({}) == 14
    assert db.business_profiles.count_documents({}) == 7
    assert db.sources.find_one({"id": dubai_id})["active_version_id"] == "approved-dubai"
