from unittest.mock import Mock

import mongomock
import pytest
from mongomock.gridfs import enable_gridfs_integration

from app.core.config import Settings


@pytest.fixture
def settings():
    # Keep tests isolated from real credentials and paid providers.
    return Settings(
        "", "test", "", "gpt-4.1-nano", "text-embedding-3-small", "gpt-4.1-mini", embedding_dimensions=3
    )


@pytest.fixture
def db():
    # Exercise repository state transitions against an in-memory test double only.
    enable_gridfs_integration()
    return mongomock.MongoClient(tz_aware=True).test


@pytest.fixture
def model(settings):
    # Replace generation/embeddings so tests never spend tokens.
    result = Mock()
    result.settings = settings
    result.embed.side_effect = lambda texts: [[1.0, 0.0, 0.0] for _ in texts]
    result.classify_intent.return_value = "permit_question"
    result.summarize.return_value = "A new official source was captured for review."
    return result
