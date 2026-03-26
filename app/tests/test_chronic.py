from unittest.mock import AsyncMock, patch


def test_chronic_disease_info(client):
    response = client.get("/api/v1/chronic/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "만성질환 예측 서비스"
    assert data["features"] == 80
    assert len(data["diseases"]) == 4


def test_get_task_not_found(client, mock_redis):
    mock_redis.hgetall = AsyncMock(return_value={})
    with patch("app.apis.v1.chronic.get_redis", AsyncMock(return_value=mock_redis)):
        response = client.get("/api/v1/chronic/task/nonexistent-task-id")
    assert response.status_code == 404


def test_get_task_found(client, mock_redis):
    mock_redis.hgetall = AsyncMock(return_value={
        "task_id": "test-task-123",
        "status": "completed",
        "created_at": "2025-01-01T00:00:00",
        "completed_at": "2025-01-01T00:00:01",
        "result": '{"DJ8_pre": 0, "DI1_pre": 1, "DE1_pre": 0, "DI2_pre": 0}',
        "error": "",
    })
    with patch("app.apis.v1.chronic.get_redis", AsyncMock(return_value=mock_redis)):
        response = client.get("/api/v1/chronic/task/test-task-123")
    assert response.status_code == 200
    data = response.json()
    assert data["task_id"] == "test-task-123"
    assert data["status"] == "completed"
