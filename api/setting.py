from datetime import datetime

from fastapi import APIRouter, Form, UploadFile, File

from blog.setting.schema import SettingResponse
from blog.setting.service import SettingService, AdminSettingService
from core.response import ApiResponse

router = APIRouter(
    prefix="/setting",
    tags=["设定"]
)

@router.get("/", response_model=ApiResponse[SettingResponse])
def getSetting():
    return ApiResponse(
        data=SettingService.get()
    )
    # return {"message": "Hello World"}


# ============================
# ==========管理员接口==========
# ============================


@router.put("/", response_model=ApiResponse)
def updateSetting(
    name: str = Form(),
    web_name: str = Form(),
    name_avatar: UploadFile | None = File(None),
    about_md: str = Form(),
    footer_text1: str = Form(),
    footer_text2: str = Form(),
    create_time: datetime | None = Form(None),
):
    AdminSettingService.update(
        name=name,
        web_name=web_name,
        name_avatar=name_avatar,
        about_md=about_md,
        footer_text1=footer_text1,
        footer_text2=footer_text2,
        create_time=create_time
    )
    return ApiResponse()