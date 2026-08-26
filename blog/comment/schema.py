from datetime import datetime

from pydantic import ConfigDict, BaseModel, Field

from core.pagination import PageResponse


class CommentResponse(BaseModel):
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


class CommentListResponse(BaseModel):
    comments: PageResponse[CommentResponse]


class AdminCommentResponse(BaseModel):
    id: int
    IP: str
    nickname: str
    email: str | None
    QQ: int | None
    content: str
    article_title: str
    created_at: datetime


class AdminCommentListResponse(BaseModel):
    comments: PageResponse[AdminCommentResponse]


class CommentsBatchDeleteRequest(BaseModel):
    ids: list[int] = Field(min_length=1, max_length=100, )