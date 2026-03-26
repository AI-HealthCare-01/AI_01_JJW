from fastapi import APIRouter, HTTPException, status
from fastapi.responses import ORJSONResponse

from app.db.databases import get_redis

health_router = APIRouter()


@health_router.get("/")
async def health_check():
    return ORJSONResponse(content={"status": "healthy", "service": "AI Healthcare API", "version": "1.0.0"})


@health_router.get("/redis")
async def redis_health_check():
    try:
        redis_client = await get_redis()
        await redis_client.ping()
        return ORJSONResponse(content={"redis_status": "connected", "message": "Redis 연결 정상"})
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Redis 연결 실패: {e!s}",
        ) from e
