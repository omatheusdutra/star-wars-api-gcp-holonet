from typing import Any

from pydantic import BaseModel, Field


class CacheMeta(BaseModel):
    hit: bool = False
    ttl: int = 0


class SourceMeta(BaseModel):
    name: str
    url: str


class Pagination(BaseModel):
    page: int
    page_size: int
    total_items: int
    total_pages: int
    has_next: bool
    has_prev: bool


class ErrorBody(BaseModel):
    message: str
    status: int
    details: Any = Field(default_factory=dict)


class ErrorEnvelope(BaseModel):
    error: ErrorBody


class Envelope(BaseModel):
    source: SourceMeta
    cache: CacheMeta
    correlation_id: str | None = None


class ItemsEnvelope(Envelope):
    items: list[dict[str, Any]]
    pagination: Pagination | None = None


class ItemEnvelope(Envelope):
    item: dict[str, Any]
