from fastapi import APIRouter, Depends, Query

from holonet.config import settings
from holonet.deps import correlation_id_dependency, get_swapi_client, require_api_key
from holonet.schemas.graph import GraphQuery
from holonet.services.graph_service import GraphService

router = APIRouter(tags=["graph"], dependencies=[Depends(require_api_key)])


@router.get("/graph")
def graph(
    start_resource: str = Query(...),
    start_id: int = Query(..., ge=1),
    depth: int = Query(default=1, ge=1, le=3),
    client=Depends(get_swapi_client),
    correlation_id: str = Depends(correlation_id_dependency),
):
    query = GraphQuery(start_resource=start_resource, start_id=start_id, depth=depth)
    graph_data = GraphService(client).build_graph(query.start_resource, query.start_id, query.depth)
    return {
        "graph": graph_data,
        "source": {"name": "swapi", "url": settings.swapi_base_url},
        "cache": {"hit": False, "ttl": settings.cache_ttl_seconds},
        "correlation_id": correlation_id,
    }
