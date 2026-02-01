from typing import Literal

from pydantic import BaseModel, Field

ResourceName = Literal["people", "planets", "starships", "films", "species", "vehicles"]


class GraphQuery(BaseModel):
    start_resource: ResourceName
    start_id: int = Field(ge=1)
    depth: int = Field(default=1, ge=1, le=3)
