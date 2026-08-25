from fastapi import APIRouter, Form

from blog.message.schema import MessageListResponse
from blog.message.service import MessageService
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
        content: str = Form(),
        nickname: str = Form(...),
        email: str = Form(None),
        QQ: int = Form(None),
):
    MessageService.userCreateMessage(
        content=content,
        nickname=nickname,
        email=email,
        QQ=QQ
    )

    return ApiResponse()
