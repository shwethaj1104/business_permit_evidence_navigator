from datetime import timedelta
from uuid import uuid4

from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError

from app.core.errors import AppError
from app.models.domain import Record, utcnow


class JobRepository:
    """Persist manually requested jobs with recoverable exclusive leases."""

    def __init__(self, db):
        # Keep queue operations separate from ingestion business rules.
        self.jobs = db.update_runs

    def create(self, profile_id, discover):
        # Reuse an active job if repeated clicks race each other.
        if not any(
            index.get("unique") and index.get("partialFilterExpression") == {"active": True}
            for index in self.jobs.list_indexes()
        ):
            raise AppError(
                "Initialize Atlas indexes first: run python -m scripts.setup_db from backend.", 503
            )
        job = {
            "id": str(uuid4()),
            "profile_id": profile_id,
            "discover": discover,
            "status": "queued",
            "active": True,
            "created_at": utcnow(),
            "attempts": 0,
            "outcomes": [],
            "error": None,
        }
        try:
            self.jobs.insert_one(job)
        except DuplicateKeyError:
            job = self.jobs.find_one({"profile_id": profile_id, "active": True})
        return Record.model_validate(job)

    def list(self, profile_id):
        # Return recent jobs so the UI can resume polling after a reload.
        return [
            Record.model_validate(row)
            for row in self.jobs.find({"profile_id": profile_id}).sort("created_at", -1).limit(20)
        ]

    def get(self, job_id):
        # Fetch one durable job for progress polling.
        row = self.jobs.find_one({"id": job_id})
        return Record.model_validate(row) if row else None

    def claim(self, owner, job_id=None):
        # Recover expired jobs while bounding crash/restart attempts.
        now = utcnow()
        self.jobs.update_many(
            {"active": True, "attempts": {"$gte": 3}, "lease_until": {"$lt": now}},
            {"$set": {"status": "failed", "active": False, "error": "Worker retry limit reached."}},
        )
        row = self.jobs.find_one_and_update(
            {
                **({"id": job_id} if job_id else {}),
                "active": True,
                "attempts": {"$lt": 3},
                "$or": [{"status": "queued"}, {"status": "running", "lease_until": {"$lt": now}}],
            },
            {
                "$set": {"status": "running", "owner": owner, "lease_until": now + timedelta(minutes=3)},
                "$inc": {"attempts": 1},
            },
            return_document=ReturnDocument.AFTER,
        )
        return Record.model_validate(row) if row else None

    def reserve_dispatch(self, job_id):
        # Suppress racing launch requests while allowing manual recovery after a lost response.
        now = utcnow()
        result = self.jobs.update_one(
            {
                "id": job_id,
                "active": True,
                "$and": [
                    {"$or": [{"status": "queued"}, {"status": "running", "lease_until": {"$lt": now}}]},
                    {"$or": [{"dispatch_until": {"$exists": False}}, {"dispatch_until": {"$lt": now}}]},
                ],
            },
            {"$set": {"dispatch_until": now + timedelta(minutes=2), "error": None}},
        )
        return bool(result.modified_count)

    def dispatch_failed(self, job_id):
        # Retain queued work for an explicit retry without overwriting a running worker.
        self.jobs.update_one(
            {"id": job_id, "status": "queued"},
            {
                "$unset": {"dispatch_until": ""},
                "$set": {"error": "Worker launch failed. Click Sync to retry."},
            },
        )

    def heartbeat(self, job_id, owner):
        # Extend only a lease still owned by this worker.
        result = self.jobs.update_one(
            {"id": job_id, "owner": owner, "active": True},
            {"$set": {"lease_until": utcnow() + timedelta(minutes=3)}},
        )
        return bool(result.matched_count)

    def progress(self, job_id, owner, outcomes):
        # Persist source checkpoints only while this worker retains ownership.
        result = self.jobs.update_one(
            {"id": job_id, "owner": owner, "active": True}, {"$set": {"outcomes": outcomes}}
        )
        return bool(result.matched_count)

    def finish(self, job_id, owner, status, error=None):
        # Release scope exclusivity when processing reaches a terminal state.
        self.jobs.update_one(
            {"id": job_id, "owner": owner},
            {"$set": {"status": status, "active": False, "error": error, "finished_at": utcnow()}},
        )
