from fastapi import APIRouter, Form, Request, Depends

from blog.message.schema import MessageListResponse, AdminMessageListResponse, MessageBatchDeleteRequest
from blog.message.service import MessageService
from core.dependencies import get_current_superuser
from core.response import ApiResponse

router = APIRouter(
    prefix='/message',
    tags=["留言"]
)


@router.get("/", response_model=ApiResponse[list[MessageListResponse]])
def getMessageList():
    return ApiResponse(data=MessageService.getMessageList())


@router.post("/", response_model=ApiResponse)
def createMessage(
        request: Request,
        content: str = Form(),
        nickname: str = Form(),
        email: str = Form(None),
        QQ: int = Form(None),
):
    MessageService.userCreateMessage(
        content=content,
        nickname=nickname,
        email=email,
        QQ=QQ,
        IP=request.state.client_ip
    )

    return ApiResponse()


# ============================
# ==========管理员接口==========
# ============================


@router.get("/admin", response_model=ApiResponse[list[AdminMessageListResponse]])
def adminGetMessage(current_user=Depends(get_current_superuser)):
    return ApiResponse(data=MessageService.getMessageList())


@router.delete("/admin/", response_model=ApiResponse)
def deleteArticleByID(
        data: MessageBatchDeleteRequest,
        current_user=Depends(get_current_superuser)
):
    deleted_count = (MessageService.deleteMessageBySlugs(data.ids))

    return ApiResponse(data={"deleted_count": deleted_count, })
