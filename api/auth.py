from typing import Annotated
from uuid import uuid4

from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from redis.exceptions import RedisError

from blog.user.schema import refreshRequest
from core.dependencies import get_current_token_payload, get_current_user
from core.rate_limit import rate_limit
from core.response import ApiResponse
from core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
)
from core.token_store import token_store

User = get_user_model()

router = APIRouter(
    prefix="/auth",
    tags=["认证"],
)


@router.post(
    "/login",
    response_model=ApiResponse,
    dependencies=[Depends(rate_limit(5, key_prefix="auth"))],
)
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], ):
    """
    用户登录
    """

    user = authenticate(
        username=form_data.username,
        password=form_data.password,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用",
        )

    session_id = uuid4().hex
    refresh_jti = uuid4().hex

    access_token = create_access_token(
        user.id,
        session_id=session_id,
    )
    refresh_token = create_refresh_token(
        user.id,
        session_id=session_id,
        jti=refresh_jti,
    )

    try:
        token_store.create_session(
            user_id=user.id,
            session_id=session_id,
            refresh_jti=refresh_jti,
        )
    except (RedisError, OSError):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="认证服务暂不可用，请稍后重试",
        )

    return ApiResponse(data={
        "user": form_data.username,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    })


@router.post(
    "/refresh",
    dependencies=[Depends(rate_limit(20, key_prefix="auth"))],
)
def refresh(data: refreshRequest, ):
    """
    使用 Refresh Token 获取新的 Access Token
    """

    try:
        payload = decode_token(data.refresh_token)

        if payload.get("type") != "refresh":
            raise ValueError("不是 Refresh Token")

        user_id = payload.get("sub")
        session_id = payload.get("sid")
        old_jti = payload.get("jti")

        if not user_id or not session_id or not old_jti:
            raise ValueError("Token 缺少必要字段")

        user_id = int(user_id)

    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效或已过期的 Refresh Token",
        )

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        try:
            token_store.revoke_session(
                user_id=user_id,
                session_id=session_id,
            )
        except (RedisError, OSError):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="认证服务暂不可用，请稍后重试",
            )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
        )

    if not user.is_active:
        try:
            token_store.revoke_session(
                user_id=user_id,
                session_id=session_id,
            )
        except (RedisError, OSError):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="认证服务暂不可用，请稍后重试",
            )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户已被禁用",
        )

    new_jti = uuid4().hex
    access_token = create_access_token(
        user_id,
        session_id=session_id,
    )
    refresh_token = create_refresh_token(
        user_id,
        session_id=session_id,
        jti=new_jti,
    )

    try:
        rotation_result = token_store.rotate_refresh_token(
            user_id=user_id,
            session_id=session_id,
            old_jti=old_jti,
            new_jti=new_jti,
        )
    except (RedisError, OSError):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="认证服务暂不可用，请稍后重试",
        )

    if rotation_result == 0:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh Token 已失效",
        )

    if rotation_result == 2:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="检测到 Refresh Token 重放，会话已撤销",
        )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post(
    "/logout",
    response_model=ApiResponse,
)
def logout(
        payload=Depends(get_current_token_payload),
        current_user=Depends(get_current_user),
):
    """
    撤销当前登录会话。
    """

    try:
        token_store.revoke_session(
            user_id=current_user.id,
            session_id=payload["sid"],
        )
    except (RedisError, OSError):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="认证服务暂不可用，请稍后重试",
        )

    return ApiResponse()
