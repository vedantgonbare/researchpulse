# tests/test_auth.py

def test_register_success(client):
    """New user can register."""
    response = client.post("/auth/register", json={
        "email": "newuser@test.com",
        "username": "newuser",
        "password": "password123"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "newuser@test.com"
    assert data["username"] == "newuser"
    assert "id" in data
    assert "hashed_password" not in data  # Never expose password

def test_register_duplicate_email(client):
    """Duplicate email returns 400."""
    client.post("/auth/register", json={
        "email": "duplicate@test.com",
        "username": "user1",
        "password": "pass123"
    })
    response = client.post("/auth/register", json={
        "email": "duplicate@test.com",
        "username": "user2",
        "password": "pass123"
    })
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]

def test_login_success(client):
    """Valid credentials return JWT token."""
    client.post("/auth/register", json={
        "email": "logintest@test.com",
        "username": "loginuser",
        "password": "pass123"
    })
    response = client.post("/auth/login", json={
        "email": "logintest@test.com",
        "password": "pass123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password(client):
    """Wrong password returns 401."""
    client.post("/auth/register", json={
        "email": "wrongpass@test.com",
        "username": "wrongpassuser",
        "password": "correctpass"
    })
    response = client.post("/auth/login", json={
        "email": "wrongpass@test.com",
        "password": "wrongpass"
    })
    assert response.status_code == 401

def test_get_me_authenticated(client, auth_headers):
    """Authenticated user can get their profile."""
    response = client.get("/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "email" in data
    assert "id" in data

def test_get_me_unauthenticated(client):
    """Unauthenticated request returns 401."""
    response = client.get("/auth/me")
    assert response.status_code == 401