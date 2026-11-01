from contextlib import contextmanager

from pymongo import MongoClient
from pymongo.errors import PyMongoError

from app.core.errors import AppError


@contextmanager
def database_connection(settings):
    # Create one Mongo client per process lifecycle, never at import time.
    if not settings.mongodb_uri:
        raise AppError("Set MONGODB_URI in the root .env, then restart the backend.", 503)
    client = MongoClient(settings.mongodb_uri, serverSelectionTimeoutMS=5000, tz_aware=True)
    try:
        try:
            client.admin.command("ping")
        except PyMongoError as exc:
            raise AppError(
                "MongoDB connection failed. Check Atlas credentials and network access.", 503
            ) from exc
        yield client[settings.database]
    finally:
        client.close()
