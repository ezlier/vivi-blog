from asgiref.sync import sync_to_async
from fastapi import Request
from fastapi.responses import JSONResponse

from blog.visitor.service import VisitorService
from core.request import get_client_ip


async def visitor_blacklist_middleware(request: Request, call_next, ):
    ip_address = get_client_ip(request)

    blocked = await sync_to_async(VisitorService.is_blocked, thread_sensitive=True, )(ip_address)

    if blocked:
        return JSONResponse(
            status_code=403,
            content={
                "code": 403,
                "message": "你的 IP 已被禁止访问",
                "data": None,
            },
        )

    response = await call_next(request)

    return response
