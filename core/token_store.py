import math

from .redis import sync_redis_client
from .security import REFRESH_TOKEN_EXPIRE_DAYS


SESSION_KEY_PREFIX = "auth:session:"
SESSION_REFRESH_KEY_PREFIX = "auth:session-refresh:"
REFRESH_KEY_PREFIX = "auth:refresh:"
USER_SESSIONS_KEY_PREFIX = "auth:user-sessions:"

REFRESH_TOKEN_TTL = max(
    1,
    math.ceil(REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60),
)


_ROTATE_REFRESH_TOKEN_SCRIPT = """
local old_refresh = redis.call("GET", KEYS[1])
local session_user = redis.call("GET", KEYS[2])
local current_jti = redis.call("GET", KEYS[3])
local expected_value = ARGV[1]

if not session_user then
    redis.call("SREM", KEYS[5], ARGV[3])
    return 0
end

if session_user ~= ARGV[6] then
    return 0
end

if old_refresh ~= expected_value or current_jti ~= ARGV[2] then
    redis.call("DEL", KEYS[1])
    if current_jti then
        redis.call("DEL", ARGV[4] .. current_jti)
    end
    redis.call("DEL", KEYS[2], KEYS[3])
    redis.call("SREM", KEYS[5], ARGV[3])
    return 2
end

redis.call("DEL", KEYS[1])
redis.call(
    "SET",
    KEYS[4],
    expected_value,
    "EX",
    ARGV[5]
)
redis.call(
    "SET",
    KEYS[2],
    session_user,
    "EX",
    ARGV[5]
)
redis.call(
    "SET",
    KEYS[3],
    ARGV[3],
    "EX",
    ARGV[5]
)
return 1
"""


_REVOKE_SESSION_SCRIPT = """
local current_jti = redis.call("GET", KEYS[2])

if current_jti then
    redis.call("DEL", ARGV[1] .. current_jti)
end

redis.call("DEL", KEYS[1], KEYS[2])
redis.call("SREM", KEYS[3], ARGV[2])
if redis.call("SCARD", KEYS[3]) == 0 then
    redis.call("DEL", KEYS[3])
end
return 1
"""


class TokenStore:
    """
    Redis-backed session and Refresh Token state.

    A session has exactly one active Refresh Token. Access Tokens only need
    the session marker, so logout/password changes can revoke them immediately.
    """

    def __init__(self, redis_client=None):
        self.redis = redis_client or sync_redis_client

    @staticmethod
    def _session_key(session_id: str) -> str:
        return f"{SESSION_KEY_PREFIX}{session_id}"

    @staticmethod
    def _session_refresh_key(session_id: str) -> str:
        return f"{SESSION_REFRESH_KEY_PREFIX}{session_id}"

    @staticmethod
    def _refresh_key(jti: str) -> str:
        return f"{REFRESH_KEY_PREFIX}{jti}"

    @staticmethod
    def _user_sessions_key(user_id: int) -> str:
        return f"{USER_SESSIONS_KEY_PREFIX}{user_id}"

    def create_session(
            self,
            *,
            user_id: int,
            session_id: str,
            refresh_jti: str,
    ) -> None:
        user_id_value = str(user_id)
        session_key = self._session_key(session_id)
        session_refresh_key = self._session_refresh_key(session_id)
        refresh_key = self._refresh_key(refresh_jti)
        user_sessions_key = self._user_sessions_key(user_id)
        refresh_value = f"{session_id}|{user_id_value}"

        with self.redis.pipeline(transaction=True) as pipeline:
            pipeline.set(
                session_key,
                user_id_value,
                ex=REFRESH_TOKEN_TTL,
            )
            pipeline.set(
                session_refresh_key,
                refresh_jti,
                ex=REFRESH_TOKEN_TTL,
            )
            pipeline.set(
                refresh_key,
                refresh_value,
                ex=REFRESH_TOKEN_TTL,
            )
            pipeline.sadd(user_sessions_key, session_id)
            pipeline.expire(user_sessions_key, REFRESH_TOKEN_TTL)
            pipeline.execute()

    def rotate_refresh_token(
            self,
            *,
            user_id: int,
            session_id: str,
            old_jti: str,
            new_jti: str,
    ) -> int:
        """
        Rotate a Refresh Token atomically.

        Returns 1 for success, 0 for an expired/revoked session, and 2 when
        the presented token is a replay or no longer the session's current
        token.
        """

        session_key = self._session_key(session_id)
        session_refresh_key = self._session_refresh_key(session_id)
        old_refresh_key = self._refresh_key(old_jti)
        new_refresh_key = self._refresh_key(new_jti)
        user_sessions_key = self._user_sessions_key(user_id)

        return int(self.redis.eval(
            _ROTATE_REFRESH_TOKEN_SCRIPT,
            5,
            old_refresh_key,
            session_key,
            session_refresh_key,
            new_refresh_key,
            user_sessions_key,
            f"{session_id}|{user_id}",
            old_jti,
            session_id,
            REFRESH_KEY_PREFIX,
            REFRESH_TOKEN_TTL,
            str(user_id),
        ))

    def is_session_active(self, *, user_id: int, session_id: str) -> bool:
        return self.redis.get(self._session_key(session_id)) == str(user_id)

    def revoke_session(self, *, user_id: int, session_id: str) -> None:
        self.redis.eval(
            _REVOKE_SESSION_SCRIPT,
            3,
            self._session_key(session_id),
            self._session_refresh_key(session_id),
            self._user_sessions_key(user_id),
            REFRESH_KEY_PREFIX,
            session_id,
        )

    def revoke_user_sessions(self, user_id: int) -> None:
        user_sessions_key = self._user_sessions_key(user_id)
        session_ids = self.redis.smembers(user_sessions_key)

        for session_id in session_ids:
            self.revoke_session(
                user_id=user_id,
                session_id=session_id,
            )

        # Remove the set itself when it is empty. This also cleans up stale
        # session IDs left behind after Redis expires their session keys.
        self.redis.delete(user_sessions_key)


token_store = TokenStore()
