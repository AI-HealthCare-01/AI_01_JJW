from fastapi import APIRouter

from app.apis.v1.health import health_router

v1_routers = APIRouter()
v1_routers.include_router(health_router, prefix="/health", tags=["health"])