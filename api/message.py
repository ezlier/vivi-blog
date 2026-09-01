from fastapi import APIRouter, Form, Request, Depends, Query

from blog.comment.schema import CommentCreateRequest
from blog.message.schema import AdminMessageListResponse, MessageBatchDeleteRequest
from blog.message.service import MessageService
from core.dependencies import get_current_superuser
from core.rate_limit import rate_limit
from core.response import ApiResponse

router = APIRouter(
    prefix='/message',
    tags=["留言"]
)


@router.get(
    "/",
    response_model=ApiResponse,
    dependencies=[Depends(rate_limit(60))],
)
def getMessageList(
        page: int = Query(default=1, ge=1, ),
        page_size: int = Query(default=10, ge=1, le=100, ),
):
    return ApiResponse(data=MessageService.getMessageList(page=page, page_size=page_size))


@router.post(
    "/",
    response_model=ApiResponse,
    dependencies=[Depends(rate_limit(10, key_prefix="message"))],
)
def createMessage(
        request: Request,
        data: CommentCreateRequest,
):
    MessageService.userCreateMessage(
        content=data.content,
        nickname=data.nickname,
        email=data.email,
        QQ=data.QQ,
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
    deleted_count = (MessageService.deleteMessageByids(data.ids))

    return ApiResponse(data={"deleted_count": deleted_count, })
