from typing import Annotated

from django.contrib.auth import get_user_model
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from .security import decode_token

User = get_user_model()

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login"
)


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    """
    根据 JWT 获取当前 Django User
    """

    try:
        payload = decode_token(token)

        if payload.get("type") != "access":
            raise ValueError("不是 Access Token")

        user_id = payload.get("sub")

        if not user_id:
            raise ValueError("Token 缺少用户标识")

    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效或已过期的 Token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user = User.objects.get(id=int(user_id))
    except User.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户已被禁用",
        )

    return user


def get_current_superuser(user=Depends(get_current_user), ):
    """
    要求当前用户必须是 Django superuser
    """

    if not user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要超级管理员权限",
        )

    return user
