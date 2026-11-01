from fastapi import APIRouter

from app.api.routes import chat, knowledge, profiles

router = APIRouter(prefix="/api/v1")
router.include_router(profiles.router)
router.include_router(chat.router)
router.include_router(knowledge.router)
