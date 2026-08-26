from datetime import datetime

from pydantic import ConfigDict, BaseModel


class CommentListResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    nickname: str
    email: str | None
    content: str
    created_at: datetime


class CommentCreateRequest(BaseModel):
    nickname: str
    email: str | None = None
    QQ: int | None = None
    content: str

