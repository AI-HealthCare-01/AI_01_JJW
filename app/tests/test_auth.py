def test_test_login(client):
    response = client.post("/api/v1/auth/test-login")
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "user_info" in data
    assert data["user_info"]["user_id"] == "test_user_123"


def test_logout(client):
    response = client.post("/api/v1/auth/logout")
    assert response.status_code == 200
    assert response.json()["message"] == "로그아웃되었습니다"


def test_get_oauth_urls(client):
    response = client.get("/api/v1/auth/oauth/urls")
    assert response.status_code == 200
    data = response.json()
    assert "kakao_client_id" in data
    assert "naver_client_id" in data


def test_oauth_login_unsupported_provider(client):
    response = client.post(
        "/api/v1/auth/oauth/login",
        json={"provider": "google", "code": "test_code", "redirect_uri": "http://localhost/"},
    )
    assert response.status_code == 422


def test_get_me_without_token(client):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401


def test_get_me_with_invalid_token(client):
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalid_token"},
    )
    assert response.status_code == 401


def test_test_login_sets_cookie(client):
    response = client.post("/api/v1/auth/test-login")
    assert response.status_code == 200
    assert "access_token" in response.cookies


def test_get_me_with_test_token(client):
    login_resp = client.post("/api/v1/auth/test-login")
    token = login_resp.json()["access_token"]
    me_resp = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_resp.status_code == 200
    assert me_resp.json()["user_id"] == "test_user_123"
