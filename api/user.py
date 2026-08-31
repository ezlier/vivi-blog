from fastapi import APIRouter, Form, Depends

from blog.user.service import UserService
from core.dependencies import get_current_superuser
from core.response import ApiResponse

router = APIRouter(
    prefix="/user",
    tags=["用户"],
)


@router.post("/", response_model=ApiResponse)
def reNameOrPassword(
    newName: str = Form(None),
    pwd: str = Form(None),
    newPwd: str = Form(None),

    current_user=Depends(get_current_superuser)
):
    if newName:
        UserService.rename(current_user, newName)
    elif pwd and newPwd:
        UserService.repwd(current_user, pwd, newPwd)

    return ApiResponse()