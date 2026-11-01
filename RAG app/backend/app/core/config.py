import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[3]


@dataclass(frozen=True)
class Settings:
    """Keep backend configuration independent of the working directory."""

    mongodb_uri: str
    database: str
    openai_key: str
    model: str
    embedding_model: str
    discovery_model: str
    embedding_dimensions: int = 1536
    vector_index: str = "permit_vectors"
    keyword_index: str = "permit_keywords"
    sync_dispatch_mode: str = "local"
    azure_sync_job_resource_id: str = ""
    azure_client_id: str = ""
    cors_origins: tuple[str, ...] = ()


@lru_cache
def get_settings() -> Settings:
    # Load local secrets only inside backend processes.
    load_dotenv(ROOT / ".env")
    MODEL = os.getenv("OPENAI_MODEL", "gpt-5-nano")
    return Settings(
        mongodb_uri=os.getenv("MONGODB_URI", ""),
        database=os.getenv("MONGODB_DB_NAME", "permit_navigator"),
        openai_key=os.getenv("OPENAI_API_KEY", ""),
        model=MODEL,
        embedding_model=os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"),
        discovery_model=os.getenv("OPENAI_SEARCH_MODEL", "gpt-5-nano"),
        sync_dispatch_mode=os.getenv("SYNC_DISPATCH_MODE", "local"),
        azure_sync_job_resource_id=os.getenv("AZURE_SYNC_JOB_RESOURCE_ID", ""),
        azure_client_id=os.getenv("AZURE_CLIENT_ID", ""),
        cors_origins=tuple(
            origin.strip() for origin in os.getenv("CORS_ORIGINS", "").split(",") if origin.strip()
        ),
    )
