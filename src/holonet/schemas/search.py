from typing import Literal

from pydantic import BaseModel, Field

ResourceName = Literal["people", "planets", "starships", "films", "species", "vehicles"]


class SearchQuery(BaseModel):
    resource: ResourceName
    q: str | None = Field(default=None, max_length=120)
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=100)
    sort: str | None = None
    order: Literal["asc", "desc"] = "asc"
    fields: list[str] | None = None
