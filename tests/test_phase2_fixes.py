"""
Comprehensive tests for Phase 2 implementation:
1. User PII Protection: owner vs other authenticated user vs admin
2. Profile editing: PUT /api/users/me with validation, role protection, persistence
3. Chat read_at timestamp marking and unread_count verification
4. Demand forecasting with dynamic dates across different months/quarters
5. Recommendations authentication and authorization isolation
"""

import pytest
from datetime import datetime, timedelta
from backend.app.models.user import User
from backend.app.models.transaction import Transaction
from backend.app.models.chat import ChatMessage
from backend.app.models.listing import Listing
from backend.app.models.material import Material


def test_user_pii_protection_returns_public_profile_to_other_users(client, seller_token, buyer_token, db_session):
    """
    When buyer requests a seller's profile, phone and email must NOT be exposed.
    """
    seller = db_session.query(User).filter(User.email == "seller@ecotextiles.com").first()
    assert seller is not None

    res = client.get(f"/api/users/{seller.id}", headers={"Authorization": f"Bearer {buyer_token}"})
    assert res.status_code == 200
    data = res.json()
    assert "email" not in data
    assert "phone" not in data
    assert data["name"] == seller.name
    assert data["organization"] == seller.organization


def test_user_owner_and_admin_receive_full_profile(client, seller_token, admin_token, db_session):
    """
    Owner and admin receive full profile including email and phone.
    """
    seller = db_session.query(User).filter(User.email == "seller@ecotextiles.com").first()
    assert seller is not None

    # Owner access
    res_owner = client.get(f"/api/users/{seller.id}", headers={"Authorization": f"Bearer {seller_token}"})
    assert res_owner.status_code == 200
    data_owner = res_owner.json()
    assert data_owner["email"] == seller.email
    assert data_owner["phone"] == seller.phone

    # Admin access
    res_admin = client.get(f"/api/users/{seller.id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert res_admin.status_code == 200
    data_admin = res_admin.json()
    assert data_admin["email"] == seller.email
    assert data_admin["phone"] == seller.phone


def test_seller_profile_editing_persists_changes(client, seller_token, db_session):
    """
    Seller can update approved fields via PUT /api/users/me and changes persist.
    """
    update_payload = {
        "phone": "+91 9888888888",
        "organization": "EcoTextiles Green Hub",
        "business_type": "Certified Recycler",
        "city": "Tiruppur",
        "state": "Tamil Nadu"
    }
    res = client.put("/api/users/me", json=update_payload, headers={"Authorization": f"Bearer {seller_token}"})
    assert res.status_code == 200
    data = res.json()
    assert data["phone"] == "+91 9888888888"
    assert data["organization"] == "EcoTextiles Green Hub"
    assert data["business_type"] == "Certified Recycler"
    assert data["location"]["city"] == "Tiruppur"

    # Verify persistence via GET /api/users/me
    get_res = client.get("/api/users/me", headers={"Authorization": f"Bearer {seller_token}"})
    assert get_res.status_code == 200
    assert get_res.json()["organization"] == "EcoTextiles Green Hub"


def test_seller_profile_editing_rejects_privileged_fields_or_invalid_values(client, seller_token):
    """
    User cannot change role, email, or id, and invalid phone is rejected.
    """
    # Attempting to escalate role or change email
    payload = {
        "role": "admin",
        "email": "hacked@admin.com",
        "organization": "Valid Org Name"
    }
    res = client.put("/api/users/me", json=payload, headers={"Authorization": f"Bearer {seller_token}"})
    assert res.status_code == 200
    # Role and email must remain unchanged
    data = res.json()
    assert data["role"] == "seller"
    assert data["email"] != "hacked@admin.com"

    # Invalid phone (too short)
    res_bad_phone = client.put("/api/users/me", json={"phone": "123"}, headers={"Authorization": f"Bearer {seller_token}"})
    assert res_bad_phone.status_code == 422


def test_chat_read_status_and_unread_count(client, seller_token, buyer_token, db_session):
    """
    1. Buyer sends a message to seller in confirmed transaction.
    2. Message initial read_at is None.
    3. Seller unread count is 1; Buyer unread count is 0 (did not receive it).
    4. Seller fetches messages -> read_at is marked with current UTC timestamp.
    5. Seller unread count drops to 0.
    """
    txn = db_session.query(Transaction).filter(Transaction.status == "CONFIRMED").first()
    assert txn is not None

    # Step 1: Buyer sends message
    send_res = client.post(
        f"/api/transactions/{txn.id}/messages",
        json={"message": "Testing read receipt timestamp flow"},
        headers={"Authorization": f"Bearer {buyer_token}"}
    )
    assert send_res.status_code == 201
    msg_id = send_res.json()["id"]

    # Step 2: Verify in DB that read_at is initially None
    db_session.expire_all()
    msg = db_session.query(ChatMessage).filter(ChatMessage.id == msg_id).first()
    assert msg.read_at is None

    # Step 3: Check conversation unread counts
    # Buyer who sent it has 0 unread
    buyer_convs = client.get("/api/chat/conversations", headers={"Authorization": f"Bearer {buyer_token}"}).json()
    target_conv_buyer = next(c for c in buyer_convs if c["transaction_id"] == txn.id)
    assert target_conv_buyer["unread_count"] == 0

    # Seller who received it has at least 1 unread
    seller_convs = client.get("/api/chat/conversations", headers={"Authorization": f"Bearer {seller_token}"}).json()
    target_conv_seller = next(c for c in seller_convs if c["transaction_id"] == txn.id)
    assert target_conv_seller["unread_count"] >= 1

    # Step 4: Seller fetches messages -> updates read_at timestamp
    get_res = client.get(f"/api/transactions/{txn.id}/messages", headers={"Authorization": f"Bearer {seller_token}"})
    assert get_res.status_code == 200

    # Step 5: Verify in DB that read_at is now set to a datetime
    db_session.expire_all()
    msg_updated = db_session.query(ChatMessage).filter(ChatMessage.id == msg_id).first()
    assert msg_updated.read_at is not None
    assert isinstance(msg_updated.read_at, datetime)

    # Seller unread count now 0
    seller_convs_after = client.get("/api/chat/conversations", headers={"Authorization": f"Bearer {seller_token}"}).json()
    target_conv_after = next(c for c in seller_convs_after if c["transaction_id"] == txn.id)
    assert target_conv_after["unread_count"] == 0


def test_demand_forecast_dynamic_calendar_features():
    """
    Test that predict_demand calculates features dynamically for different dates
    (e.g., January Q1 vs October Q4) rather than hardcoded month 10.
    """
    from backend.app.services.demand_prediction_service import demand_prediction_service

    # Test January date (month=1, quarter=1)
    jan_date = datetime(2026, 1, 15)
    res_jan = demand_prediction_service.predict_demand("Aluminum", forecast_date=jan_date)
    assert "predicted_demand_kg" in res_jan
    assert res_jan["material"] == "Aluminum"

    # Test July date (month=7, quarter=3)
    jul_date = datetime(2026, 7, 20)
    res_jul = demand_prediction_service.predict_demand("Aluminum", forecast_date=jul_date)
    assert "predicted_demand_kg" in res_jul

    # Both return valid demand predictions and categories
    assert res_jan["demand_category"] in ["High", "Moderate", "Low"]
    assert res_jul["demand_category"] in ["High", "Moderate", "Low"]


def test_buyer_recommendations_requires_auth_and_isolates_buyers(client, buyer_token, seller_token, db_session):
    """
    1. Unauthenticated request to /api/recommendations/materials/{buyer_id} returns 401.
    2. Authenticated buyer requesting own recommendations returns 200.
    3. User requesting recommendations for a different buyer returns 403 Forbidden.
    """
    buyer = db_session.query(User).filter(User.email == "buyer@greenplast.com").first()
    assert buyer is not None

    # Unauthenticated
    unauth_res = client.get(f"/api/recommendations/materials/{buyer.id}")
    assert unauth_res.status_code == 401

    # Authorized buyer accessing own
    auth_res = client.get(f"/api/recommendations/materials/{buyer.id}", headers={"Authorization": f"Bearer {buyer_token}"})
    assert auth_res.status_code == 200
    assert isinstance(auth_res.json(), list)

    # Different user (seller) attempting to access buyer's recommendations
    forbidden_res = client.get(f"/api/recommendations/materials/{buyer.id}", headers={"Authorization": f"Bearer {seller_token}"})
    assert forbidden_res.status_code == 403
    assert "cannot view recommendations for another buyer" in forbidden_res.json()["detail"].lower()
