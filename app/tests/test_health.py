from unittest.mock import AsyncMock, MagicMock, patch


def test_health_check(client):
    response = client.get("/api/v1/health/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "AI Healthcare API"


def test_redis_health_check_ok(client, mock_redis):
    with patch("app.apis.v1.health.get_redis", AsyncMock(return_value=mock_redis)):
        response = client.get("/api/v1/health/redis")
    assert response.status_code == 200
    assert response.json()["redis_status"] == "connected"


def test_redis_health_check_fail(client):
    failing_redis = MagicMock()
    failing_redis.ping = AsyncMock(side_effect=ConnectionError("Redis 연결 실패"))
    with patch("app.apis.v1.health.get_redis", AsyncMock(return_value=failing_redis)):
        response = client.get("/api/v1/health/redis")
    assert response.status_code == 503
