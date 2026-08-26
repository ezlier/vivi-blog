from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

from blog.comment.schema import CommentListResponse


class ArticleListResponse(BaseModel):
    title: str
    slug: str
    cover: str | None
    is_draft: bool
    created_at: datetime
    updated_at: datetime


class ArticleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    title: str
    slug: str
    cover: str | None
    content: str
    is_draft: bool
    created_at: datetime
    updated_at: datetime


class ArticleBatchDeleteRequest(BaseModel):
    slugs: list[str] = Field(min_length=1, max_length=100, )
