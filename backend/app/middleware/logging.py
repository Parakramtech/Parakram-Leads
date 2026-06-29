import time
import uuid
import contextvars
from typing import Callable

import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

# Context variables for request-scoped data
request_id_var: contextvars.ContextVar[str] = contextvars.ContextVar("request_id", default="-")
user_id_var: contextvars.ContextVar[str] = contextvars.ContextVar("user_id", default="-")
org_id_var: contextvars.ContextVar[str] = contextvars.ContextVar("org_id", default="-")


def _extract_user_id_from_auth(header_value: str) -> str:
    """Extract user_id (sub claim) from a Bearer JWT token."""
    if not header_value or not header_value.startswith("Bearer "):
        return "-"
    token = header_value[7:]
    try:
        import json
        import base64
        # Decode JWT payload without verification (just for logging context)
        parts = token.split(".")
        if len(parts) != 3:
            return "-"
        payload = parts[1]
        # Add padding
        padding = 4 - len(payload) % 4
        if padding != 4:
            payload += "=" * padding
        decoded = base64.urlsafe_b64decode(payload)
        data = json.loads(decoded)
        return str(data.get("sub", "-"))
    except Exception:
        return "-"


class StructuredLoggingMiddleware(BaseHTTPMiddleware):
    """FastAPI middleware that adds structured JSON logging via structlog."""

    def __init__(self, app, logger=None):
        super().__init__(app)
        self.logger = logger or structlog.get_logger("sigma.requests")

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        req_id = str(uuid.uuid4())
        request_id_var.set(req_id)

        # Extract user_id from Authorization header if present
        auth_header = request.headers.get("authorization", "")
        uid = _extract_user_id_from_auth(auth_header)
        user_id_var.set(uid)

        client_ip = request.client.host if request.client else "-"
        method = request.method
        path = request.url.path

        # Bind request context to structlog
        structlog.contextvars.bind_contextvars(
            request_id=req_id,
            user_id=uid,
            org_id=org_id_var.get(),
        )

        self.logger.info(
            "request.start",
            method=method,
            path=path,
            client_ip=client_ip,
        )

        start = time.perf_counter()
        try:
            response: Response = await call_next(request)
        except Exception:
            duration_ms = round((time.perf_counter() - start) * 1000, 2)
            self.logger.error(
                "request.error",
                method=method,
                path=path,
                duration_ms=duration_ms,
                exc_info=True,
            )
            raise
        duration_ms = round((time.perf_counter() - start) * 1000, 2)

        self.logger.info(
            "request.end",
            method=method,
            path=path,
            status_code=response.status_code,
            duration_ms=duration_ms,
        )

        response.headers["X-Request-ID"] = req_id
        return response


def configure_structlog(log_level: str = "INFO", log_format: str = "json"):
    """Configure structlog for the application. Call once at startup."""
    import logging

    # Map string log level to numeric value for structlog's filtering writer
    level_map = {
        "CRITICAL": logging.CRITICAL,
        "ERROR": logging.ERROR,
        "WARNING": logging.WARNING,
        "INFO": logging.INFO,
        "DEBUG": logging.DEBUG,
        "NOTSET": logging.NOTSET,
    }
    min_level = level_map.get(log_level.upper(), logging.INFO)

    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
    ]
    if log_format == "json":
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(min_level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )
