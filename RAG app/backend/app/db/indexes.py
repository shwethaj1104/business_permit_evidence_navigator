from pymongo.operations import SearchIndexModel


def setup_indexes(db, settings):
    # Provision query and Atlas search indexes explicitly through a setup command.
    for name in (
        "business_profiles",
        "sources",
        "document_versions",
        "chunks",
        "update_runs",
        "conversations",
        "conversation_messages",
    ):
        db[name].create_index("id", unique=True)
    db.sources.create_index([("profile_id", 1), ("url", 1)], unique=True)
    db.document_versions.create_index([("source_id", 1), ("fetched_at", -1)])
    db.chunks.create_index([("version_id", 1), ("ordinal", 1)], unique=True)
    db.chunks.create_index([("content_hash", 1), ("embedding_model", 1)])
    db.update_runs.create_index("profile_id", unique=True, partialFilterExpression={"active": True})
    db.update_runs.create_index([("status", 1), ("lease_until", 1)])
    db.change_records.create_index("version_id", unique=True)
    db.conversations.create_index([("profile_id", 1), ("created_at", -1), ("id", -1)])
    db.conversation_messages.create_index([("conversation_id", 1), ("order", 1)], unique=True)
    existing = {index["name"] for index in db.chunks.list_search_indexes()}
    if settings.vector_index not in existing:
        db.chunks.create_search_index(
            SearchIndexModel(
                name=settings.vector_index,
                type="vectorSearch",
                definition={
                    "fields": [
                        {
                            "type": "vector",
                            "path": "embedding",
                            "numDimensions": settings.embedding_dimensions,
                            "similarity": "cosine",
                        },
                        {"type": "filter", "path": "profile_id"},
                        {"type": "filter", "path": "version_id"},
                        {"type": "filter", "path": "embedding_model"},
                    ]
                },
            )
        )
    if settings.keyword_index not in existing:
        db.chunks.create_search_index(
            SearchIndexModel(
                name=settings.keyword_index,
                definition={
                    "mappings": {
                        "dynamic": False,
                        "fields": {
                            "text": {"type": "string"},
                            "profile_id": {"type": "token"},
                            "version_id": {"type": "token"},
                        },
                    }
                },
            )
        )
