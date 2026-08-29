from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from core.pagination import PageResponse


def normalize_tag_name(value: str) -> str:
    value = value.strip()
    if not value:
        raise ValueError("标签名称不能为空")
    if len(value) > 50:
        raise ValueError("标签名称不能超过 50 个字符")
    return value


class TagCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=50)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        return normalize_tag_name(value)


class TagUpdateRequest(TagCreateRequest):
    pass


class TagResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    created_at: datetime
    article_count: int


class TagListResponse(BaseModel):
    tags: PageResponse[TagResponse]


class TagDeleteResponse(BaseModel):
    deleted_id: int
