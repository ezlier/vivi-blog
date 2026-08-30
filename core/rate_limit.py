import hashlib
import logging
import math
import time
import uuid

from django.conf import settings
from fastapi import HTTPException, Request, Response, status
from redis.exceptions import RedisError

from core.redis import redis_client
from core.request import get_client_ip


logger = logging.getLogger(__name__)


_SLIDING_WINDOW_SCRIPT = """
local now = tonumber(ARGV[1])
local window = tonumber(ARGV[2])
local limit = tonumber(ARGV[3])
local member = ARGV[4]

redis.call("ZREMRANGEBYSCORE", KEYS[1], "-inf", now - window)
local count = redis.call("ZCARD", KEYS[1])

if count >= limit then
    local oldest = redis.call("ZRANGE", KEYS[1], 0, 0, "WITHSCORES")
    local retry_ms = window

    if oldest[2] then
        retry_ms = tonumber(oldest[2]) + window - now
    end

    redis.call("EXPIRE", KEYS[1], math.ceil(window / 1000))
    return {0, math.max(1, math.ceil(retry_ms / 1000)), count}
end

redis.call("ZADD", KEYS[1], now, member)
redis.call("EXPIRE", KEYS[1], math.ceil(window / 1000))
return {1, 0, count + 1}
"""


class RateLimiter:
    """
    FastAPI Dependency：按客户端 IP 和路由执行 Redis 滑动窗口限流。
    """

    def __init__(
            self,
            requests: int,
            window_seconds: int = 60,
            key_prefix: str = "api",
    ):
        if requests < 1:
            raise ValueError("requests 必须大于等于 1")
        if window_seconds < 1:
            raise ValueError("window_seconds 必须大于等于 1")

        self.requests = requests
        self.window_seconds = window_seconds
        self.key_prefix = key_prefix

    async def __call__(
            self,
            request: Request,
            response: Response,
    ) -> None:
        if not getattr(settings, "RATE_LIMIT_ENABLED", True):
            return

        client_ip = get_client_ip(request)
        route = request.scope.get("route")
        route_path = getattr(route, "path", request.url.path)
        redis_key = self._build_key(client_ip, route_path)

        now_ms = time.time_ns() // 1_000_000
        window_ms = self.window_seconds * 1000
        member = f"{now_ms}:{uuid.uuid4().hex}"

        try:
            result = await redis_client.eval(
                _SLIDING_WINDOW_SCRIPT,
                1,
                redis_key,
                now_ms,
                window_ms,
                self.requests,
                member,
            )
        except (RedisError, OSError):
            logger.exception(
                "Redis rate limiter is unavailable, key=%s",
                redis_key,
            )

            if getattr(settings, "RATE_LIMIT_FAIL_OPEN", True):
                return

            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="限流服务暂不可用，请稍后重试",
            )

        allowed = bool(int(result[0]))
        retry_after = max(1, int(result[1])) if not allowed else 0
        current_count = int(result[2])
        remaining = max(0, self.requests - current_count)

        headers = {
            "X-RateLimit-Limit": str(self.requests),
            "X-RateLimit-Remaining": str(remaining),
            "X-RateLimit-Reset": str(
                math.ceil((now_ms + window_ms) / 1000)
            ),
        }
        response.headers.update(headers)

        if not allowed:
            headers["Retry-After"] = str(retry_after)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"访问过于频繁，每 {self.window_seconds} 秒最多请求 {self.requests} 次",
                headers=headers,
            )

    def _build_key(self, client_ip: str, route_path: str) -> str:
        raw_key = f"{self.key_prefix}:{client_ip}:{route_path}"
        digest = hashlib.sha256(raw_key.encode("utf-8")).hexdigest()
        return f"rate-limit:{self.key_prefix}:{digest}"


def rate_limit(
        requests_per_minute: int,
        *,
        key_prefix: str = "api",
) -> RateLimiter:
    """
    创建每分钟限流 Dependency。

    示例：
        dependencies=[Depends(rate_limit(60))]
    """
    return RateLimiter(
        requests=requests_per_minute,
        window_seconds=60,
        key_prefix=key_prefix,
    )
