from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict

from core.pagination import PageResponse


class MessageResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    nickname: str
    content: str
    created_at: datetime


class MessageList(BaseModel):
    messages: PageResponse[MessageResponse]


class AdminMessageResponse(BaseModel):
    id: int
    IP: str | None
    nickname: str
    content: str
    QQ: str | int | None
    email: str | None
    created_at: datetime


class AdminMessageList(BaseModel):
    messages: PageResponse[AdminMessageResponse]


class MessageBatchDeleteRequest(BaseModel):
    ids: list[int] = Field(min_length=1, max_length=20)
