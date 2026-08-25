from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request


class ClientIPMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        ip = request.client.host
        request.state.client_ip = ip
        response = await call_next(request)
        return response