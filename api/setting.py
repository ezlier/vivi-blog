from datetime import datetime

from fastapi import APIRouter, Form, UploadFile, File, Depends, HTTPException

from blog.setting.schema import SettingResponse
from blog.setting.service import SettingService, AdminSettingService
from core.dependencies import get_current_superuser
from core.rate_limit import rate_limit
from core.response import ApiResponse

router = APIRouter(
    prefix="/setting",
    tags=["设定"]
)

@router.get(
    "/",
    response_model=ApiResponse[SettingResponse],
    dependencies=[Depends(rate_limit(60))],
)
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

    current_user=Depends(get_current_superuser)
):
    try:
        AdminSettingService.update(
            name=name,
            web_name=web_name,
            name_avatar=name_avatar,
            about_md=about_md,
            footer_text1=footer_text1,
            footer_text2=footer_text2,
            create_time=create_time
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    return ApiResponse()
