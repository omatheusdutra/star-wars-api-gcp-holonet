import logging
import random
import time
from typing import Any

import httpx

from holonet.config import settings
from holonet.errors import AppError
from holonet.logging import log_json
from holonet.utils.cache import CacheBackend


class SwapiClient:
    def __init__(
        self, cache: CacheBackend | None = None, correlation_id: str | None = None
    ) -> None:
        self._cache = cache
        self._correlation_id = correlation_id
        self._client = httpx.Client(timeout=settings.http_timeout_seconds)

    def get_resource(self, resource: str, resource_id: int) -> dict[str, Any]:
        url = f"{settings.swapi_base_url.rstrip('/')}/{resource}/{resource_id}/"
        return self._request(url)

    def get_by_url(self, url: str) -> dict[str, Any]:
        return self._request(url)

    def search(self, resource: str, query: str | None, page: int) -> dict[str, Any]:
        base = f"{settings.swapi_base_url.rstrip('/')}/{resource}/"
        params: dict[str, Any] = {"page": page}
        if query:
            params["search"] = query
        return self._request(base, params=params)

    def _request(self, url: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        cache_key = None
        if self._cache is not None:
            cache_key = f"{url}?{params}" if params else url
            cached = self._cache.get(cache_key)
            if cached is not None:
                cached["_cache"] = {"hit": True, "ttl": settings.cache_ttl_seconds}
                log_json(
                    "swapi_cache_hit",
                    url=url,
                    correlation_id=self._correlation_id or "unknown",
                )
                return cached

        last_exc: Exception | None = None
        for attempt in range(settings.http_retries + 1):
            started = time.time()
            try:
                response = self._client.get(url, params=params)
            except httpx.RequestError as exc:
                logging.getLogger().exception("swapi_request_failed")
                last_exc = exc
            else:
                if response.status_code == 404:
                    raise AppError("Resource not found", status_code=404)
                if response.status_code >= 400:
                    raise AppError(
                        "SWAPI error", status_code=502, details={"status": response.status_code}
                    )
                payload = response.json()
                payload["_cache"] = {"hit": False, "ttl": settings.cache_ttl_seconds}
                if self._cache is not None and cache_key is not None:
                    self._cache.set(cache_key, payload)
                elapsed_ms = int((time.time() - started) * 1000)
                log_json(
                    "swapi_request",
                    url=url,
                    status=response.status_code,
                    elapsed_ms=elapsed_ms,
                    correlation_id=self._correlation_id or "unknown",
                )
                return payload

            if attempt < settings.http_retries:
                base = settings.http_backoff_factor * (2**attempt)
                jitter = random.uniform(0, 0.1)  # nosec B311 - non-cryptographic jitter
                time.sleep(base + jitter)

        raise AppError(
            "SWAPI unavailable",
            status_code=502,
            details={"error": str(last_exc) if last_exc else "unknown"},
        )
