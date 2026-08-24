from fastapi import APIRouter

from blog.setting.schema import SettingResponse
from blog.setting.service import SettingService
from core.response import ApiResponse

router = APIRouter(
    prefix="/setting",
    tags=["设定"]
)

@router.get("/", response_model=ApiResponse[SettingResponse])
def get_setting():
    return ApiResponse(
        data=SettingService.get()
    )
    # return {"message": "Hello World"}