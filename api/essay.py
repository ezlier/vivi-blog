from typing import Annotated

from fastapi import APIRouter, Query, Form, UploadFile, File, Depends

from blog.essay.schema import EssayListResponse, EssayResponse, EssayBatchDeleteRequest
from blog.essay.service import UserEssayService, AdminEssayService
from core.dependencies import get_current_superuser
from core.response import ApiResponse

router = APIRouter(
    prefix="/essay",
    tags=["笔记"],
)


@router.get("/", response_model=ApiResponse[EssayListResponse])
def getEssayList(
        page: int = Query(default=1, ge=1, ),
        page_size: int = Query(default=10, ge=1, le=100, ),
):
    return ApiResponse(data=UserEssayService.getEssayList(page, page_size))


@router.get("/slug", response_model=ApiResponse[EssayResponse])
def getEssayBySlug(slug: str):
    pass


# ============================
# ==========管理员接口==========
# ============================


@router.post("/", response_model=ApiResponse)
def createEssay(
        title: str = Form(...),
        content: str = Form(...),
        is_draft: bool = Form(True),
        imgs: Annotated[list[UploadFile] | None, File()] = None,

        current_user=Depends(get_current_superuser)
):
    AdminEssayService.createEssay(
        title=title,
        content=content,
        is_draft=is_draft,
        imgs=imgs,
    )
    return ApiResponse()


@router.delete("/slug", response_model=ApiResponse)
def deleteEssay(
        data: EssayBatchDeleteRequest,
        current_user=Depends(get_current_superuser),
):
    deleted_count = AdminEssayService.deleteEssay(data.slugs)
    return ApiResponse(data=deleted_count)
