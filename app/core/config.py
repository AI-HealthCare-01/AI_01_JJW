import os
from pathlib import Path
from enum import StrEnum

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
    
    # Static Files 설정
    STATIC_DIR: str = os.path.join(Path(__file__).resolve().parent.parent.parent, "src")
    
    # Task TTL 설정 (초)
    TASK_RESULT_TTL: int = 3600  # 1시간


config = Config()