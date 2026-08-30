from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request

from core.request import get_client_ip


class ClientIPMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        ip = get_client_ip(request)
        request.state.client_ip = ip
        response = await call_next(request)
        return response
