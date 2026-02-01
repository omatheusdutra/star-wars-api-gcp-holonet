from fastapi import APIRouter, Depends, Query

from holonet.config import settings
from holonet.deps import correlation_id_dependency, get_swapi_client, require_api_key
from holonet.schemas.planets_map import PlanetsMapQuery
from holonet.services.planets_map_service import PlanetsMapService

router = APIRouter(tags=["planets"], dependencies=[Depends(require_api_key)])


@router.get("/planets/map")
def planets_map(
    page_size: int = Query(default=settings.api_page_size_default, ge=1, le=50),
    client=Depends(get_swapi_client),
    correlation_id: str = Depends(correlation_id_dependency),
):
    query = PlanetsMapQuery(page_size=page_size)
    items = PlanetsMapService(client).planets_map(query.page_size)
    return {
        "items": items,
        "source": {"name": "swapi", "url": settings.swapi_base_url},
        "cache": {"hit": False, "ttl": settings.cache_ttl_seconds},
        "correlation_id": correlation_id,
    }
