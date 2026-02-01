import json
import logging
import sys
import time
import uuid
from collections.abc import Callable
from typing import Any

from fastapi import Request, Response

from holonet.config import settings


def setup_logging() -> None:
    logging.basicConfig(
        level=settings.log_level,
        format="%(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def get_correlation_id(request: Request) -> str:
    cid = request.headers.get("x-correlation-id")
    if cid:
        return cid
    return str(uuid.uuid4())


def log_json(event: str, **fields: Any) -> None:
    payload = {"event": event}
    payload.update(fields)
    logging.getLogger().info(json.dumps(payload))


def build_request_logger() -> Callable[[Request, Callable[[Request], Response]], Response]:
    async def _logger(request: Request, call_next):
        start = time.time()
        correlation_id = getattr(request.state, "correlation_id", None)
        if not correlation_id:
            correlation_id = get_correlation_id(request)
            request.state.correlation_id = correlation_id
        response = await call_next(request)
        elapsed_ms = int((time.time() - start) * 1000)
        log_json(
            "request_completed",
            path=request.url.path,
            method=request.method,
            status=response.status_code,
            correlation_id=correlation_id,
            elapsed_ms=elapsed_ms,
        )
        return response

    return _logger
