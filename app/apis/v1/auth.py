from datetime import datetime, timedelta
from typing import Annotated
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import ORJSONResponse as Response
import jwt

from app.services.oauth import OAuthService
from app.dependencies.auth import get_current_user
from app.core.config import config
from schemas import OAuthRequest, AuthResponse, UserInfo


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=24)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config.JWT_SECRET, algorithm=config.JWT_ALGORITHM)
    return encoded_jwt

auth_router = APIRouter()


@auth_router.post("/oauth/login", response_model=AuthResponse)
async def oauth_login(request: OAuthRequest):
    """OAuth 로그인"""
    try:
        oauth_service = OAuthService()
        
        # OAuth 제공자별 사용자 정보 조회
        if request.provider == "kakao":
            user_info = await oauth_service.get_kakao_user_info(
                request.code, 
                request.redirect_uri
            )
        elif request.provider == "naver":
            user_info = await oauth_service.get_naver_user_info(
                request.code, 
                request.redirect_uri
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="지원하지 않는 OAuth 제공자입니다"
            )
        
        # JWT 토큰 생성
        access_token = oauth_service.create_access_token(user_info)
        
        return ORJSONResponse(
            content=AuthResponse(
                access_token=access_token,
                user_info=user_info
            ).dict()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"로그인 처리 중 오류가 발생했습니다: {str(e)}"
        )


@auth_router.get("/me", response_model=UserInfo)
async def get_user_profile(
    current_user: Annotated[UserInfo, Depends(get_current_user)]
):
    """현재 사용자 정보 조회"""
    return ORJSONResponse(content=current_user.dict())


@auth_router.post("/logout")
async def logout():
    """로그아웃 (클라이언트에서 토큰 삭제)"""
    return ORJSONResponse(
        content={"message": "로그아웃되었습니다"}
    )


@auth_router.post("/test-login")
async def test_login():
    """테스트용 로그인 (OAuth 설정 없이 사용 가능)"""
    test_user = {
        "user_id": "test_user_123",
        "email": "test@example.com",
        "name": "테스트 사용자",
        "provider": "test"
    }
    
    # JWT 토큰 생성
    access_token = create_access_token(data={"user_id": test_user["user_id"]})
    
    response = Response(
        content={
            "access_token": access_token,
            "user_info": test_user
        }
    )
    
    # 쿠키에도 토큰 저장
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=config.ENV == "prod",
        max_age=3600 * 24 * 7  # 7일
    )
    
    return response


@auth_router.get("/oauth/urls")
async def get_oauth_urls():
    """OAuth 인증 URL 제공"""
    oauth_service = OAuthService()
    
    kakao_url = (
        f"https://kauth.kakao.com/oauth/authorize"
        f"?client_id={oauth_service.kakao_client_id}"
        f"&redirect_uri={{redirect_uri}}"
        f"&response_type=code"
    )
    
    naver_url = (
        f"https://nid.naver.com/oauth2.0/authorize"
        f"?client_id={oauth_service.naver_client_id}"
        f"&redirect_uri={{redirect_uri}}"
        f"&response_type=code"
        f"&state={{state}}"
    )
    
    return ORJSONResponse(content={
        "kakao": kakao_url,
        "naver": naver_url
    })