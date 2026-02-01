from typing import Any

from holonet.clients.swapi_client import SwapiClient
from holonet.config import settings
from holonet.errors import AppError
from holonet.schemas.search import SearchQuery
from holonet.utils.pagination import build_pagination
from holonet.utils.sorting import project_fields, safe_sort

ALLOWED_SORT_FIELDS = {
    "people": {
        "name",
        "height",
        "mass",
        "birth_year",
        "gender",
        "created",
        "edited",
    },
    "planets": {
        "name",
        "population",
        "diameter",
        "climate",
        "terrain",
        "created",
        "edited",
        "rotation_period",
        "orbital_period",
        "surface_water",
    },
    "starships": {
        "name",
        "model",
        "manufacturer",
        "cost_in_credits",
        "length",
        "crew",
        "passengers",
        "starship_class",
        "created",
        "edited",
    },
    "films": {
        "title",
        "episode_id",
        "release_date",
        "director",
        "producer",
        "created",
        "edited",
    },
    "species": {
        "name",
        "classification",
        "designation",
        "average_height",
        "average_lifespan",
        "language",
        "created",
        "edited",
    },
    "vehicles": {
        "name",
        "model",
        "manufacturer",
        "cost_in_credits",
        "length",
        "crew",
        "passengers",
        "vehicle_class",
        "created",
        "edited",
    },
}


class SearchService:
    def __init__(self, client: SwapiClient) -> None:
        self._client = client

    def search(
        self, query: SearchQuery
    ) -> tuple[list[dict[str, Any]], dict[str, Any], dict[str, Any]]:
        page = query.page
        page_size = min(query.page_size, settings.max_page_size)

        start = (page - 1) * page_size
        end = start + page_size

        aggregated: list[dict[str, Any]] = []
        total_items = 0
        swapi_page = 1
        fetched_pages = 0
        cache_meta: dict[str, Any] = {"hit": False, "ttl": settings.cache_ttl_seconds}

        while fetched_pages < settings.max_upstream_pages:
            payload = self._client.search(query.resource, query.q, swapi_page)
            cache_meta = payload.get("_cache", cache_meta)
            total_items = payload.get("count", total_items)
            results = payload.get("results", [])
            for item in results:
                item["id"] = _extract_id(item.get("url"))
                aggregated.append(item)
            fetched_pages += 1
            swapi_page += 1
            if payload.get("next") is None:
                break
            if len(aggregated) >= end:
                break

        if start >= len(aggregated) and total_items > 0:
            raise AppError("Page out of range", status_code=404, details={"page": page})

        items = aggregated[start:end]

        if query.sort:
            allowed = ALLOWED_SORT_FIELDS.get(query.resource, set())
            if query.sort not in allowed:
                raise AppError(
                    "Invalid sort field",
                    status_code=400,
                    details={"sort": query.sort, "allowed": sorted(allowed)},
                )
            items = safe_sort(items, query.sort, query.order)

        items = project_fields(items, query.fields)

        pagination = build_pagination(page, page_size, total_items)
        return items, pagination, cache_meta


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
