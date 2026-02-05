from fastapi import APIRouter, Depends, Query

from holonet.config import settings
from holonet.deps import correlation_id_dependency, get_swapi_client
from holonet.errors import AppError
from holonet.schemas.common import ItemsEnvelope
from holonet.schemas.search import SearchQuery
from holonet.services.search_service import SearchService
from holonet.utils.fields import parse_fields

router = APIRouter(tags=["public"])


def _public_search(
    resource: str,
    q: str | None,
    search: str | None,
    page: int,
    page_size: int,
    sort: str | None,
    order_by: str | None,
    order: str,
    reverse: bool,
    fields: str | None,
    all_results: bool,
    client,
    correlation_id: str,
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
    if all_results:
        items, pagination, cache_meta = service.search_all(query)
    else:
        items, pagination, cache_meta = service.search(query)
    return {
        "items": items,
        "pagination": pagination,
        "source": {"name": "swapi", "url": settings.swapi_base_url},
        "cache": cache_meta,
        "correlation_id": correlation_id,
    }


@router.get("/films", response_model=ItemsEnvelope)
def public_films(
    q: str | None = Query(default=None),
    search: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=settings.api_page_size_default, ge=1),
    all: bool = Query(default=True, description="Return all results"),
    sort: str | None = Query(default=None),
    order_by: str | None = Query(default=None),
    order: str = Query(default="asc"),
    reverse: bool = Query(default=False),
    fields: str | None = Query(default=None),
    client=Depends(get_swapi_client),
    correlation_id: str = Depends(correlation_id_dependency),
):
    return _public_search(
        "films",
        q,
        search,
        page,
        page_size,
        sort,
        order_by,
        order,
        reverse,
        fields,
        all,
        client,
        correlation_id,
    )


@router.get("/characters", response_model=ItemsEnvelope)
def public_characters(
    q: str | None = Query(default=None),
    search: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=settings.api_page_size_default, ge=1),
    all: bool = Query(default=True, description="Return all results"),
    sort: str | None = Query(default=None),
    order_by: str | None = Query(default=None),
    order: str = Query(default="asc"),
    reverse: bool = Query(default=False),
    fields: str | None = Query(default=None),
    client=Depends(get_swapi_client),
    correlation_id: str = Depends(correlation_id_dependency),
):
    return _public_search(
        "people",
        q,
        search,
        page,
        page_size,
        sort,
        order_by,
        order,
        reverse,
        fields,
        all,
        client,
        correlation_id,
    )


@router.get("/planets", response_model=ItemsEnvelope)
def public_planets(
    q: str | None = Query(default=None),
    search: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=settings.api_page_size_default, ge=1),
    all: bool = Query(default=True, description="Return all results"),
    sort: str | None = Query(default=None),
    order_by: str | None = Query(default=None),
    order: str = Query(default="asc"),
    reverse: bool = Query(default=False),
    fields: str | None = Query(default=None),
    client=Depends(get_swapi_client),
    correlation_id: str = Depends(correlation_id_dependency),
):
    return _public_search(
        "planets",
        q,
        search,
        page,
        page_size,
        sort,
        order_by,
        order,
        reverse,
        fields,
        all,
        client,
        correlation_id,
    )


@router.get("/starships", response_model=ItemsEnvelope)
def public_starships(
    q: str | None = Query(default=None),
    search: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=settings.api_page_size_default, ge=1),
    all: bool = Query(default=True, description="Return all results"),
    sort: str | None = Query(default=None),
    order_by: str | None = Query(default=None),
    order: str = Query(default="asc"),
    reverse: bool = Query(default=False),
    fields: str | None = Query(default=None),
    client=Depends(get_swapi_client),
    correlation_id: str = Depends(correlation_id_dependency),
):
    return _public_search(
        "starships",
        q,
        search,
        page,
        page_size,
        sort,
        order_by,
        order,
        reverse,
        fields,
        all,
        client,
        correlation_id,
    )


@router.get("/vehicles", response_model=ItemsEnvelope)
def public_vehicles(
    q: str | None = Query(default=None),
    search: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=settings.api_page_size_default, ge=1),
    all: bool = Query(default=True, description="Return all results"),
    sort: str | None = Query(default=None),
    order_by: str | None = Query(default=None),
    order: str = Query(default="asc"),
    reverse: bool = Query(default=False),
    fields: str | None = Query(default=None),
    client=Depends(get_swapi_client),
    correlation_id: str = Depends(correlation_id_dependency),
):
    return _public_search(
        "vehicles",
        q,
        search,
        page,
        page_size,
        sort,
        order_by,
        order,
        reverse,
        fields,
        all,
        client,
        correlation_id,
    )


@router.get("/species", response_model=ItemsEnvelope)
def public_species(
    q: str | None = Query(default=None),
    search: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=settings.api_page_size_default, ge=1),
    all: bool = Query(default=True, description="Return all results"),
    sort: str | None = Query(default=None),
    order_by: str | None = Query(default=None),
    order: str = Query(default="asc"),
    reverse: bool = Query(default=False),
    fields: str | None = Query(default=None),
    client=Depends(get_swapi_client),
    correlation_id: str = Depends(correlation_id_dependency),
):
    return _public_search(
        "species",
        q,
        search,
        page,
        page_size,
        sort,
        order_by,
        order,
        reverse,
        fields,
        all,
        client,
        correlation_id,
    )
