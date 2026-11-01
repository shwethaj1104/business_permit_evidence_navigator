import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pymongo.errors import PyMongoError
from starlette.concurrency import run_in_threadpool

from app.api.dependencies import build_services
from app.api.router import router
from app.core.config import get_settings
from app.core.errors import AppError
from app.core.logging import RequestLoggingMiddleware, configure_logging, log_failure
from app.db.client import database_connection

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app):
    # Keep the setup UI usable when credentials are missing or Atlas is unreachable.
    settings = get_settings()
    configure_logging()
    logger.info("event=api_startup")
    app.state.services, app.state.database_error = None, None
    connection = database_connection(settings)
    try:
        db = await run_in_threadpool(connection.__enter__)
    except AppError as exc:
        app.state.database_error = exc.message
        log_failure("api.database_startup", exc)
    else:
        app.state.services = build_services(db)
        logger.info("event=api_ready database_connected=true openai_configured=%s", bool(settings.openai_key))
    try:
        yield
    finally:
        logger.info("event=api_shutdown")
        if app.state.services:
            app.state.services.model.close()
            await run_in_threadpool(connection.__exit__, None, None, None)


def create_app():
    # Compose HTTP routing and centralized safe error translation.
    app = FastAPI(title="Business Permit Evidence Navigator", version="0.1.0", lifespan=lifespan)
    app.include_router(router)
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(get_settings().cors_origins),
        allow_methods=["GET", "POST", "PATCH", "DELETE"],
        allow_headers=["Content-Type", "Authorization"],
        expose_headers=["X-Request-ID"],
    )

    @app.exception_handler(AppError)
    async def application_error(request: Request, exc: AppError):
        # Return actionable domain errors without exposing provider internals.
        log_failure("http.application", exc)
        return JSONResponse(status_code=exc.status, content={"detail": exc.message})

    @app.exception_handler(PyMongoError)
    async def database_error(request: Request, exc: PyMongoError):
        # Translate persistence failures into a safe setup/retry message.
        log_failure("http.database", exc)
        return JSONResponse(
            status_code=503,
            content={
                "detail": "MongoDB operation failed. Check connectivity and run the database setup command."
            },
        )

    @app.exception_handler(Exception)
    async def unexpected_error(request: Request, exc: Exception):
        # Hide internal error details while preserving a diagnostic server log.
        log_failure("http.unexpected", exc, request_id=getattr(request.state, "request_id", "-"))
        return JSONResponse(
            status_code=500,
            content={"detail": "An unexpected error occurred. Check backend logs."},
            headers={"X-Request-ID": getattr(request.state, "request_id", "-")},
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error(request: Request, exc: RequestValidationError):
        # Identify invalid field locations without logging submitted values.
        logger.warning("event=validation_failed fields=%s", [str(error["loc"]) for error in exc.errors()])
        return await request_validation_exception_handler(request, exc)

    @app.get("/api/v1/health", tags=["system"])
    def health():
        # Report configuration readiness without revealing any secret values.
        settings = get_settings()
        return {
            "status": "ready" if app.state.services and settings.openai_key else "setup_required",
            "database_ready": app.state.services is not None,
            "openai_configured": bool(settings.openai_key),
            "message": app.state.database_error,
            "model": settings.model,
            "embedding_model": settings.embedding_model,
        }

    return app


app = create_app()
