from datetime import datetime

from pydantic import BaseModel, ConfigDict

from core.pagination import PageResponse


class EssayResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    title: str
    slug: str
    content: str
    imgs: list[str] | None
    updated_at: datetime
    created_at: datetime


class EssayListResponse(BaseModel):
    essayList: PageResponse[EssayResponse]