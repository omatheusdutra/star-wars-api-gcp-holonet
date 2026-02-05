from holonet.clients import swapi_client
from holonet.config import settings
from holonet.errors import AppError


def test_search_endpoint(client, monkeypatch):
    def fake_search(self, resource, query, page):
        return {
            "count": 1,
            "results": [{"name": "Tatooine", "url": "https://swapi.dev/api/planets/1/"}],
            "next": None,
            "_cache": {"hit": False, "ttl": 180},
        }

    monkeypatch.setattr(swapi_client.SwapiClient, "search", fake_search)

    resp = client.get("/v1/search?resource=planets&q=tat&page=1&page_size=10")
    assert resp.status_code == 200
    payload = resp.json()
    assert payload["items"][0]["name"] == "Tatooine"
    assert payload["correlation_id"]


def test_search_aliases_and_reverse(client, monkeypatch):
    def fake_search(self, resource, query, page):
        return {
            "count": 2,
            "results": [
                {"name": "A", "url": "https://swapi.dev/api/people/1/"},
                {"name": "B", "url": "https://swapi.dev/api/people/2/"},
            ],
            "next": None,
            "_cache": {"hit": False, "ttl": 180},
        }

    monkeypatch.setattr(swapi_client.SwapiClient, "search", fake_search)

    resp = client.get("/v1/search?resource=people&search=luke&order_by=name&reverse=true")
    assert resp.status_code == 200
    payload = resp.json()
    assert payload["items"][0]["name"] == "B"


def test_search_rejects_page_size_over_max(client):
    too_large = settings.max_page_size + 1
    resp = client.get(f"/v1/search?resource=people&page_size={too_large}")
    assert resp.status_code == 400
    payload = resp.json()
    assert payload["error"]["message"] == "page_size exceeds maximum"


def test_get_film(client, monkeypatch):
    def fake_get(self, resource, resource_id):
        return {
            "title": "A New Hope",
            "url": "https://swapi.dev/api/films/1/",
            "_cache": {"hit": True},
        }

    monkeypatch.setattr(swapi_client.SwapiClient, "get_resource", fake_get)

    resp = client.get("/v1/films/1")
    assert resp.status_code == 200
    payload = resp.json()
    assert payload["item"]["title"] == "A New Hope"


def test_graph_endpoint(client, monkeypatch):
    def fake_get(self, resource, resource_id):
        if resource == "people":
            return {"name": "Luke", "films": ["https://swapi.dev/api/films/1/"]}
        return {"title": "A New Hope", "characters": []}

    monkeypatch.setattr(swapi_client.SwapiClient, "get_resource", fake_get)

    resp = client.get("/v1/graph?start_resource=people&start_id=1&depth=1")
    assert resp.status_code == 200
    payload = resp.json()
    assert payload["graph"]["nodes"]


def test_planets_map_endpoint(client, monkeypatch):
    def fake_search(self, resource, query, page):
        return {
            "results": [
                {
                    "name": "Tatooine",
                    "population": "200000",
                    "terrain": "desert",
                    "climate": "arid",
                    "url": "https://swapi.dev/api/planets/1/",
                }
            ],
            "next": None,
        }

    monkeypatch.setattr(swapi_client.SwapiClient, "search", fake_search)

    resp = client.get("/v1/planets/map?page_size=1")
    assert resp.status_code == 200
    payload = resp.json()
    assert payload["items"][0]["name"] == "Tatooine"


def test_expand_urls_handles_error(client, monkeypatch):
    def fake_get(self, resource, resource_id):
        return {"title": "A New Hope", "characters": ["https://swapi.dev/api/people/1/"]}

    def fake_by_url(self, url):
        raise AppError("SWAPI unavailable", status_code=502)

    monkeypatch.setattr(swapi_client.SwapiClient, "get_resource", fake_get)
    monkeypatch.setattr(swapi_client.SwapiClient, "get_by_url", fake_by_url)

    resp = client.get("/v1/films/1/characters")
    assert resp.status_code == 200
    payload = resp.json()
    assert payload["items"] == []


def test_people_films_expanded(client, monkeypatch):
    def fake_get(self, resource, resource_id):
        return {"name": "Luke", "films": ["https://swapi.dev/api/films/1/"]}

    def fake_by_url(self, url):
        return {"title": "A New Hope", "url": url, "_cache": {"hit": False}}

    monkeypatch.setattr(swapi_client.SwapiClient, "get_resource", fake_get)
    monkeypatch.setattr(swapi_client.SwapiClient, "get_by_url", fake_by_url)

    resp = client.get("/v1/people/1/films")
    assert resp.status_code == 200
    payload = resp.json()
    assert payload["items"][0]["title"] == "A New Hope"


def test_people_planets_starships_endpoints(client, monkeypatch):
    def fake_get(self, resource, resource_id):
        return {
            "name": f"{resource}-{resource_id}",
            "url": f"https://swapi.dev/api/{resource}/{resource_id}/",
            "_cache": {"hit": False},
        }

    monkeypatch.setattr(swapi_client.SwapiClient, "get_resource", fake_get)

    resp = client.get("/v1/people/1")
    assert resp.status_code == 200
    assert resp.json()["item"]["name"] == "people-1"

    resp = client.get("/v1/planets/2")
    assert resp.status_code == 200
    assert resp.json()["item"]["name"] == "planets-2"

    resp = client.get("/v1/starships/3")
    assert resp.status_code == 200
    assert resp.json()["item"]["name"] == "starships-3"


def test_film_characters_expanded_success(client, monkeypatch):
    def fake_get(self, resource, resource_id):
        return {"title": "A New Hope", "characters": ["https://swapi.dev/api/people/1/"]}

    def fake_by_url(self, url):
        return {"name": "Luke", "url": url, "_cache": {"hit": False}}

    monkeypatch.setattr(swapi_client.SwapiClient, "get_resource", fake_get)
    monkeypatch.setattr(swapi_client.SwapiClient, "get_by_url", fake_by_url)

    resp = client.get("/v1/films/1/characters")
    assert resp.status_code == 200
    payload = resp.json()
    assert payload["items"][0]["name"] == "Luke"
