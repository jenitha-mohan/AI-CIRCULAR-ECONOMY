import pytest


def test_root_status(client):
    res = client.get("/")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "operational"
    assert "docs" in data


def test_register_seller(client):
    payload = {
        "name": "Test Seller Company",
        "email": "newseller@test.com",
        "password": "Password@123",
        "role": "seller",
        "phone": "+91 9999999991",
        "organization": "Test Seller Org",
        "city": "Coimbatore",
        "state": "Tamil Nadu",
    }
    res = client.post("/api/auth/register", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["user"]["email"] == "newseller@test.com"
    assert data["user"]["role"] == "seller"


def test_register_duplicate_email(client):
    payload = {
        "name": "Duplicate Seller",
        "email": "newseller@test.com",
        "password": "Password@123",
        "role": "seller",
    }
    res = client.post("/api/auth/register", json=payload)
    assert res.status_code == 400
    assert "already exists" in res.json()["message"]


def test_login_success(client):
    payload = {
        "email": "newseller@test.com",
        "password": "Password@123",
    }
    res = client.post("/api/auth/login", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["user"]["email"] == "newseller@test.com"


def test_login_invalid_credentials(client):
    payload = {
        "email": "newseller@test.com",
        "password": "WrongPassword!1",
    }
    res = client.post("/api/auth/login", json=payload)
    assert res.status_code == 401


def test_auth_me_valid_token(client, seller_token):
    headers = {"Authorization": f"Bearer {seller_token}"}
    res = client.get("/api/auth/me", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["role"] == "seller"
    assert "password_hash" not in data


def test_auth_me_invalid_token(client):
    headers = {"Authorization": "Bearer invalid.token.value"}
    res = client.get("/api/auth/me", headers=headers)
    assert res.status_code == 401


def test_role_authorization_seller_forbidden_on_admin(client, seller_token):
    headers = {"Authorization": f"Bearer {seller_token}"}
    # Attempting an admin-only endpoint: GET /api/users
    res = client.get("/api/users", headers=headers)
    assert res.status_code == 403


def test_role_authorization_admin_allowed(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    res = client.get("/api/users", headers=headers)
    assert res.status_code == 200
    users = res.json()
    assert isinstance(users, list)
    assert len(users) >= 1
