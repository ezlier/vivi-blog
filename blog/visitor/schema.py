from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from core.pagination import PageResponse


class VisitorCreateRequest(BaseModel):
    """
    前端主动上报访客访问
    """
    device_type: str | None = None


class VisitorResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: int
    ip_address: str
    user_agent: str
    device_type: str
    visited_at: datetime


class logsListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    logs: PageResponse[VisitorResponse]


class BlacklistCreateRequest(BaseModel):
    ip_address: str
    reason: str | None = None
    expires_at: datetime | None = None


class BlacklistUpdateRequest(BaseModel):
    ip_address: str | None = None
    reason: str | None = None
    is_active: bool | None = None
    expires_at: datetime | None = None


class BlacklistResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: int
    ip_address: str
    reason: str
    is_active: bool
    created_at: datetime
    expires_at: datetime | None


class BlacklistListResponse(BaseModel):
    blacklists: PageResponse[BlacklistResponse]


class deleteBlackListIdsBatchDeleteRequest(BaseModel):
    ids: list[int]
