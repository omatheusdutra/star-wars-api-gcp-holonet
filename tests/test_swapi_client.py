import httpx
import pytest

from holonet.clients.swapi_client import SwapiClient
from holonet.errors import AppError
from holonet.utils.cache import TTLCache


def _response(status_code=200, json_body=None):
    request = httpx.Request("GET", "https://swapi.dev/api")
    return httpx.Response(status_code, json=json_body or {}, request=request)


def test_swapi_client_cache_hit():
    cache = TTLCache(ttl_seconds=60, max_entries=10)
    client = SwapiClient(cache)

    def fake_get(url, params=None):
        return _response(200, {"name": "Luke", "url": url})

    client._client.get = fake_get  # type: ignore

    first = client.get_resource("people", 1)
    second = client.get_resource("people", 1)

    assert first["name"] == "Luke"
    assert second["_cache"]["hit"] is True


def test_swapi_client_404():
    client = SwapiClient()

    def fake_get(url, params=None):
        return _response(404, {"detail": "Not found"})

    client._client.get = fake_get  # type: ignore

    with pytest.raises(AppError) as exc:
        client.get_resource("people", 999)
    assert exc.value.status_code == 404


def test_swapi_client_500():
    client = SwapiClient()

    def fake_get(url, params=None):
        return _response(500, {"detail": "err"})

    client._client.get = fake_get  # type: ignore

    with pytest.raises(AppError) as exc:
        client.get_resource("people", 2)
    assert exc.value.status_code == 502


def test_swapi_client_request_exception(monkeypatch):
    client = SwapiClient()

    def boom(*_args, **_kwargs):
        raise httpx.RequestError("fail")

    monkeypatch.setattr(client._client, "get", boom)

    with pytest.raises(AppError) as exc:
        client.get_resource("people", 3)
    assert exc.value.status_code == 502


def test_swapi_client_get_by_url_and_search():
    client = SwapiClient()

    def fake_get(url, params=None):
        if url.endswith("/people/10/"):
            return _response(200, {"name": "Obi", "url": url})
        return _response(200, {"count": 0, "results": [], "next": None})

    client._client.get = fake_get  # type: ignore

    data = client.get_by_url("https://swapi.dev/api/people/10/")
    assert data["name"] == "Obi"
    payload = client.search("people", "obi", 1)
    assert payload["count"] == 0
