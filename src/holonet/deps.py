from fastapi import Header, HTTPException, Request

from holonet.clients.swapi_client import SwapiClient


def require_api_key(
    x_api_key: str | None = Header(default=None), api_key: str | None = None
) -> None:
    from holonet.config import settings

    if not settings.require_api_key:
        return None
    key = x_api_key or api_key
    if not key or key != settings.api_key:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return None


def correlation_id_dependency(request: Request) -> str:
    return request.state.correlation_id


def get_swapi_client(request: Request) -> SwapiClient:
    cache = request.app.state.cache
    correlation_id = getattr(request.state, "correlation_id", None)
    return SwapiClient(cache, correlation_id=correlation_id)
