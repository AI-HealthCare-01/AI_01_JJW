from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from app.db.databases import get_redis
from app.main import app


@pytest.fixture
def mock_redis():
    redis = MagicMock()
    redis.ping = AsyncMock(return_value=True)
    redis.hset = AsyncMock(return_value=True)
    redis.expire = AsyncMock(return_value=True)
    redis.lpush = AsyncMock(return_value=1)
    redis.hgetall = AsyncMock(return_value={})
    return redis


@pytest.fixture
def client(mock_redis):
    app.dependency_overrides[get_redis] = AsyncMock(return_value=mock_redis)
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c
    app.dependency_overrides.clear()
