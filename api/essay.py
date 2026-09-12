from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Query, Form, UploadFile, File, Depends, Request, HTTPException
from django.conf import settings

from blog.essay.schema import EssayListResponse, EssayResponse, EssayBatchDeleteRequest
from blog.essay.service import UserEssayService, AdminEssayService
from core.dependencies import get_current_superuser
from core.rate_limit import rate_limit
from core.response import ApiResponse
from core import MediaStorage

router = APIRouter(
    prefix="/essay",
    tags=["笔记"],
)


@router.get(
    "/",
    response_model=ApiResponse[EssayListResponse],
    dependencies=[Depends(rate_limit(60))],
)
def getEssayList(
        request: Request,
        page: int = Query(default=1, ge=1, ),
        page_size: int = Query(default=10, ge=1, le=100, ),
):
    return ApiResponse(
        data=
        UserEssayService.getEssayList(
            request=request, page=page, page_size=page_size,
        )
    )


# ============================
# ==========管理员接口==========
# ============================


def _serialize_essay(essay, request: Request):
    media_url = settings.MEDIA_URL.rstrip("/")
    base_url = str(request.base_url).rstrip("/")
    imgs = [
        f"{base_url}{media_url}/{img.lstrip('/')}"
        for img in MediaStorage.getImgs(essay.imgs)
    ]

    return {
        "title": essay.title,
        "slug": essay.slug,
        "content": essay.content,
        "imgs": imgs,
        "created_at": essay.created_at,
        "updated_at": essay.updated_at,
    }


@router.get("/slug", response_model=ApiResponse[EssayResponse])
def getEssayBySlug(
        request: Request,
        slug: str = Query(...),
        current_user=Depends(get_current_superuser),
):
    try:
        essay = AdminEssayService.getEssayBySlug(slug)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return ApiResponse(data=_serialize_essay(essay, request))


@router.post("/", response_model=ApiResponse)
def createEssay(
        title: str = Form(...),
        content: str = Form(...),
        is_draft: bool = Form(True),
        imgs: Annotated[list[UploadFile] | None, File()] = None,

        current_user=Depends(get_current_superuser)
):
    try:
        AdminEssayService.createEssay(
            title=title,
            content=content,
            is_draft=is_draft,
            imgs=imgs,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    return ApiResponse()


@router.delete("/slug", response_model=ApiResponse)
def deleteEssay(
        data: EssayBatchDeleteRequest,
        current_user=Depends(get_current_superuser),
):
    deleted_count = AdminEssayService.deleteEssay(data.slugs)
    return ApiResponse(data=deleted_count)


@router.put("/slug", response_model=ApiResponse)
def updateEssay(
        slug: str = Form(),
        title: str = Form(None),
        content: str = Form(None),
        imgs: Annotated[list[UploadFile] | None, File()] = None,
        created_at: datetime | None = Form(None),
        is_draft: bool | None = Form(None),

        current_user=Depends(get_current_superuser)
):
    try:
        AdminEssayService.updateEssayBySlug(
            slug=slug,
            title=title,
            content=content,
            imgs=imgs,
            created_at=created_at,
            is_draft=is_draft,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    return ApiResponse()
