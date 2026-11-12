import argparse
import logging
import signal
import threading
from uuid import uuid4

from pymongo.errors import ConnectionFailure, OperationFailure, PyMongoError

from app.api.dependencies import build_services
from app.core.config import get_settings
from app.core.errors import AppError
from app.core.logging import configure_logging, log_context, log_failure, logged_operation
from app.db.client import database_connection

logger = logging.getLogger(__name__)


def renew_lease(jobs, job_id, owner, done, lost):
    # Renew only this job's lease while network/model calls are in progress.
    while not done.wait(20):
        try:
            if not jobs.heartbeat(job_id, owner):
                logger.error("event=lease_lost job_id=%s", job_id)
                lost.set()
                return
        except PyMongoError as exc:
            log_failure("worker.heartbeat", exc, job_id=job_id)
            lost.set()
            return


def claim_next_job(jobs, owner):
    # Retry temporary disconnections on the next poll and distinguish permanent queue errors.
    try:
        return jobs.claim(owner)
    except ConnectionFailure as exc:
        logger.warning("Queue connection interrupted (%s); retrying in 5 seconds.", type(exc).__name__)
        return None
    except OperationFailure as exc:
        log_failure("worker.claim", exc)
        hint = (
            "Check the database user's readWrite permission."
            if exc.code in (13, 18)
            else "Check the queue indexes and Atlas service status."
        )
        raise AppError(f"MongoDB queue operation failed (code {exc.code}). {hint}", 503) from exc


@logged_operation("worker.run")
def run(job_id=None, once=False):
    # Process only manually queued jobs; this loop never schedules source discovery.
    settings = get_settings()
    configure_logging()
    logger.info("event=worker_startup")
    stop = threading.Event()
    signal.signal(signal.SIGINT, lambda *_: stop.set())
    signal.signal(signal.SIGTERM, lambda *_: stop.set())
    with database_connection(settings) as db:
        services = build_services(db)
        owner = str(uuid4())
        logger.info("event=worker_ready mode=%s", "one-shot" if job_id or once else "local-polling")
        exit_code = 0
        try:
            while not stop.is_set():
                job = services.jobs.claim(owner, job_id) if job_id else claim_next_job(services.jobs, owner)
                if not job:
                    if job_id or once:
                        logger.info("event=worker_no_claimable_job job_id=%s", job_id)
                        break
                    stop.wait(5)
                    continue
                logger.info("event=job_claimed job_id=%s attempt=%s", job.id, job.attempts)
                done, lost = threading.Event(), threading.Event()

                thread = threading.Thread(
                    target=renew_lease, args=(services.jobs, job.id, owner, done, lost), daemon=True
                )
                thread.start()
                try:
                    with log_context(job_id=job.id):
                        # Ingestion workflow: app/services/ingestion/sync_service.py -> SyncService.process -> ingest.
                        services.sync.process(job, owner, lambda lost=lost: not lost.is_set())
                except Exception as exc:  # noqa: BLE001 - a failed job must not terminate the worker
                    exit_code = 1
                    log_failure("worker.process_job", exc, job_id=job.id)
                    if not lost.is_set():
                        services.jobs.finish(
                            job.id, owner, "failed", "Sync failed; check worker logs and retry manually."
                        )
                finally:
                    done.set()
                    thread.join(timeout=1)
                if job_id or once:
                    result = services.jobs.get(job.id)
                    if lost.is_set() or (result and result.status == "failed"):
                        exit_code = 1
                    break
        finally:
            services.model.close()
            logger.info("event=worker_shutdown")

    return exit_code


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process manual sync jobs.")
    parser.add_argument("--job-id", help="Process only this MongoDB job, then exit.")
    parser.add_argument("--once", action="store_true", help="Process at most one queued job, then exit.")
    arguments = parser.parse_args()
    raise SystemExit(run(arguments.job_id, arguments.once))
