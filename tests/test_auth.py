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
        "phone": "+91 9999999991",
        "organization": "Duplicate Org",
        "city": "Coimbatore",
        "state": "Tamil Nadu",
    }
    res = client.post("/api/auth/register", json=payload)
    assert res.status_code == 409  # backend raises HTTP_409_CONFLICT
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


# ── Validation Error Handler Tests ────────────────────────────────────────────

def test_validation_error_missing_uppercase_returns_422(client):
    """
    A password without an uppercase letter must yield HTTP 422 (not 500)
    and a human-readable JSON response — not a raw Python exception object.
    """
    payload = {
        "name": "No Upper User",
        "email": "noupper@test.com",
        "password": "alllowercase1!",
        "role": "buyer",
        "phone": "+91 9000000001",
        "organization": "Test Org",
        "city": "Chennai",
        "state": "Tamil Nadu",
    }
    res = client.post("/api/auth/register", json=payload)
    assert res.status_code == 422
    data = res.json()
    # Must be JSON-serialisable (no Python exception objects in the response)
    assert isinstance(data, dict)
    assert data.get("success") is False
    # The readable message must mention the uppercase requirement
    msg = data.get("message", "")
    assert "uppercase" in msg.lower() or "invalid input" in msg.lower()
    # errors array must contain only safe scalar types
    for err in data.get("errors", []):
        assert isinstance(err.get("loc"), list)
        assert isinstance(err.get("msg"), str)
        assert isinstance(err.get("type"), str)


def test_validation_error_response_contains_no_raw_exception_objects(client):
    """
    The validation error response body must be fully JSON-serialisable;
    no Python ValueError / exception objects must leak to the client.
    """
    import json
    payload = {
        "name": "Bad",
        "email": "bad@test.com",
        "password": "nouppercase99",   # missing uppercase
        "role": "seller",
    }
    res = client.post("/api/auth/register", json=payload)
    assert res.status_code == 422
    # Confirm the raw bytes parse cleanly as JSON (no serialisation errors)
    parsed = json.loads(res.content)
    assert "success" in parsed


def test_valid_password_registration_succeeds(client):
    """
    A well-formed password with uppercase, digit, and special char
    must proceed past validation and register successfully.
    """
    payload = {
        "name": "Valid Password User",
        "email": "validpass@test.com",
        "password": "Secure@Pass1",
        "role": "buyer",
        "phone": "+91 9000000002",
        "organization": "Valid Org",
        "city": "Mumbai",
        "state": "Maharashtra",
    }
    res = client.post("/api/auth/register", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["user"]["email"] == "validpass@test.com"


def test_unauthenticated_request_rejected(client):
    """
    Logged-out user trying to access protected seller/buyer endpoints receives 401.
    """
    res1 = client.get("/api/auth/me")
    assert res1.status_code == 401

    res2 = client.get("/api/offers/seller/me")
    assert res2.status_code == 401

    res3 = client.get("/api/offers/buyer/me")
    assert res3.status_code == 401


def test_cross_role_access_prevented(client, seller_token, buyer_token):
    """
    Buyers cannot access seller-only endpoints, and sellers cannot access buyer-only endpoints.
    """
    # Buyer attempts seller-only offers
    res_buyer_on_seller = client.get(
        "/api/offers/seller/me",
        headers={"Authorization": f"Bearer {buyer_token}"}
    )
    assert res_buyer_on_seller.status_code == 403

    # Seller attempts buyer-only offers
    res_seller_on_buyer = client.get(
        "/api/offers/buyer/me",
        headers={"Authorization": f"Bearer {seller_token}"}
    )
    assert res_seller_on_buyer.status_code == 403


def test_jwt_secret_validation_rejects_missing_or_insecure():
    """
    Tests that validate_jwt_secret raises RuntimeError for missing, empty,
    known development defaults, or short keys (< 32 characters).
    """
    from backend.app.config import validate_jwt_secret

    # Empty or missing
    with pytest.raises(RuntimeError, match="missing or empty"):
        validate_jwt_secret("")
    with pytest.raises(RuntimeError, match="missing or empty"):
        validate_jwt_secret("   ")

    # Known insecure defaults
    with pytest.raises(RuntimeError, match="Insecure default JWT_SECRET detected"):
        validate_jwt_secret("circular_economy_dev_secret_change_in_production_2026")
    with pytest.raises(RuntimeError, match="Insecure default JWT_SECRET detected"):
        validate_jwt_secret("secret")

    # Too short (<32 chars)
    with pytest.raises(RuntimeError, match="at least 32 characters"):
        validate_jwt_secret("short_key_1234567890")

    # Valid cryptographically strong secret succeeds without error
    validate_jwt_secret("a_very_strong_random_secret_with_more_than_32_characters_2026")

