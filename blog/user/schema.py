from pydantic import BaseModel


class refreshRequest(BaseModel):
    refresh_token: str