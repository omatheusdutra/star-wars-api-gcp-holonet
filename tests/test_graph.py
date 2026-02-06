from holonet.services.graph_service import GraphService


class FakeClient:
    def get_resource(self, resource, resource_id):
        if resource == "people":
            return {
                "name": "Luke",
                "films": ["https://swapi.dev/api/films/1/"],
                "homeworld": "https://swapi.dev/api/planets/1/",
                "url": "https://swapi.dev/api/people/1/",
            }
        if resource == "films":
            return {
                "title": "A New Hope",
                "characters": ["https://swapi.dev/api/people/1/"],
                "planets": ["https://swapi.dev/api/planets/1/"],
                "url": "https://swapi.dev/api/films/1/",
            }
        if resource == "planets":
            return {
                "name": "Tatooine",
                "residents": ["https://swapi.dev/api/people/1/"],
                "films": ["https://swapi.dev/api/films/1/"],
                "url": "https://swapi.dev/api/planets/1/",
            }
        return {"name": "unknown", "url": f"https://swapi.dev/api/{resource}/{resource_id}/"}


def test_build_graph():
    service = GraphService(FakeClient())
    graph = service.build_graph("people", 1, depth=2)

    assert graph["nodes"]
    assert graph["edges"]
    node_ids = {node["id"] for node in graph["nodes"]}
    assert "people:1" in node_ids
    assert "films:1" in node_ids
    assert "planets:1" in node_ids
    unknown = FakeClient().get_resource("starships", 9)
    assert unknown["url"].endswith("/starships/9/")


def test_build_graph_invalid_url():
    class BadClient:
        def get_resource(self, resource, resource_id):
            return {"name": "X", "films": ["bad-url"]}

    service = GraphService(BadClient())
    graph = service.build_graph("people", 1, depth=1)
    assert graph["nodes"]


def test_graph_parse_non_int():
    class ClientNonInt:
        def get_resource(self, resource, resource_id):
            return {"name": "X", "films": ["https://swapi.dev/api/films/abc/"]}

    service = GraphService(ClientNonInt())
    graph = service.build_graph("people", 1, depth=1)
    assert graph["nodes"]


def test_graph_skips_visited_nodes():
    class DupClient:
        def get_resource(self, resource, resource_id):
            if resource == "people":
                return {
                    "name": "Luke",
                    "films": [
                        "https://swapi.dev/api/films/1/",
                        "https://swapi.dev/api/films/1/",
                    ],
                    "url": "https://swapi.dev/api/people/1/",
                }
            if resource == "films":
                return {"title": "A New Hope", "url": "https://swapi.dev/api/films/1/"}
            return {"name": "unknown", "url": f"https://swapi.dev/api/{resource}/{resource_id}/"}

    service = GraphService(DupClient())
    graph = service.build_graph("people", 1, depth=2)
    film_nodes = [node for node in graph["nodes"] if node["id"] == "films:1"]
    assert len(film_nodes) == 1
    unknown = DupClient().get_resource("species", 3)
    assert unknown["url"].endswith("/species/3/")
