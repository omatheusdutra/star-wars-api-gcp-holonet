from pydantic import BaseModel, Field


class PlanetsMapQuery(BaseModel):
    page_size: int = Field(default=10, ge=1, le=50)
