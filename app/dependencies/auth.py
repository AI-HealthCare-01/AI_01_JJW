from typing import Annotated
from fastapi import Depends, HTTPException, status, Header
from app.services.oauth import OAuthService
from schemas import UserInfo


async def get_current_user(
    authorization: Annotated[str | None, Header()] = None
) -> UserInfo:
    """현재 인증된 사용자 정보 반환"""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="인증이 필요합니다"
        )
    
    try:
        # Bearer 토큰 추출
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Bearer 토큰이 필요합니다"
            )
        
        # 토큰 검증
        oauth_service = OAuthService()
        payload = oauth_service.verify_access_token(token)
        
        return UserInfo(
            user_id=payload["user_id"],
            email=payload["email"],
            name=payload["name"],
            provider=payload["provider"],
            profile_image=payload.get("profile_image")
        )
        
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="잘못된 토큰 형식입니다"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )