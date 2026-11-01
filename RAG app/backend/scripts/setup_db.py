from app.core.config import get_settings
from app.core.logging import configure_logging, logged_operation
from app.db.client import database_connection
from app.db.indexes import setup_indexes
from app.models.domain import PROFILE, SEED_SOURCES
from app.repositories.knowledge_repository import KnowledgeRepository


@logged_operation("database.setup")
def main():
    # Provision one Atlas database and register sources without fetching or model calls.
    settings = get_settings()
    with database_connection(settings) as db:
        setup_indexes(db, settings)
        KnowledgeRepository(db, settings).seed(PROFILE, SEED_SOURCES)
    print("Database initialized. Wait for Atlas search indexes to become READY before approving evidence.")


if __name__ == "__main__":
    configure_logging()
    main()
