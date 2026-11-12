import difflib
import hashlib
import logging

from app.core.errors import AppError
from app.core.logging import log_context, log_failure, logged_operation
from app.integrations.official_sources.extractor import chunk_sections, content_hash, extract, section_history
from app.integrations.official_sources.fetcher import validate_url
from app.models.domain import sources_for_profile, utcnow

logger = logging.getLogger(__name__)


class SyncService:
    """Coordinate manual source refresh, immutable versions, and explicit publication."""

    def __init__(self, profiles, knowledge, jobs, files, model, fetcher, discovery, dispatcher=None):
        # Share business logic between HTTP requests and the independent worker.
        self.profiles, self.knowledge, self.jobs = profiles, knowledge, jobs
        self.files, self.model, self.fetcher, self.discovery = files, model, fetcher, discovery
        self.dispatcher = dispatcher

    @logged_operation("sync.enqueue")
    def start(self, request):
        # Register pilot URLs and enqueue work without fetching on the API thread.
        profile = self.profiles.require(request.profile_id)
        if not self.model.settings.openai_key:
            raise AppError("Set OPENAI_API_KEY before syncing: new documents need embeddings.", 503)
        self.knowledge.seed(profile, sources_for_profile(profile))
        job = self.jobs.create(profile.id, request.discover)
        logger.info("event=job_enqueued job_id=%s discover=%s", job.id, request.discover)
        if self.dispatcher and self.jobs.reserve_dispatch(job.id):
            try:
                # Azure launch: app/integrations/azure_jobs.py -> AzureJobDispatcher.start; runs app/workers/sync_worker.py.
                self.dispatcher.start(job.id)
            except Exception as exc:
                log_failure("sync.dispatch", exc, job_id=job.id)
                self.jobs.dispatch_failed(job.id)
                raise AppError(
                    "Sync was saved, but the Azure worker could not start. Click Sync to retry.", 503
                ) from exc
        return self.jobs.get(job.id)

    @logged_operation("sync.list_jobs")
    def list_jobs(self, profile_id):
        # Resume durable job visibility after the UI reloads.
        self.profiles.require(profile_id)
        return self.jobs.list(profile_id)

    @logged_operation("sync.job_status")
    def get_job(self, job_id):
        # Return safe progress for one known job.
        job = self.jobs.get(job_id)
        if not job:
            raise AppError("Sync job not found.", 404)
        return job

    @logged_operation("sources.list")
    def list_sources(self, profile_id):
        # Show source freshness without triggering a website request.
        self.profiles.require(profile_id)
        return self.knowledge.sources(profile_id)

    @logged_operation("versions.list")
    def list_versions(self, profile_id):
        # Expose immutable version history for comparisons and review.
        self.profiles.require(profile_id)
        return self.knowledge.versions(profile_id)

    @logged_operation("versions.detail")
    def get_version(self, version_id):
        # Load full text only for a requested comparison or historical citation.
        version = self.knowledge.version(version_id)
        if not version:
            raise AppError("Source version not found.", 404)
        return version

    @logged_operation("versions.review")
    def review(self, version_id, action):
        # Publish only the latest complete version with searchable evidence.
        version = self.knowledge.version(version_id)
        if not version:
            raise AppError("Source version not found.", 404)
        if version.status != "pending":
            raise AppError("This version has already been reviewed.", 409)
        if action == "approve" and not self.knowledge.index_ready(version.id):
            raise AppError(
                "Search indexes are still building or missing evidence. Retry after Atlas finishes indexing.",
                409,
            )
        if not self.knowledge.review(version, action):
            raise AppError("A newer version exists. Review the latest version instead.", 409)
        return self.knowledge.version(version_id)

    @logged_operation("sync.process")
    def process(self, job, owner, lease_alive):
        # Resume source-level checkpoints and keep partial failures visible.
        profile = self.profiles.require(job.profile_id)
        outcomes = list(job.outcomes)
        if job.discover and not any(row.get("url") == "discovery" for row in outcomes):
            try:
                discovered = []
                # Web-search tool request: app/integrations/official_sources/discovery.py -> OfficialDiscovery.discover.
                for row in self.discovery.discover(profile):
                    try:
                        validate_url(row["url"], resolve=False)
                        discovered.append(row)
                    except AppError:
                        continue
                self.knowledge.seed(profile, discovered)
                outcomes.append(
                    {
                        "url": "discovery",
                        "status": "discovered",
                        "summary": f"Registered {len(discovered)} official URLs.",
                    }
                )
            except AppError as exc:
                log_failure("sync.discovery", exc)
                outcomes.append({"url": "discovery", "status": "failed", "summary": exc.message})
            self.jobs.progress(job.id, owner, outcomes)
        completed = {row["url"] for row in outcomes}
        for source in self.knowledge.sources(profile.id):
            if not lease_alive() or not self.jobs.heartbeat(job.id, owner):
                raise AppError("Worker lease was lost; job will be recovered.", 409)
            if source.url in completed:
                continue
            try:
                with log_context(source_id=source.id):
                    outcome = self.ingest(source, lease_alive)
            except AppError as exc:
                outcome = {"url": source.url, "status": "failed", "summary": exc.message}
            self.knowledge.capture_result(source.id, outcome)
            logger.info("event=source_result source_id=%s status=%s", source.id, outcome["status"])
            outcomes.append(outcome)
            if not self.jobs.progress(job.id, owner, outcomes):
                raise AppError("Worker lease was lost; job will be recovered.", 409)
        failures = sum(row["status"] == "failed" for row in outcomes)
        status = "completed" if not failures else "partial" if failures < len(outcomes) else "failed"
        self.jobs.finish(job.id, owner, status)
        logger.info("event=job_finished status=%s sources=%s failures=%s", status, len(outcomes), failures)

    @logged_operation("source.ingest")
    def ingest(self, source, lease_alive):
        # Skip unchanged text and stage changed evidence before review.
        self.knowledge.checked(source.id)
        # Website download: app/integrations/official_sources/fetcher.py -> SourceFetcher.fetch (no LLM).
        raw, content_type, final_url = self.fetcher.fetch(source.url)
        fetched_at = utcnow()
        document = extract(raw, content_type)
        fingerprint = content_hash(document)
        previous = self.knowledge.version(source.latest_version_id) if source.latest_version_id else None
        self.knowledge.checked(source.id, success=True)
        if previous and previous.content_hash == fingerprint:
            logger.info("event=source_unchanged embeddings_skipped=true summary_skipped=true")
            return {
                "url": source.url,
                "status": "unchanged",
                "summary": "No content or explicit source-date changes detected.",
            }
        version_id = hashlib.sha256(
            f"{source.id}:{fingerprint}:{source.latest_version_id}".encode()
        ).hexdigest()[:32]
        chunks = chunk_sections(document.sections)
        reused = self.knowledge.embeddings_for([chunk["content_hash"] for chunk in chunks])
        missing = [chunk for chunk in chunks if chunk["content_hash"] not in reused]
        if missing:
            # Embeddings request: app/integrations/openai/client.py -> LanguageModel.embed.
            vectors = self.model.embed([chunk["text"] for chunk in missing])
            reused.update(
                {chunk["content_hash"]: vector for chunk, vector in zip(missing, vectors, strict=True)}
            )
        embeddings = [reused[chunk["content_hash"]] for chunk in chunks]
        logger.info(
            "event=chunks_prepared total=%s embedded=%s reused=%s",
            len(chunks),
            len(missing),
            len(chunks) - len(missing),
        )
        records = [
            {
                **chunk,
                "id": f"{version_id}:{chunk['ordinal']}",
                "version_id": version_id,
                "source_id": source.id,
                "profile_id": source.profile_id,
                "embedding_model": self.model.settings.embedding_model,
                "embedding": vector,
            }
            for chunk, vector in zip(chunks, embeddings, strict=True)
        ]
        if not lease_alive():
            raise AppError("Worker lease lost before embedding checkpoint.", 409)
        self.knowledge.save_chunks(records)
        diff = "\n".join(
            difflib.unified_diff(
                (previous.text if previous else "").splitlines(),
                document.text.splitlines(),
                fromfile="Previous",
                tofile="Fetched",
                lineterm="",
            )
        )
        # Summary LLM request: app/integrations/openai/client.py -> LanguageModel.summarize -> structured.
        summary = self.model.summarize(diff or "Only explicit source date metadata changed.")
        if not lease_alive():
            raise AppError("Worker lease lost before publication staging.", 409)
        file_id = self.files.save(version_id, raw, content_type)
        sections, changes = section_history(
            document.sections, getattr(previous, "sections", []) if previous else [], fetched_at
        )
        version = {
            "sections": sections,
            "section_changes": changes,
            "id": version_id,
            "source_id": source.id,
            "profile_id": source.profile_id,
            "title": document.title,
            "url": final_url,
            "content_hash": fingerprint,
            "file_id": file_id,
            "text": document.text,
            "diff": diff[:200000],
            "summary": summary,
            "status": "pending",
            "previous_version_id": previous.id if previous else None,
            "fetched_at": fetched_at,
            "change_detected_at": fetched_at,
            "source_published_at": document.published,
            "source_updated_at": document.updated,
            "effective_from": None,
            "reviewed_at": None,
            "activated_at": None,
        }
        self.knowledge.save_version(version)
        return {
            "url": source.url,
            "status": "modified" if previous else "new",
            "summary": summary,
            "version_id": version_id,
        }
