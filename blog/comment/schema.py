from datetime import datetime

from pydantic import ConfigDict, BaseModel, Field

from core.pagination import PageResponse


class CommentResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    nickname: str
    content: str
    created_at: datetime


class CommentCreateRequest(BaseModel):
    nickname: str = Field(min_length=1, max_length=20, description="昵称")
    email: str | None = Field(None, max_length=30, description="邮箱")
    QQ: str | None = Field(None, max_length=20, description="QQ号码")
    content: str = Field(min_length=1, max_length=200, description="评论内容，最多200字符")


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