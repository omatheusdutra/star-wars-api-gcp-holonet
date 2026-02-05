import pytest

from holonet.clients import swapi_client


@pytest.mark.parametrize(
    ("path", "resource"),
    [
        ("/films", "films"),
        ("/characters", "people"),
        ("/planets", "planets"),
        ("/starships", "starships"),
        ("/vehicles", "vehicles"),
        ("/species", "species"),
    ],
)
def test_public_endpoints_return_items(client, monkeypatch, path, resource):
    def fake_search(self, resource_name, query, page):
        assert resource_name == resource
        return {
            "count": 1,
            "results": [
                {
                    "name": f"{resource_name}-item",
                    "url": f"https://swapi.dev/api/{resource_name}/1/",
                }
            ],
            "next": None,
            "_cache": {"hit": False, "ttl": 180},
        }

    monkeypatch.setattr(swapi_client.SwapiClient, "search", fake_search)

    resp = client.get(path)
    assert resp.status_code == 200
    payload = resp.json()
    assert payload["items"][0]["name"].endswith("-item")
    assert payload["pagination"]["total_items"] == 1
    assert payload["correlation_id"]


def test_public_aliases_and_reverse_order(client, monkeypatch):
    calls = []

    def fake_search(self, resource_name, query, page):
        calls.append({"resource": resource_name, "query": query, "page": page})
        return {
            "count": 2,
            "results": [
                {"name": "A", "url": "https://swapi.dev/api/planets/1/"},
                {"name": "B", "url": "https://swapi.dev/api/planets/2/"},
            ],
            "next": None,
            "_cache": {"hit": False, "ttl": 180},
        }

    monkeypatch.setattr(swapi_client.SwapiClient, "search", fake_search)

    resp = client.get("/planets?search=tatooine&order_by=name&reverse=true&all=false")
    assert resp.status_code == 200
    payload = resp.json()
    assert calls[0]["query"] == "tatooine"
    assert payload["items"][0]["name"] == "B"


def test_public_rejects_page_size_over_max(client):
    resp = client.get("/planets?page_size=9999")
    assert resp.status_code == 400
