from datetime import datetime

from pydantic import BaseModel


class MessageListResponse(BaseModel):
    nickname: str
    content: str
    QQ: str | None
    email: str | None
    created_at: datetime