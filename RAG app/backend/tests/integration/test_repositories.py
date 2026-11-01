from datetime import timedelta

from app.models.domain import PROFILE, SEED_SOURCES, utcnow
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.job_repository import JobRepository
from app.repositories.knowledge_repository import KnowledgeRepository
from app.schemas.api import AnswerResponse


def test_exclusive_jobs_and_lease_recovery(db):
    # Repeated sync requests share a job and only expired leases can be reclaimed.
    db.update_runs.create_index("profile_id", unique=True, partialFilterExpression={"active": True})
    jobs = JobRepository(db)
    first = jobs.create(PROFILE.id, False)
    assert jobs.create(PROFILE.id, False).id == first.id
    assert jobs.claim("worker-a").id == first.id
    assert jobs.claim("worker-b") is None
    db.update_runs.update_one({"id": first.id}, {"$set": {"lease_until": utcnow() - timedelta(seconds=1)}})
    assert jobs.claim("worker-b").id == first.id
    assert not jobs.heartbeat(first.id, "worker-a")
    jobs.finish(first.id, "worker-b", "completed")
    assert jobs.create(PROFILE.id, False).id != first.id


def test_crashed_jobs_eventually_release_scope(db):
    # A repeatedly interrupted job cannot block the profile indefinitely.
    db.update_runs.insert_one(
        {
            "id": "dead",
            "profile_id": PROFILE.id,
            "active": True,
            "attempts": 3,
            "status": "running",
            "lease_until": utcnow() - timedelta(seconds=1),
        }
    )
    assert JobRepository(db).claim("worker") is None
    assert db.update_runs.find_one({"id": "dead"})["active"] is False


def test_pending_versions_are_not_active_evidence(db, settings):
    # Staging and rejected versions never enter the active source set.
    repository = KnowledgeRepository(db, settings)
    repository.seed(PROFILE, SEED_SOURCES)
    source = repository.sources(PROFILE.id)[0]
    db.document_versions.insert_one({"id": "pending", "source_id": source.id, "status": "pending"})
    assert repository.active_versions(PROFILE.id) == []
    db.sources.update_one({"id": source.id}, {"$set": {"active_version_id": "approved"}})
    assert repository.active_versions(PROFILE.id) == ["approved"]


def test_conversation_paginates_without_deleting_older_messages(db):
    # Keep responses bounded while retaining all messages and citation snapshots.
    repository = ConversationRepository(db)
    answer = AnswerResponse(
        kind="gap", message="No evidence", items=[], gaps=["Missing source"], citations=[]
    )
    conversation_id = None
    for _ in range(25):
        conversation = repository.append(PROFILE.id, conversation_id, "Question", answer)
        conversation_id = conversation.id
    assert len(conversation.messages) == 40
    assert conversation.has_older
    assert conversation.messages[-1]["answer"]["gaps"] == ["Missing source"]
    assert db.conversation_messages.count_documents({"conversation_id": conversation.id}) == 50
    earlier = repository.get(conversation.id, before=conversation.oldest_order)
    assert len(earlier.messages) == 10
    assert not earlier.has_older
    assert earlier.messages[0]["order"] == 0


def test_chat_navigation_lists_all_pages_and_preserves_legacy_messages(db):
    # Reopen old embedded chats and paginate beyond the first 20 conversations.
    repository = ConversationRepository(db)
    now = utcnow()
    db.conversations.insert_one(
        {
            "id": "legacy",
            "profile_id": PROFILE.id,
            "created_at": now,
            "messages": [{"role": "user", "text": "Old question", "answer": None}],
        }
    )
    assert repository.get("legacy").messages[0]["text"] == "Old question"
    answer = AnswerResponse(kind="gap", message="No evidence", items=[], gaps=[], citations=[])
    legacy = repository.append(PROFILE.id, "legacy", "New question", answer)
    assert [message["order"] for message in legacy.messages] == [0, 1, 2]
    for index in range(24):
        repository.append(PROFILE.id, None, f"Question {index}", answer)
    first = repository.list(PROFILE.id)
    second = repository.list(PROFILE.id, first["next_cursor"])
    ids = [row["id"] for row in first["conversations"] + second["conversations"]]
    assert len(ids) == len(set(ids)) == 25
    assert second["next_cursor"] is None
