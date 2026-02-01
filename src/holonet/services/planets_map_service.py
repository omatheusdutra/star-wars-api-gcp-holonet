from typing import Any

from holonet.clients.swapi_client import SwapiClient
from holonet.config import settings


class PlanetsMapService:
    def __init__(self, client: SwapiClient) -> None:
        self._client = client

    def planets_map(self, page_size: int) -> list[dict[str, Any]]:
        planets: list[dict[str, Any]] = []
        page = 1
        fetched = 0
        while fetched < settings.map_max_pages:
            payload = self._client.search("planets", None, page)
            results = payload.get("results", [])
            for item in results:
                item["id"] = _extract_id(item.get("url"))
                planets.append(_to_map_item(item))
            fetched += 1
            page += 1
            if payload.get("next") is None:
                break
            if len(planets) >= page_size:
                break
        return planets[:page_size]


def _to_map_item(item: dict[str, Any]) -> dict[str, Any]:
    population = item.get("population")
    terrain = item.get("terrain") or "unknown"
    climate = item.get("climate") or "unknown"
    category = _categorize(population, climate, terrain)
    return {
        "id": item.get("id"),
        "name": item.get("name"),
        "terrain": terrain,
        "climate": climate,
        "population": population,
        "category": category,
        "meta": {
            "diameter": item.get("diameter"),
            "gravity": item.get("gravity"),
            "orbital_period": item.get("orbital_period"),
            "rotation_period": item.get("rotation_period"),
        },
    }


def _categorize(population: Any, climate: str, terrain: str) -> str:
    if population in ("unknown", None):
        return "unknown"
    try:
        pop = int(population)
    except ValueError:
        return "unknown"
    if pop > 1_000_000_000 and "temperate" in climate:
        return "core"
    if "frozen" in climate or "ice" in terrain:
        return "ice"
    if "arid" in climate or "desert" in terrain:
        return "arid"
    return "frontier"


def _extract_id(url: str | None) -> int | None:
    if not url:
        return None
    parts = [p for p in url.split("/") if p]
    if not parts:
        return None
    try:
        return int(parts[-1])
    except ValueError:
        return None
