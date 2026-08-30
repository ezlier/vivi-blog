from fastapi import APIRouter, HTTPException, Request, Query, Depends

from blog.comment.schema import (
    CommentListResponse,
    CommentCreateRequest,
    CommentResponse,
    CommentsBatchDeleteRequest,
    AdminCommentListResponse,
)
from blog.comment.service import UserCommentService, AdminCommentService
from core.dependencies import get_current_superuser
from core.rate_limit import rate_limit
from core.response import ApiResponse

router = APIRouter(
    prefix="/comment",
    tags=["评论"],
)


@router.get("/admin", response_model=ApiResponse[AdminCommentListResponse])
def getAllComments(
        page: int = Query(default=1, ge=1, ),
        page_size: int = Query(default=10, ge=1, le=100, ),
        current_user=Depends(get_current_superuser)
):
    return ApiResponse(data=AdminCommentService.getAllComment(page=page, page_size=page_size))


@router.delete("/", response_model=ApiResponse)
def deleteComments(
        data: CommentsBatchDeleteRequest,
        current_user=Depends(get_current_superuser)
):
    deleted_count = AdminCommentService.deleteCommentsByIds(data.ids)

    return ApiResponse(data={"deleted_count": deleted_count, })


# ===============================
# ===========↓用户接口↓===========
# ===============================


@router.get(
    "/{slug}/",
    response_model=ApiResponse[CommentListResponse],
    dependencies=[Depends(rate_limit(60))],
)
def getCommentBySlug(
        slug: str,
        page: int = Query(default=1, ge=1, ),
        page_size: int = Query(default=10, ge=1, le=100, )
):
    return ApiResponse(data=UserCommentService.getCommentBySlug(slug=slug, page=page, page_size=page_size))


@router.post(
    "/{slug}/",
    response_model=ApiResponse[CommentResponse],
    dependencies=[Depends(rate_limit(10, key_prefix="comment"))],
)
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
