from datetime import UTC, datetime, timedelta
from typing import Any

import httpx
import jwt
from fastapi import HTTPException, status

from app.core.config import config
from schemas import OAuthProvider, UserInfo


class OAuthService:
    def __init__(self):
        self.kakao_client_id = config.KAKAO_CLIENT_ID
        self.kakao_client_secret = config.KAKAO_CLIENT_SECRET
        self.naver_client_id = config.NAVER_CLIENT_ID
        self.naver_client_secret = config.NAVER_CLIENT_SECRET
        self.jwt_secret = config.JWT_SECRET
        self.jwt_algorithm = config.JWT_ALGORITHM

    async def get_kakao_user_info(self, code: str, redirect_uri: str) -> UserInfo:
        try:
            token_url = "https://kauth.kakao.com/oauth/token"
            token_data = {
                "grant_type": "authorization_code",
                "client_id": self.kakao_client_id,
                "code": code,
                "redirect_uri": redirect_uri,
            }
            if self.kakao_client_secret and self.kakao_client_secret not in ("", "your_kakao_client_secret"):
                token_data["client_secret"] = self.kakao_client_secret

            async with httpx.AsyncClient() as client:
                token_response = await client.post(token_url, data=token_data)
                if not token_response.is_success:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"카카오 토큰 발급 실패: {token_response.text}",
                    )
                token_json = token_response.json()
                access_token = token_json["access_token"]

                # id_token(JWT)에서 sub 추출 또는 tokeninfo API 사용
                # 어떤 사용자 정보도 요청하지 않고 인증만 수행
                tokeninfo_response = await client.get(
                    "https://kapi.kakao.com/v1/user/access_token_info",
                    headers={"Authorization": f"Bearer {access_token}"},
                )
                tokeninfo_response.raise_for_status()
                user_id = str(tokeninfo_response.json()["id"])

            return UserInfo(
                user_id=user_id,
                email="",
                name="",
                provider=OAuthProvider.KAKAO,
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"카카오 인증 실패: {e!s}",
            ) from e

    async def get_naver_user_info(self, code: str, redirect_uri: str) -> UserInfo:
        try:
            token_url = "https://nid.naver.com/oauth2.0/token"
            token_data = {
                "grant_type": "authorization_code",
                "client_id": self.naver_client_id,
                "client_secret": self.naver_client_secret,
                "code": code,
                "redirect_uri": redirect_uri,
            }
            async with httpx.AsyncClient() as client:
                token_response = await client.post(token_url, data=token_data)
                token_response.raise_for_status()
                access_token = token_response.json()["access_token"]

                user_response = await client.get(
                    "https://openapi.naver.com/v1/nid/me",
                    headers={"Authorization": f"Bearer {access_token}"},
                )
                user_response.raise_for_status()
                response_data = user_response.json().get("response", {})

            return UserInfo(
                user_id=response_data.get("id", ""),
                email=response_data.get("email", ""),
                name=response_data.get("name", ""),
                provider=OAuthProvider.NAVER,
                profile_image=response_data.get("profile_image"),
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"네이버 인증 실패: {e!s}",
            ) from e

    def create_access_token(self, user_info: UserInfo) -> str:
        payload = {
            "user_id": user_info.user_id,
            "email": user_info.email,
            "name": user_info.name,
            "provider": user_info.provider,
            "exp": datetime.now(UTC) + timedelta(hours=24),
            "iat": datetime.now(UTC),
        }
        return jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)

    def verify_access_token(self, token: str) -> dict[str, Any]:
        try:
            return jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
        except jwt.ExpiredSignatureError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="토큰이 만료되었습니다",
            ) from e
        except jwt.InvalidTokenError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="유효하지 않은 토큰입니다",
            ) from e

