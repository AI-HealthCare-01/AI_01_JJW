from fastapi import APIRouter

from app.apis.v1.auth import auth_router
from app.apis.v1.chronic import chronic_router
from app.apis.v1.health import health_router

v1_routers = APIRouter()
v1_routers.include_router(auth_router, prefix="/auth", tags=["authentication"])
v1_routers.include_router(chronic_router, prefix="/chronic", tags=["chronic-disease"])
v1_routers.include_router(health_router, prefix="/health", tags=["health"])
