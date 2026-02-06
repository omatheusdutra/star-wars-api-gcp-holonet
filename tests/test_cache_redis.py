import pytest

from holonet.utils.cache import RedisCache


def test_redis_cache_serialize(monkeypatch):
    class FakeRedis:
        def __init__(self):
            self.store = {}

        def get(self, key):
            return self.store.get(key)

        def setex(self, key, ttl, value):
            self.store[key] = value

        def flushdb(self):
            self.store.clear()

    import redis

    fake = FakeRedis()
    monkeypatch.setattr(redis.Redis, "from_url", lambda *args, **kwargs: fake)

    cache = RedisCache(redis_url="redis://localhost:6379/0", ttl_seconds=60)
    cache.set("k", {"v": 1})
    assert cache.get("k") == {"v": 1}
    cache.clear()
    assert cache.get("k") is None


def test_redis_cache_missing_package(monkeypatch):
    import builtins

    original_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "redis":
            raise ImportError("no")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    import json  # exercise non-redis import path

    with pytest.raises(RuntimeError):
        RedisCache(redis_url="redis://localhost:6379/0", ttl_seconds=60)
