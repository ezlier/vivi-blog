from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from fastapi import HTTPException, status
from redis.exceptions import RedisError

from core.token_store import token_store


class UserService:

    @staticmethod
    def rename(user, newName):
        user.username = newName
        user.save()

    @staticmethod
    def repwd(user, pwd, newPwd):
        if not user.check_password(pwd):
            raise HTTPException(status_code=401, detail="Old Password error")

        try:
            validate_password(newPwd, user)
        except ValidationError as error:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error.messages,
            )

        try:
            # Revoke before saving the new password so a Redis failure cannot
            # leave the old sessions usable after the password is changed.
            token_store.revoke_user_sessions(user.id)
        except (RedisError, OSError):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="认证服务暂不可用，请稍后重试",
            )

        user.set_password(newPwd)
        user.save()
