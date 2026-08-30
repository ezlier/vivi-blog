from fastapi import APIRouter, Depends, HTTPException, Query, status

from blog.tag.schema import (
    TagCreateRequest,
    TagDeleteResponse,
    TagListResponse,
    TagResponse,
    TagUpdateRequest,
)
from blog.tag.service import TagService
from core.dependencies import get_current_superuser
from core.rate_limit import rate_limit
from core.response import ApiResponse

router = APIRouter(
    prefix="/tags",
    tags=["标签"],
)


@router.get(
    "",
    response_model=ApiResponse[TagListResponse],
    dependencies=[Depends(rate_limit(60))],
)
def get_tags(
        page: int = Query(default=1, ge=1),
        page_size: int = Query(default=10, ge=1, le=100),
):
    return ApiResponse(
        data=TagService.get_tags(
            page=page,
            page_size=page_size,
        )
    )


@router.post("", response_model=ApiResponse[TagResponse])
def create_tag(
        data: TagCreateRequest,
        current_user=Depends(get_current_superuser),
):
    try:
        return ApiResponse(data=TagService.create_tag(data.name))
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.put("/{tag_id}", response_model=ApiResponse[TagResponse])
def update_tag(
        tag_id: int,
        data: TagUpdateRequest,
        current_user=Depends(get_current_superuser),
):
    try:
        return ApiResponse(
            data=TagService.update_tag(
                tag_id=tag_id,
                name=data.name,
            )
        )
    except LookupError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete("/{tag_id}", response_model=ApiResponse[TagDeleteResponse], )
def delete_tag(
        tag_id: int,
        current_user=Depends(get_current_superuser),
):
    try:
        TagService.delete_tag(tag_id)
    except LookupError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    return ApiResponse(data={"deleted_id": tag_id})
