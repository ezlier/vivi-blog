from typing import Annotated

from django.contrib.auth import authenticate
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from core.rate_limit import rate_limit
from core.response import ApiResponse
from core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
)

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

    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)

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
def refresh(refresh_token: str, ):
    """
    使用 Refresh Token 获取新的 Access Token
    """

    try:
        payload = decode_token(refresh_token)

        if payload.get("type") != "refresh":
            raise ValueError("不是 Refresh Token")

        user_id = payload.get("sub")

        if not user_id:
            raise ValueError("Token 缺少用户标识")

    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效或已过期的 Refresh Token",
        )

    access_token = create_access_token(int(user_id))

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }
