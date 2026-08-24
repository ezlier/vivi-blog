from datetime import datetime
from pydantic import BaseModel


class SettingResponse(BaseModel):
    name: str
    web_name: str
    name_avatar: str
    about_md: str
    footer_text1: str
    footer_text2: str
    create_time: datetime