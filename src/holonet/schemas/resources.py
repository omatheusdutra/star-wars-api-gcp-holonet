from pydantic import BaseModel, Field


class ResourcePath(BaseModel):
    resource_id: int = Field(ge=1)
