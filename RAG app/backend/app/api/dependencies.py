from dataclasses import dataclass

from fastapi import Request

from app.controllers.chat_controller import ChatController
from app.controllers.knowledge_controller import KnowledgeController
from app.core.config import get_settings
from app.core.errors import AppError
from app.db.files import SourceFiles
from app.integrations.azure_jobs import build_dispatcher
from app.integrations.official_sources.discovery import OfficialDiscovery
from app.integrations.official_sources.fetcher import SourceFetcher
from app.integrations.openai.client import LanguageModel
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.job_repository import JobRepository
from app.repositories.knowledge_repository import KnowledgeRepository
from app.services.ingestion.sync_service import SyncService
from app.services.profile_service import ProfileService
from app.services.retrieval.chat_service import ChatService


@dataclass
class Services:
    """Hold process-scoped dependencies shared by HTTP and worker entry points."""

    profiles: ProfileService
    jobs: JobRepository
    chat: ChatService
    sync: SyncService
    model: LanguageModel


def build_services(db):
    # Compose concrete adapters once without coupling services to FastAPI.
    settings = get_settings()
    profiles, model = ProfileService(), LanguageModel(settings)
    knowledge, jobs = KnowledgeRepository(db, settings), JobRepository(db)
    chat = ChatService(profiles, knowledge, ConversationRepository(db), model)
    sync = SyncService(
        profiles,
        knowledge,
        jobs,
        SourceFiles(db),
        model,
        SourceFetcher(),
        OfficialDiscovery(model),
        build_dispatcher(settings),
    )
    return Services(profiles, jobs, chat, sync, model)


def require_services(request: Request):
    # Fail database-dependent requests clearly while the setup UI remains available.
    services = request.app.state.services
    if services is None:
        raise AppError(request.app.state.database_error or "Database is not configured.", 503)
    return services


def chat_controller(request: Request):
    # Inject the chat controller without exposing ingestion operations.
    return ChatController(require_services(request).chat)


def knowledge_controller(request: Request):
    # Inject the knowledge controller for manual sync and review endpoints.
    return KnowledgeController(require_services(request).sync)
