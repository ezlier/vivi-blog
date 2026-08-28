from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from core.pagination import PageResponse


class EssayResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    title: str
    slug: str
    content: str
    imgs: list[str] | None
    updated_at: datetime
    created_at: datetime


class EssayListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    essayList: PageResponse[EssayResponse]


class EssayBatchDeleteRequest(BaseModel):
    slugs: list[str] = Field(min_length=1, max_length=100, )