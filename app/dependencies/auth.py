from typing import Annotated

from fastapi import Header, HTTPException, status

from app.services.oauth import OAuthService
from schemas import UserInfo


async def get_current_user(
    authorization: Annotated[str | None, Header()] = None,
) -> UserInfo:
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="인증이 필요합니다",
        )

    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Bearer 토큰이 필요합니다",
            )

        oauth_service = OAuthService()
        payload = oauth_service.verify_access_token(token)

        return UserInfo(
            user_id=payload["user_id"],
            email=payload["email"],
            name=payload["name"],
            provider=payload["provider"],
            profile_image=payload.get("profile_image"),
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="잘못된 토큰 형식입니다",
        ) from e
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        ) from e
