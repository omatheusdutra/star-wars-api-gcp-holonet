from holonet.services.planets_map_service import PlanetsMapService


class FakeClient:
    def search(self, resource, query, page):
        if page == 1:
            return {
                "results": [
                    {
                        "name": "Tatooine",
                        "population": "200000",
                        "terrain": "desert",
                        "climate": "arid",
                        "url": "https://swapi.dev/api/planets/1/",
                        "diameter": "10465",
                        "gravity": "1 standard",
                        "orbital_period": "304",
                        "rotation_period": "23",
                    },
                    {
                        "name": "Hoth",
                        "population": "unknown",
                        "terrain": "ice",
                        "climate": "frozen",
                        "url": "https://swapi.dev/api/planets/4/",
                    },
                    {
                        "name": "Coruscant",
                        "population": "1000000000000",
                        "terrain": "cityscape",
                        "climate": "temperate",
                        "url": "https://swapi.dev/api/planets/9/",
                    },
                    {
                        "name": "Dagobah",
                        "population": "1000",
                        "terrain": "swamp",
                        "climate": "murky",
                        "url": "https://swapi.dev/api/planets/5/",
                    },
                ],
                "next": None,
            }
        return {"results": [], "next": None}


def test_planets_map_categories():
    service = PlanetsMapService(FakeClient())
    items = service.planets_map(page_size=10)
    assert len(items) == 4
    categories = {item["name"]: item["category"] for item in items}
    assert categories["Tatooine"] == "arid"
    assert categories["Hoth"] == "unknown"
    assert categories["Coruscant"] == "core"
    assert categories["Dagobah"] == "frontier"


class PagedClient:
    def search(self, resource, query, page):
        if page == 1:
            return {
                "results": [
                    {
                        "name": "Ice",
                        "population": "100",
                        "terrain": "ice",
                        "climate": "frozen",
                        "url": "https://swapi.dev/api/planets/2/",
                    }
                ],
                "next": "page2",
            }
        if page == 2:
            return {
                "results": [
                    {
                        "name": "Weird",
                        "population": "unknown-value",
                        "terrain": "rocks",
                        "climate": "temperate",
                        "url": "https://swapi.dev/api/planets/3/",
                    }
                ],
                "next": None,
            }
        return {"results": [], "next": None}


def test_planets_map_multiple_pages_and_categories():
    service = PlanetsMapService(PagedClient())
    items = service.planets_map(page_size=1)
    categories = {item["name"]: item["category"] for item in items}
    assert categories["Ice"] == "ice"


def test_map_extract_id_cases():
    from holonet.services.planets_map_service import _extract_id

    assert _extract_id(None) is None
    assert _extract_id("") is None
    assert _extract_id("/planets/") is None
    assert _extract_id("///") is None
    assert _extract_id("https://swapi.dev/api/planets/abc/") is None


def test_map_categorize_invalid_population():
    from holonet.services.planets_map_service import _categorize

    assert _categorize("not-a-number", "temperate", "mountains") == "unknown"
