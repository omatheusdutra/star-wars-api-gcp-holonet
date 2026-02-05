from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from holonet.config import settings
from holonet.errors import AppError
from holonet.logging import build_request_logger, get_correlation_id, setup_logging
from holonet.routes import graph, health, planets_map, public, resources, search
from holonet.utils.cache import build_cache


def create_app() -> FastAPI:
    setup_logging()
    app = FastAPI(title="Holonet Galactic Console API", version="1.0.0")

    app.state.cache = build_cache(
        ttl_seconds=settings.cache_ttl_seconds,
        max_entries=settings.cache_max_entries,
        backend=settings.cache_backend,
        redis_url=settings.redis_url,
    )

    @app.middleware("http")
    async def correlation_id_middleware(request: Request, call_next):
        request.state.correlation_id = get_correlation_id(request)
        response = await call_next(request)
        response.headers["x-correlation-id"] = request.state.correlation_id
        return response

    app.add_middleware(BaseHTTPMiddleware, dispatch=build_request_logger())

    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError):
        correlation_id = getattr(request.state, "correlation_id", None)
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "message": exc.message,
                    "status": exc.status_code,
                    "details": exc.details,
                },
                "correlation_id": correlation_id,
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError):
        correlation_id = getattr(request.state, "correlation_id", None)
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "message": "Validation error",
                    "status": 422,
                    "details": exc.errors(),
                },
                "correlation_id": correlation_id,
            },
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        details = exc.detail if isinstance(exc.detail, dict) else {}
        message = exc.detail if isinstance(exc.detail, str) else "HTTP error"
        correlation_id = getattr(request.state, "correlation_id", None)
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {"message": message, "status": exc.status_code, "details": details},
                "correlation_id": correlation_id,
            },
        )

    @app.get("/")
    def root():
        return {"Luke": "I am your father!"}

    app.include_router(public.router)
    app.include_router(health.router)
    app.include_router(search.router, prefix="/v1")
    app.include_router(planets_map.router, prefix="/v1")
    app.include_router(resources.router, prefix="/v1")
    app.include_router(graph.router, prefix="/v1")

    return app


app = create_app()
