import redis.asyncio as redis
from app.core.config import config

# Redis 연결 풀
redis_pool = None


async def get_redis() -> redis.Redis:
    """Redis 연결 반환"""
    global redis_pool
    if redis_pool is None:
        redis_pool = redis.ConnectionPool(
            host=config.REDIS_HOST,
            port=config.REDIS_PORT,
            db=config.REDIS_DB,
            decode_responses=True
        )
    return redis.Redis(connection_pool=redis_pool)


async def close_redis():
    """Redis 연결 종료"""
    global redis_pool
    if redis_pool:
        await redis_pool.disconnect()
        redis_pool = None