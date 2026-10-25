"""Тесты авторизации: регистрация, логин, /me."""


def test_register_success(client):
    res = client.post(
        "/api/v1/auth/register",
        json={"email": "new@test.com", "password": "password123"},
    )
    assert res.status_code == 201
    data = res.json()
    assert data["email"] == "new@test.com"
    assert "id" in data
    assert "password" not in data
    assert "hashed_password" not in data


def test_register_duplicate_email(client):
    payload = {"email": "dup@test.com", "password": "password123"}
    first = client.post("/api/v1/auth/register", json=payload)
    assert first.status_code == 201

    second = client.post("/api/v1/auth/register", json=payload)
    assert second.status_code == 409


def test_register_short_password(client):
    res = client.post(
        "/api/v1/auth/register",
        json={"email": "short@test.com", "password": "short"},
    )
    assert res.status_code == 422


def test_register_invalid_email(client):
    res = client.post(
        "/api/v1/auth/register",
        json={"email": "not-an-email", "password": "password123"},
    )
    assert res.status_code == 422


def test_login_success(client):
    client.post(
        "/api/v1/auth/register",
        json={"email": "login@test.com", "password": "password123"},
    )
    res = client.post(
        "/api/v1/auth/login",
        data={"username": "login@test.com", "password": "password123"},
    )
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client):
    client.post(
        "/api/v1/auth/register",
        json={"email": "wrong@test.com", "password": "password123"},
    )
    res = client.post(
        "/api/v1/auth/login",
        data={"username": "wrong@test.com", "password": "wrong"},
    )
    assert res.status_code == 401


def test_login_unknown_email(client):
    res = client.post(
        "/api/v1/auth/login",
        data={"username": "ghost@test.com", "password": "password123"},
    )
    assert res.status_code == 401


def test_me_with_token(client, registered_user):
    res = client.get("/api/v1/auth/me", headers=registered_user["headers"])
    assert res.status_code == 200
    data = res.json()
    assert data["email"] == registered_user["email"]
    assert data["id"] == registered_user["user"]["id"]


def test_me_without_token(client):
    res = client.get("/api/v1/auth/me")
    assert res.status_code == 401


def test_me_with_invalid_token(client):
    res = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalid.token.here"},
    )
    assert res.status_code == 401