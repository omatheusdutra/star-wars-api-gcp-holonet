from fastapi import APIRouter, Depends, Query

from holonet.config import settings
from holonet.deps import correlation_id_dependency, get_swapi_client, require_api_key
from holonet.errors import AppError
from holonet.schemas.common import ItemsEnvelope
from holonet.schemas.search import SearchQuery
from holonet.services.search_service import SearchService
from holonet.utils.fields import parse_fields

router = APIRouter(tags=["search"], dependencies=[Depends(require_api_key)])


@router.get("/search", response_model=ItemsEnvelope)
def search(
    resource: str = Query(...),
    q: str | None = Query(default=None),
    search: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=settings.api_page_size_default, ge=1),
    sort: str | None = Query(default=None),
    order_by: str | None = Query(default=None),
    order: str = Query(default="asc"),
    reverse: bool = Query(default=False),
    fields: str | None = Query(default=None),
    client=Depends(get_swapi_client),
    correlation_id: str = Depends(correlation_id_dependency),
):
    if page_size > settings.max_page_size:
        raise AppError(
            "page_size exceeds maximum",
            status_code=400,
            details={"max_page_size": settings.max_page_size},
        )
    if q is None and search:
        q = search
    if sort is None and order_by:
        sort = order_by
    if reverse:
        order = "desc"
    query = SearchQuery(
        resource=resource,
        q=q,
        page=page,
        page_size=page_size,
        sort=sort,
        order=order,
        fields=parse_fields(fields),
    )
    service = SearchService(client)
    items, pagination, cache_meta = service.search(query)
    return {
        "items": items,
        "pagination": pagination,
        "source": {"name": "swapi", "url": settings.swapi_base_url},
        "cache": cache_meta,
        "correlation_id": correlation_id,
    }
