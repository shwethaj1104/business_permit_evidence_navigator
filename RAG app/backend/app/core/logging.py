import logging
import os
import re
import time
import traceback
from contextlib import contextmanager
from contextvars import ContextVar
from functools import wraps
from pathlib import Path
from uuid import uuid4

from app.core.errors import AppError

_context = ContextVar("log_context", default=None)
logger = logging.getLogger(__name__)


class ContextFilter(logging.Filter):
    """Attach correlation fields without logging request bodies or secrets."""

    def filter(self, record):
        # Fill defaults so startup and dependency logs use the same console format.
        for key in ("request_id", "job_id", "source_id"):
            if not hasattr(record, key):
                setattr(record, key, (_context.get() or {}).get(key, "-"))
        return True


def configure_logging():
    # Add one app-owned console handler and suppress noisy provider HTTP logs.
    root = logging.getLogger()
    if not any(getattr(handler, "permit_console", False) for handler in root.handlers):
        handler = logging.StreamHandler()
        handler.permit_console = True
        handler.addFilter(ContextFilter())
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s %(levelname)s %(name)s request=%(request_id)s job=%(job_id)s "
                "source=%(source_id)s %(message)s"
            )
        )
        root.addHandler(handler)
    root.setLevel(getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper(), logging.INFO))
    for name in ("httpx", "httpcore", "openai", "pymongo"):
        logging.getLogger(name).setLevel(logging.WARNING)


@contextmanager
def log_context(**fields):
    # Scope correlation IDs to one request, job, or source and restore them reliably.
    token = _context.set({**(_context.get() or {}), **fields})
    try:
        yield
    finally:
        _context.reset(token)


def log_failure(stage, exc, **fields):
    # Report safe application hints and stack locations, never raw provider text or local values.
    failures, seen, current = [], set(), exc
    while current is not None and id(current) not in seen:
        seen.add(id(current))
        locations = " > ".join(
            f"{frame.name}:{frame.lineno}@{Path(frame.filename).name}"
            for frame in traceback.extract_tb(current.__traceback__)
        )
        code = getattr(current, "code", None)
        status = getattr(current, "status_code", None)
        safe_code = (
            str(code)
            if isinstance(code, (int, str)) and re.fullmatch(r"[A-Za-z0-9_-]{1,64}", str(code))
            else "-"
        )
        hint = ""
        if isinstance(current, AppError):
            hint = current.message.replace("\n", " ")
            for key in ("OPENAI_API_KEY", "MONGODB_URI"):
                secret = os.getenv(key)
                if secret:
                    hint = hint.replace(secret, "[redacted]")
            hint = re.sub(r"mongodb(?:\+srv)?://\S+", "[connection redacted]", hint)
            hint = hint[:400]
        failures.append(
            f"type={type(current).__name__} code={safe_code} hint={hint!r} "
            f"http_status={status if isinstance(status, int) else '-'} at=[{locations}]"
        )
        current = current.__cause__ or (None if current.__suppress_context__ else current.__context__)
    logger.error("event=failed stage=%s errors=%s", stage, " | caused_by ".join(failures), extra=fields)


def logged_operation(stage):
    # Reuse timed stage logs at service and integration boundaries without changing business logic.
    def decorate(function):
        # Preserve signatures so dependency injection and tests see the original function.
        @wraps(function)
        def wrapped(*args, **kwargs):
            # Log the stage and duration while deliberately excluding arguments and results.
            started = time.perf_counter()
            logger.info("event=started stage=%s", stage)
            try:
                result = function(*args, **kwargs)
            except Exception as exc:
                log_failure(stage, exc)
                raise
            logger.info(
                "event=completed stage=%s duration_ms=%.1f", stage, (time.perf_counter() - started) * 1000
            )
            return result

        return wrapped

    return decorate


class RequestLoggingMiddleware:
    """Trace every HTTP outcome, including validation and uncaught failures."""

    def __init__(self, app):
        # Wrap ASGI directly so context reaches threadpool-based routes.
        self.app = app

    async def __call__(self, scope, receive, send):
        # Correlate requests without recording query strings, bodies, or headers.
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        request_id, started, status = uuid4().hex[:12], time.perf_counter(), 500
        request_path = scope["path"]
        scope.setdefault("state", {})["request_id"] = request_id

        async def capture(message):
            # Expose the same request ID on responses for debugging from browser tools.
            nonlocal status
            if message["type"] == "http.response.start":
                status = message["status"]
                message.setdefault("headers", []).append((b"x-request-id", request_id.encode()))
            await send(message)

        with log_context(request_id=request_id):
            logger.info("event=request_started method=%s", scope["method"])
            try:
                await self.app(scope, receive, capture)
            except Exception as exc:
                log_failure("http.unhandled", exc)
                raise
            finally:
                route = "[unmatched]"
                if scope.get("route") is not None:
                    params = {
                        str(value): "{" + key + "}" for key, value in scope.get("path_params", {}).items()
                    }
                    route = "/".join(params.get(segment, segment) for segment in request_path.split("/"))
                level = logging.ERROR if status >= 500 else logging.WARNING if status >= 400 else logging.INFO
                logger.log(
                    level,
                    "event=request_finished method=%s route=%s status=%s duration_ms=%.1f",
                    scope["method"],
                    route,
                    status,
                    (time.perf_counter() - started) * 1000,
                )
