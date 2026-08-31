import ipaddress
from datetime import datetime

from redis import Redis
from redis.exceptions import ResponseError

from core.redis import sync_redis_client


BLACKLIST_KEY = "blacklist:ips"
BLACKLIST_LOADED_KEY = "blacklist:loaded"

# Redis sorted set scores are Unix timestamps. This value represents no
# expiration and is far enough in the future for normal application use.
NEVER_EXPIRES = 32503680000.0


def normalize_blacklist_target(value: str) -> str:
    """
    Normalize an exact IP or an IPv4 wildcard target such as 17.*.*.*.
    """
    if not isinstance(value, str):
        raise ValueError("ip_address 必须是字符串")

    value = value.strip()
    if not value:
        raise ValueError("ip_address 不能为空")

    if "*" not in value:
        try:
            return str(ipaddress.ip_address(value))
        except ValueError as exc:
            raise ValueError("ip_address 必须是有效的 IP 地址或 IPv4 网段") from exc

    parts = value.split(".")
    if len(parts) != 4:
        raise ValueError("IPv4 网段必须使用类似 17.*.*.* 的格式")

    normalized_parts = []
    for part in parts:
        if part == "*":
            normalized_parts.append(part)
            continue

        if not part.isdigit():
            raise ValueError("IPv4 网段每段必须是 0-255 或 *")

        number = int(part)
        if number < 0 or number > 255:
            raise ValueError("IPv4 网段每段必须是 0-255 或 *")

        normalized_parts.append(str(number))

    return ".".join(normalized_parts)


def matching_blacklist_targets(ip_address: str) -> list[str]:
    """
    Return the exact IP and every IPv4 wildcard form that can match it.

    For 17.1.2.3 this includes 17.*.*.*, 17.1.*.*, *.*.*.* and so on.
    """
    try:
        parsed_ip = ipaddress.ip_address(ip_address)
    except ValueError:
        return [ip_address]

    if parsed_ip.version == 6:
        return [str(parsed_ip)]

    parts = str(parsed_ip).split(".")
    targets = []

    for mask in range(16):
        targets.append(
            ".".join(
                "*" if mask & (1 << index) else part
                for index, part in enumerate(parts)
            )
        )

    return targets


class RedisBlacklist:
    """
    Redis-backed blacklist cache.

    A sorted set stores blacklist targets as members and their expiration
    timestamps as scores. A separate marker distinguishes an initialized
    empty cache from a cache that has not been loaded yet.
    """

    def __init__(self, redis_client: Redis | None = None):
        self.redis = redis_client or sync_redis_client

    def is_loaded(self) -> bool:
        return bool(self.redis.exists(BLACKLIST_LOADED_KEY))

    def is_empty(self, now: datetime) -> bool:
        try:
            self._remove_expired(now)
            return self.redis.zcard(BLACKLIST_KEY) == 0
        except ResponseError as exc:
            # Recover from the Set format used by an older cache version.
            if "WRONGTYPE" not in str(exc).upper():
                raise
            self.clear()
            return True

    def load(self, blacklists) -> None:
        """
        Replace the Redis cache with active database blacklist records.
        """
        entries = {}
        for blacklist in blacklists:
            expires_at = blacklist.expires_at
            score = (
                expires_at.timestamp()
                if expires_at is not None
                else NEVER_EXPIRES
            )
            entries[blacklist.ip_address] = score

        pipeline = self.redis.pipeline()
        pipeline.delete(BLACKLIST_KEY)
        if entries:
            pipeline.zadd(BLACKLIST_KEY, entries)
        pipeline.set(BLACKLIST_LOADED_KEY, "1")
        pipeline.execute()

    def contains(self, ip_address: str, now: datetime) -> bool:
        self._remove_expired(now)
        targets = matching_blacklist_targets(ip_address)
        scores = self.redis.zmscore(BLACKLIST_KEY, targets)
        now_timestamp = now.timestamp()

        return any(
            score is not None and float(score) > now_timestamp
            for score in scores
        )

    def clear(self) -> None:
        self.redis.delete(BLACKLIST_KEY, BLACKLIST_LOADED_KEY)

    def _remove_expired(self, now: datetime) -> None:
        self.redis.zremrangebyscore(
            BLACKLIST_KEY,
            "-inf",
            now.timestamp(),
        )
