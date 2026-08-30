from fastapi import (APIRouter, Request, Depends, Query, HTTPException, )
from starlette import status

from blog.visitor.schema import VisitorResponse, VisitorCreateRequest, BlacklistResponse, BlacklistCreateRequest, \
    deleteBlackListIdsBatchDeleteRequest, logsListResponse, BlacklistListResponse, BlacklistUpdateRequest
from blog.visitor.service import VisitorService
from core.dependencies import get_current_superuser
from core.request import get_client_ip
from core.rate_limit import rate_limit
from core.response import ApiResponse

router = APIRouter(
    prefix="/visitor",
    tags=["访客"],
)


@router.post(
    "/track",
    response_model=ApiResponse[VisitorResponse],
    dependencies=[Depends(rate_limit(30, key_prefix="visitor"))],
)
def track_visitor(data: VisitorCreateRequest, request: Request, ):
    ip_address = get_client_ip(request)
    user_agent = request.headers.get("User-Agent", "", )

    return ApiResponse(
        data=(
            VisitorService.record_visitor(
                ip_address=ip_address,
                user_agent=user_agent,
                device_type=data.device_type,
            )
        )
    )


@router.get("/logs", response_model=ApiResponse[logsListResponse], )
def get_logs(
        page: int = Query(default=1, ge=1, ),
        page_size: int = Query(default=10, ge=1, le=100, ),
        current_user=Depends(get_current_superuser)
):
    return ApiResponse(data=VisitorService.get_logs(page=page, page_size=page_size))


@router.post("/blacklist", response_model=ApiResponse[BlacklistResponse], status_code=status.HTTP_201_CREATED, )
def add_blacklist(
        data: BlacklistCreateRequest,
        current_user=Depends(get_current_superuser),
):
    return ApiResponse(
        data=(
            VisitorService.add_blacklist(
                ip_address=data.ip_address,
                reason=data.reason or "",
                expires_at=data.expires_at,
                created_by=current_user,
            )
        )
    )


@router.get("/blacklist", response_model=ApiResponse[BlacklistListResponse], )
def get_blacklist(
        page: int = Query(default=1, ge=1, ),
        page_size: int = Query(default=10, ge=1, le=100, ),
        current_user=Depends(get_current_superuser),
):
    return ApiResponse(
        data=VisitorService.get_blacklists(
            page=page,
            page_size=page_size,
        )
    )


@router.put("/blacklist/{blacklist_id}", response_model=ApiResponse[BlacklistResponse], )
def update_blacklist(
        blacklist_id: int,
        data: BlacklistUpdateRequest,
        current_user=Depends(get_current_superuser),
):
    try:
        return ApiResponse(
            data=VisitorService.update_blacklist(
                blacklist_id=blacklist_id,
                **data.model_dump(exclude_unset=True),
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


@router.delete("/blacklist", response_model=ApiResponse, )
def delete_blacklist(
        data: deleteBlackListIdsBatchDeleteRequest,
        current_user=Depends(get_current_superuser),
):
    deleted_count = (VisitorService.deleteArticleBySlugs(data.ids))

    return ApiResponse(data={"deleted_count": deleted_count, })
