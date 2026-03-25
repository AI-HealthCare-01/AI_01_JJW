import os
from enum import StrEnum
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Env(StrEnum):
    LOCAL = "local"
    DEV = "dev"
    PROD = "prod"


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="allow")

    ENV: Env = Env.LOCAL

    # Redis 설정
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    # 빌드된 SPA 파일 디렉토리 (vite build → ../static)
    STATIC_DIR: str = os.path.join(Path(__file__).resolve().parent.parent.parent, "static")

    # Task TTL 설정 (초)
    TASK_RESULT_TTL: int = 3600

    # OAuth 설정
    KAKAO_CLIENT_ID: str = "your_kakao_client_id"
    KAKAO_CLIENT_SECRET: str = "your_kakao_client_secret"
    NAVER_CLIENT_ID: str = "your_naver_client_id"
    NAVER_CLIENT_SECRET: str = "your_naver_client_secret"

    # JWT 설정
    JWT_SECRET: str = "your-super-secret-jwt-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"

    # CORS 설정
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173", "http://localhost:8000", "http://localhost"]


config = Config()
