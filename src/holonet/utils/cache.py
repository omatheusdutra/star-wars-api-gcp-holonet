import json
import threading
import time
from typing import Any, Protocol


class CacheBackend(Protocol):
    def get(self, key: str) -> Any | None: ...

    def set(self, key: str, value: Any) -> None: ...

    def clear(self) -> None: ...


class TTLCache:
    def __init__(self, ttl_seconds: int, max_entries: int) -> None:
        self._ttl_seconds = ttl_seconds
        self._max_entries = max_entries
        self._lock = threading.Lock()
        self._data: dict[str, tuple[float, Any]] = {}

    def get(self, key: str) -> Any | None:
        now = time.time()
        with self._lock:
            if key not in self._data:
                return None
            expires_at, value = self._data[key]
            if expires_at < now:
                del self._data[key]
                return None
            return value

    def set(self, key: str, value: Any) -> None:
        now = time.time()
        expires_at = now + self._ttl_seconds
        with self._lock:
            if len(self._data) >= self._max_entries:
                oldest_key = min(self._data, key=lambda k: self._data[k][0])
                del self._data[oldest_key]
            self._data[key] = (expires_at, value)

    def clear(self) -> None:
        with self._lock:
            self._data.clear()


class RedisCache:
    def __init__(self, redis_url: str, ttl_seconds: int) -> None:
        try:
            import redis  # type: ignore
        except ImportError as exc:
            raise RuntimeError("redis package not installed") from exc
        self._ttl_seconds = ttl_seconds
        self._client = redis.Redis.from_url(redis_url, decode_responses=True)

    def get(self, key: str) -> Any | None:
        raw = self._client.get(key)
        if raw is None:
            return None
        return json.loads(raw)

    def set(self, key: str, value: Any) -> None:
        payload = json.dumps(value)
        self._client.setex(key, self._ttl_seconds, payload)

    def clear(self) -> None:
        self._client.flushdb()


def build_cache(
    ttl_seconds: int, max_entries: int, backend: str, redis_url: str | None
) -> CacheBackend:
    if backend == "redis":
        if not redis_url:
            raise RuntimeError("REDIS_URL is required for redis cache backend")
        return RedisCache(redis_url, ttl_seconds)
    return TTLCache(ttl_seconds, max_entries)
