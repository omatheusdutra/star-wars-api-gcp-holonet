from fastapi import APIRouter, Depends

from holonet.config import settings
from holonet.deps import correlation_id_dependency, get_swapi_client, require_api_key
from holonet.schemas.common import ItemEnvelope

router = APIRouter(tags=["resources"], dependencies=[Depends(require_api_key)])


@router.get("/films/{resource_id}", response_model=ItemEnvelope)
def get_film(
    resource_id: int,
    client=Depends(get_swapi_client),
    correlation_id: str = Depends(correlation_id_dependency),
):
    return _get_resource("films", resource_id, client, correlation_id)


@router.get("/people/{resource_id}", response_model=ItemEnvelope)
def get_person(
    resource_id: int,
    client=Depends(get_swapi_client),
    correlation_id: str = Depends(correlation_id_dependency),
):
    return _get_resource("people", resource_id, client, correlation_id)


@router.get("/planets/{resource_id}", response_model=ItemEnvelope)
def get_planet(
    resource_id: int,
    client=Depends(get_swapi_client),
    correlation_id: str = Depends(correlation_id_dependency),
):
    return _get_resource("planets", resource_id, client, correlation_id)


@router.get("/starships/{resource_id}", response_model=ItemEnvelope)
def get_starship(
    resource_id: int,
    client=Depends(get_swapi_client),
    correlation_id: str = Depends(correlation_id_dependency),
):
    return _get_resource("starships", resource_id, client, correlation_id)


@router.get("/films/{resource_id}/characters", response_model=dict)
def get_film_characters(
    resource_id: int,
    client=Depends(get_swapi_client),
    correlation_id: str = Depends(correlation_id_dependency),
):
    film = client.get_resource("films", resource_id)
    cache_meta = film.pop("_cache", {"hit": False, "ttl": settings.cache_ttl_seconds})
    characters = film.get("characters", [])
    from holonet.services.expand_service import ExpandService

    expanded = ExpandService(client).expand_urls(characters)
    return {
        "items": expanded,
        "film": {"id": resource_id, "title": film.get("title")},
        "source": {"name": "swapi", "url": settings.swapi_base_url},
        "cache": cache_meta,
        "correlation_id": correlation_id,
    }


@router.get("/people/{resource_id}/films", response_model=dict)
def get_person_films(
    resource_id: int,
    client=Depends(get_swapi_client),
    correlation_id: str = Depends(correlation_id_dependency),
):
    person = client.get_resource("people", resource_id)
    cache_meta = person.pop("_cache", {"hit": False, "ttl": settings.cache_ttl_seconds})
    films = person.get("films", [])
    from holonet.services.expand_service import ExpandService

    expanded = ExpandService(client).expand_urls(films)
    return {
        "items": expanded,
        "person": {"id": resource_id, "name": person.get("name")},
        "source": {"name": "swapi", "url": settings.swapi_base_url},
        "cache": cache_meta,
        "correlation_id": correlation_id,
    }


def _get_resource(resource: str, resource_id: int, client, correlation_id: str) -> dict:
    item = client.get_resource(resource, resource_id)
    cache_meta = item.pop("_cache", {"hit": False, "ttl": settings.cache_ttl_seconds})
    item["id"] = resource_id
    return {
        "item": item,
        "source": {"name": "swapi", "url": settings.swapi_base_url},
        "cache": cache_meta,
        "correlation_id": correlation_id,
    }
