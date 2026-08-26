from fastapi import APIRouter, HTTPException, Request

from blog.comment.schema import CommentListResponse, CommentCreateRequest
from blog.comment.service import UserCommentService
from core.response import ApiResponse

router = APIRouter(
    prefix="/comment",
    tags=["评论"],
)


@router.get("/{slug}/", response_model=ApiResponse[list[CommentListResponse]])
def getCommentBySlug(slug: str):
    return ApiResponse(data=UserCommentService.getCommentBySlug(slug))


@router.post("/{slug}/", response_model=ApiResponse[CommentListResponse], )
def create_comment(
        request: Request,
        slug: str,
        data: CommentCreateRequest,
):
    try:
        return ApiResponse(data=UserCommentService.createComment(
            article_slug=slug,
            nickname=data.nickname,
            email=data.email,
            QQ=data.QQ,
            content=data.content,
            IP=request.state.client_ip
        ))

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )


