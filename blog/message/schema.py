from datetime import datetime

from pydantic import BaseModel, Field


class MessageListResponse(BaseModel):
    nickname: str
    content: str
    QQ: str | None
    email: str | None
    created_at: datetime


class AdminMessageListResponse(BaseModel):
    id: int
    IP: str | None
    nickname: str
    content: str
    QQ: str | None
    email: str | None
    created_at: datetime


class MessageBatchDeleteRequest(BaseModel):
    ids: list[int] = Field(min_length=1, max_length=20)
