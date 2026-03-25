import httpx
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, status

from app.core.config import config
from schemas import OAuthProvider, UserInfo


class OAuthService:
    def __init__(self):
        self.kakao_client_id = getattr(config, 'KAKAO_CLIENT_ID', 'your_kakao_client_id')
        self.kakao_client_secret = getattr(config, 'KAKAO_CLIENT_SECRET', 'your_kakao_client_secret')
        self.naver_client_id = getattr(config, 'NAVER_CLIENT_ID', 'your_naver_client_id')
        self.naver_client_secret = getattr(config, 'NAVER_CLIENT_SECRET', 'your_naver_client_secret')
        self.jwt_secret = getattr(config, 'JWT_SECRET', 'your-super-secret-jwt-key-change-in-production')
        self.jwt_algorithm = getattr(config, 'JWT_ALGORITHM', 'HS256')
    
    async def get_kakao_user_info(self, code: str, redirect_uri: str) -> UserInfo:
        """카카오 OAuth로 사용자 정보 조회"""
        try:
            # 1. 액세스 토큰 요청
            token_url = "https://kauth.kakao.com/oauth/token"
            token_data = {
                "grant_type": "authorization_code",
                "client_id": self.kakao_client_id,
                "client_secret": self.kakao_client_secret,
                "code": code,
                "redirect_uri": redirect_uri
            }
            
            async with httpx.AsyncClient() as client:
                token_response = await client.post(token_url, data=token_data)
                token_response.raise_for_status()
                token_info = token_response.json()
                
                access_token = token_info["access_token"]
                
                # 2. 사용자 정보 요청
                user_url = "https://kapi.kakao.com/v2/user/me"
                headers = {"Authorization": f"Bearer {access_token}"}
                
                user_response = await client.get(user_url, headers=headers)
                user_response.raise_for_status()
                user_data = user_response.json()
                
                # 3. 사용자 정보 파싱
                kakao_account = user_data.get("kakao_account", {})
                profile = kakao_account.get("profile", {})
                
                return UserInfo(
                    user_id=str(user_data["id"]),
                    email=kakao_account.get("email", ""),
                    name=profile.get("nickname", ""),
                    provider=OAuthProvider.KAKAO,
                    profile_image=profile.get("profile_image_url")
                )
                
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"카카오 인증 실패: {str(e)}"
            )
    
    async def get_naver_user_info(self, code: str, redirect_uri: str) -> UserInfo:
        """네이버 OAuth로 사용자 정보 조회"""
        try:
            # 1. 액세스 토큰 요청
            token_url = "https://nid.naver.com/oauth2.0/token"
            token_data = {
                "grant_type": "authorization_code",
                "client_id": self.naver_client_id,
                "client_secret": self.naver_client_secret,
                "code": code,
                "redirect_uri": redirect_uri
            }
            
            async with httpx.AsyncClient() as client:
                token_response = await client.post(token_url, data=token_data)
                token_response.raise_for_status()
                token_info = token_response.json()
                
                access_token = token_info["access_token"]
                
                # 2. 사용자 정보 요청
                user_url = "https://openapi.naver.com/v1/nid/me"
                headers = {"Authorization": f"Bearer {access_token}"}
                
                user_response = await client.get(user_url, headers=headers)
                user_response.raise_for_status()
                user_data = user_response.json()
                
                # 3. 사용자 정보 파싱
                response_data = user_data.get("response", {})
                
                return UserInfo(
                    user_id=response_data.get("id", ""),
                    email=response_data.get("email", ""),
                    name=response_data.get("name", ""),
                    provider=OAuthProvider.NAVER,
                    profile_image=response_data.get("profile_image")
                )
                
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"네이버 인증 실패: {str(e)}"
            )
    
    def create_access_token(self, user_info: UserInfo) -> str:
        """JWT 액세스 토큰 생성"""
        payload = {
            "user_id": user_info.user_id,
            "email": user_info.email,
            "name": user_info.name,
            "provider": user_info.provider,
            "exp": datetime.utcnow() + timedelta(hours=24),
            "iat": datetime.utcnow()
        }
        
        return jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)
    
    def verify_access_token(self, token: str) -> Dict[str, Any]:
        """JWT 토큰 검증"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="토큰이 만료되었습니다"
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="유효하지 않은 토큰입니다"
            )