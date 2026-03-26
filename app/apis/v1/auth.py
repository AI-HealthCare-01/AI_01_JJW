from datetime import UTC, datetime, timedelta
from typing import Annotated

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import ORJSONResponse

from app.core.config import config
from app.dependencies.auth import get_current_user
from app.services.oauth import OAuthService
from schemas import AuthResponse, OAuthRequest, UserInfo


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(UTC) + (expires_delta or timedelta(hours=24))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, config.JWT_SECRET, algorithm=config.JWT_ALGORITHM)


auth_router = APIRouter()


@auth_router.post("/oauth/login", response_model=AuthResponse)
async def oauth_login(request: OAuthRequest):
    try:
        oauth_service = OAuthService()

        if request.provider == "kakao":
            user_info = await oauth_service.get_kakao_user_info(
                request.code,
                request.redirect_uri,
            )
        elif request.provider == "naver":
            user_info = await oauth_service.get_naver_user_info(
                request.code,
                request.redirect_uri,
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="지원하지 않는 OAuth 제공자입니다",
            )

        access_token = oauth_service.create_access_token(user_info)

        return ORJSONResponse(content=AuthResponse(access_token=access_token, user_info=user_info).model_dump())

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"로그인 처리 중 오류가 발생했습니다: {e!s}",
        ) from e


@auth_router.get("/me", response_model=UserInfo)
async def get_user_profile(
    current_user: Annotated[UserInfo, Depends(get_current_user)],
):
    return ORJSONResponse(content=current_user.model_dump())


@auth_router.post("/logout")
async def logout():
    return ORJSONResponse(content={"message": "로그아웃되었습니다"})


@auth_router.post("/test-login")
async def test_login():
    test_user = {
        "user_id": "test_user_123",
        "email": "test@example.com",
        "name": "테스트 사용자",
        "provider": "test",
    }

    access_token = create_access_token(data={"user_id": test_user["user_id"]})

    response = ORJSONResponse(content={"access_token": access_token, "user_info": test_user})

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=config.ENV == "prod",
        max_age=3600 * 24 * 7,
    )

    return response


@auth_router.get("/oauth/urls")
async def get_oauth_urls():
    oauth_service = OAuthService()

    kakao_url = f"https://kauth.kakao.com/oauth/authorize?client_id={oauth_service.kakao_client_id}&response_type=code"

    naver_url = (
        f"https://nid.naver.com/oauth2.0/authorize"
        f"?client_id={oauth_service.naver_client_id}"
        f"&response_type=code"
        f"&state={{state}}"
    )

    return ORJSONResponse(
        content={
            "kakao": kakao_url,
            "naver": naver_url,
        }
    )
