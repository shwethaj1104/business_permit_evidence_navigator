from hashlib import sha256

from app.core.logging import logged_operation
from app.models.domain import PROFILE, Record, utcnow


class KnowledgeRepository:
    """Own source/version persistence and Atlas retrieval queries."""

    def __init__(self, db, settings):
        # Retain persistence and search configuration at one boundary.
        self.db, self.settings = db, settings

    def seed(self, profile, sources):
        # Register sources without fetching anything or overwriting review state.
        self.db.business_profiles.update_one({"id": profile.id}, {"$set": profile.model_dump()}, upsert=True)
        for source in sources:
            # Scope shared federal URLs to each profile, preserving existing Dubai evidence IDs.
            source_key = source["url"] if profile.id == PROFILE.id else f"{profile.id}:{source['url']}"
            source_id = sha256(source_key.encode()).hexdigest()[:24]
            self.db.sources.update_one(
                {"id": source_id},
                {
                    "$setOnInsert": {
                        "id": source_id,
                        "profile_id": profile.id,
                        "active_version_id": None,
                        "latest_version_id": None,
                        **source,
                        "registered_at": utcnow(),
                    }
                },
                upsert=True,
            )

    def sources(self, profile_id):
        # Distinguish registered links, failed captures, and reviewable document versions.
        sources = list(self.db.sources.find({"profile_id": profile_id}, {"_id": 0}))
        ids = [source["latest_version_id"] for source in sources if source.get("latest_version_id")]
        versions = {
            row["id"]: row["status"]
            for row in self.db.document_versions.find({"id": {"$in": ids}}, {"_id": 0, "id": 1, "status": 1})
        }
        previous_results = {}
        for job in (
            self.db.update_runs.find({"profile_id": profile_id}, {"outcomes": 1})
            .sort("created_at", -1)
            .limit(20)
        ):
            for outcome in job.get("outcomes", []):
                previous_results.setdefault(outcome.get("url"), outcome)
        records = []
        for source in sources:
            result = previous_results.get(source["url"], {})
            source.setdefault("last_capture_status", result.get("status"))
            source.setdefault(
                "last_capture_error", result.get("summary") if result.get("status") == "failed" else None
            )
            source["latest_version_status"] = versions.get(source.get("latest_version_id"))
            records.append(Record.model_validate(source))
        return records

    def capture_result(self, source_id, outcome):
        # Persist capture outcomes so a registered URL is never mistaken for reviewable evidence.
        self.db.sources.update_one(
            {"id": source_id},
            {
                "$set": {
                    "last_capture_status": outcome["status"],
                    "last_capture_at": utcnow(),
                    "last_capture_error": outcome.get("summary") if outcome["status"] == "failed" else None,
                }
            },
        )

    def version(self, version_id):
        # Fetch an exact immutable content version for review or citation.
        row = self.db.document_versions.find_one({"id": version_id}, {"_id": 0})
        return Record.model_validate(row) if row else None

    def versions(self, profile_id):
        # List bounded version history without leaking large vectors or originals.
        rows = (
            self.db.document_versions.find(
                {"profile_id": profile_id},
                {"_id": 0, "text": 0, "diff": 0, "sections": 0, "section_changes": 0},
            )
            .sort("fetched_at", -1)
            .limit(100)
        )
        return [Record.model_validate(row) for row in rows]

    def checked(self, source_id, success=False):
        # Separate successful freshness from a failed check attempt.
        fields = {"last_checked_at": utcnow()}
        if success:
            fields["last_successful_fetch_at"] = fields["last_checked_at"]
        self.db.sources.update_one({"id": source_id}, {"$set": fields})

    @logged_operation("database.stage_version")
    def save_version(self, version):
        # Persist staging data idempotently before exposing it for review.
        self.db.document_versions.update_one({"id": version["id"]}, {"$setOnInsert": version}, upsert=True)
        self.db.change_records.update_one(
            {"version_id": version["id"]},
            {
                "$setOnInsert": {
                    "version_id": version["id"],
                    "source_id": version["source_id"],
                    "summary": version["summary"],
                    "diff": version["diff"],
                    "detected_at": version["change_detected_at"],
                }
            },
            upsert=True,
        )
        self.db.sources.update_one(
            {"id": version["source_id"]}, {"$set": {"latest_version_id": version["id"]}}
        )
        self.db.document_versions.update_many(
            {"source_id": version["source_id"], "id": {"$ne": version["id"]}, "status": "pending"},
            {"$set": {"status": "superseded"}},
        )

    @logged_operation("database.checkpoint_embeddings")
    def save_chunks(self, chunks):
        # Retain paid embedding work across summary failures without activating any evidence.
        for chunk in chunks:
            self.db.chunks.update_one({"id": chunk["id"]}, {"$setOnInsert": chunk}, upsert=True)

    def embeddings_for(self, hashes):
        # Reuse unchanged passages only when the embedding model and dimensions match.
        rows = self.db.chunks.find(
            {"content_hash": {"$in": hashes}, "embedding_model": self.settings.embedding_model},
            {"content_hash": 1, "embedding": 1},
        )
        return {
            row["content_hash"]: row["embedding"]
            for row in rows
            if len(row["embedding"]) == self.settings.embedding_dimensions
        }

    @logged_operation("database.search_readiness")
    def index_ready(self, version_id):
        # Require indexed keyword rows and usable vector results before publication.
        expected = self.db.chunks.count_documents({"version_id": version_id})
        if not expected:
            return False
        count = list(
            self.db.chunks.aggregate(
                [
                    {
                        "$searchMeta": {
                            "index": self.settings.keyword_index,
                            "equals": {"path": "version_id", "value": version_id},
                            "count": {"type": "total"},
                        }
                    }
                ]
            )
        )
        sample = self.db.chunks.find_one({"version_id": version_id})
        vector = list(
            self.db.chunks.aggregate(
                [
                    {
                        "$vectorSearch": {
                            "index": self.settings.vector_index,
                            "path": "embedding",
                            "queryVector": sample["embedding"],
                            "filter": {"version_id": version_id},
                            "exact": True,
                            "limit": expected,
                        }
                    },
                    {"$count": "total"},
                ]
            )
        )
        return bool(
            count
            and vector
            and count[0].get("count", {}).get("total", 0) == expected
            and vector[0]["total"] == expected
        )

    @logged_operation("database.publish_version")
    def review(self, version, action):
        # Commit review state and the active pointer together to prevent partial publication.
        def commit(session):
            # Reject stale or competing reviews within the same transaction snapshot.
            current = self.db.document_versions.find_one(
                {"id": version.id, "status": "pending"}, session=session
            )
            source = self.db.sources.find_one(
                {"id": version.source_id, "latest_version_id": version.id}, session=session
            )
            if not current or not source:
                return False
            now = utcnow()
            if action == "approve":
                self.db.sources.update_one(
                    {"id": version.source_id}, {"$set": {"active_version_id": version.id}}, session=session
                )
            self.db.document_versions.update_one(
                {"id": version.id},
                {
                    "$set": {
                        "status": "approved" if action == "approve" else "rejected",
                        "reviewed_at": now,
                        "activated_at": now if action == "approve" else None,
                    }
                },
                session=session,
            )
            self.db.change_records.update_one(
                {"version_id": version.id},
                {"$set": {"decision": action, "reviewed_at": now}},
                session=session,
            )
            return True

        with self.db.client.start_session() as session:
            return session.with_transaction(commit)

    def active_versions(self, profile_id):
        # Source pointers are authoritative even if search indexes lag writes.
        return [
            row["active_version_id"]
            for row in self.db.sources.find(
                {"profile_id": profile_id, "active_version_id": {"$ne": None}}, {"active_version_id": 1}
            )
        ]

    @logged_operation("database.hybrid_retrieval")
    def retrieve(self, profile_id, vector, question):
        # Fuse lexical and semantic ranks only within active profile versions.
        active = self.active_versions(profile_id)
        if not active:
            return []
        semantic = list(
            self.db.chunks.aggregate(
                [
                    {
                        "$vectorSearch": {
                            "index": self.settings.vector_index,
                            "path": "embedding",
                            "queryVector": vector,
                            "numCandidates": 100,
                            "limit": 12,
                            "filter": {
                                "profile_id": profile_id,
                                "version_id": {"$in": active},
                                "embedding_model": self.settings.embedding_model,
                            },
                        }
                    },
                    {"$project": {"_id": 0, "embedding": 0}},
                ]
            )
        )
        lexical = list(
            self.db.chunks.aggregate(
                [
                    {
                        "$search": {
                            "index": self.settings.keyword_index,
                            "compound": {
                                "must": [{"text": {"query": question, "path": "text"}}],
                                "filter": [
                                    {"equals": {"path": "profile_id", "value": profile_id}},
                                    {"in": {"path": "version_id", "value": active}},
                                ],
                            },
                        }
                    },
                    {"$limit": 12},
                    {"$project": {"_id": 0, "embedding": 0}},
                ]
            )
        )
        scores, rows = {}, {}
        for results in (semantic, lexical):
            for rank, row in enumerate(results):
                rows[row["id"]] = row
                scores[row["id"]] = scores.get(row["id"], 0) + 1 / (60 + rank + 1)
        current = set(self.active_versions(profile_id))
        return [
            Record.model_validate(rows[key])
            for key in sorted(scores, key=scores.get, reverse=True)
            if rows[key]["version_id"] in current
        ][:8]
