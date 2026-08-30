import os

import redis.asyncio as redis


REDIS_HOST = os.getenv(
    "REDIS_HOST",
    "127.0.0.1",
)

REDIS_PORT = int(
    os.getenv(
        "REDIS_PORT",
        "6379",
    )
)

REDIS_DB = int(
    os.getenv(
        "REDIS_DB",
        "0",
    )
)

REDIS_PASSWORD = os.getenv(
    "REDIS_PASSWORD"
)

REDIS_SOCKET_CONNECT_TIMEOUT = float(
    os.getenv(
        "REDIS_SOCKET_CONNECT_TIMEOUT",
        "0.5",
    )
)
REDIS_SOCKET_TIMEOUT = float(
    os.getenv(
        "REDIS_SOCKET_TIMEOUT",
        "0.5",
    )
)

redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    password=REDIS_PASSWORD or None,
    decode_responses=True,
    socket_connect_timeout=REDIS_SOCKET_CONNECT_TIMEOUT,
    socket_timeout=REDIS_SOCKET_TIMEOUT,
    health_check_interval=30,
)
