from unittest.mock import Mock

from app.models.domain import PROFILE, SEED_SOURCES
from app.repositories.knowledge_repository import KnowledgeRepository
from app.services.ingestion.sync_service import SyncService
from app.services.profile_service import ProfileService


def test_sync_preserves_versions_and_skips_unchanged_embeddings(db, settings, model):
    # A second identical fetch updates freshness without another paid model call.
    repository = KnowledgeRepository(db, settings)
    repository.seed(PROFILE, SEED_SOURCES[:1])
    fetcher, files = Mock(), Mock()
    fetcher.fetch.return_value = (
        b"<main>" + b"<p>Official preparation guidance.</p>" * 30 + b"</main>",
        "text/html",
        SEED_SOURCES[0]["url"],
    )
    files.save.return_value = "file"
    service = SyncService(ProfileService(), repository, Mock(), files, model, fetcher, Mock())
    first = service.ingest(repository.sources(PROFILE.id)[0], lambda: True)
    assert first["status"] == "new"
    version = repository.version(first["version_id"])
    assert version.source_published_at is None
    assert version.status == "pending"
    assert repository.active_versions(PROFILE.id) == []
    calls = model.embed.call_count
    again = service.ingest(repository.sources(PROFILE.id)[0], lambda: True)
    assert again["status"] == "unchanged"
    assert model.embed.call_count == calls
    fetcher.fetch.return_value = (
        b"<main>" + b"<p>Official preparation guidance.</p>" * 30 + b"<p>Additional document.</p></main>",
        "text/html",
        SEED_SOURCES[0]["url"],
    )
    changed = service.ingest(repository.sources(PROFILE.id)[0], lambda: True)
    assert changed["status"] == "modified"
    assert db.document_versions.count_documents({}) == 2
    assert repository.version(changed["version_id"]).previous_version_id == first["version_id"]


def test_failed_fetch_does_not_advance_successful_freshness(db, settings, model):
    # Preserve the last success date when a later network check fails.
    import pytest

    from app.core.errors import AppError

    repository = KnowledgeRepository(db, settings)
    repository.seed(PROFILE, SEED_SOURCES[:1])
    fetcher = Mock()
    fetcher.fetch.side_effect = AppError("Source unreachable", 502)
    service = SyncService(ProfileService(), repository, Mock(), Mock(), model, fetcher, Mock())
    with pytest.raises(AppError):
        service.ingest(repository.sources(PROFILE.id)[0], lambda: True)
    source = repository.sources(PROFILE.id)[0]
    assert source.last_checked_at is not None
    assert not hasattr(source, "last_successful_fetch_at")
    model.embed.assert_not_called()


def test_summary_failure_keeps_embedding_work_without_publishing(db, settings, model):
    # A generation failure must not force another embedding bill for identical text on retry.
    import pytest

    from app.core.errors import AppError

    repository = KnowledgeRepository(db, settings)
    repository.seed(PROFILE, SEED_SOURCES[:1])
    fetcher, files = Mock(), Mock()
    fetcher.fetch.return_value = (
        b"<main>" + b"<p>Official preparation guidance.</p>" * 30 + b"</main>",
        "text/html",
        SEED_SOURCES[0]["url"],
    )
    model.summarize.side_effect = AppError("Model unavailable", 502)
    service = SyncService(ProfileService(), repository, Mock(), files, model, fetcher, Mock())
    with pytest.raises(AppError):
        service.ingest(repository.sources(PROFILE.id)[0], lambda: True)
    assert db.chunks.count_documents({}) > 0
    assert repository.active_versions(PROFILE.id) == []
    assert db.document_versions.count_documents({}) == 0
    calls = model.embed.call_count
    model.summarize.side_effect = None
    files.save.return_value = "test-file"
    service.ingest(repository.sources(PROFILE.id)[0], lambda: True)
    assert model.embed.call_count == calls
    assert repository.active_versions(PROFILE.id) == []
