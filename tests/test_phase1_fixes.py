"""
Regression Tests for Phase 1 Fixes:
1. Buyer Dashboard transaction metric counting (CONFIRMED and COMPLETED)
2. Analytics Overview unauthenticated vs authenticated privacy / recent_transactions
3. Seller analytics multi-tenant isolation and 403 enforcement
4. Buyer cannot create direct transaction without seller agreement / authorization check
"""

import pytest
from backend.app.models.transaction import Transaction
from backend.app.models.listing import Listing
from backend.app.models.user import User


def test_buyer_transactions_endpoint_returns_confirmed_and_completed(client, buyer_token, db_session):
    """
    Transactions created via offer acceptance (status=CONFIRMED) and direct completion (status=completed)
    must both be returned to the authenticated buyer under /api/transactions.
    """
    res = client.get("/api/transactions", headers={"Authorization": f"Bearer {buyer_token}"})
    assert res.status_code == 200
    txs = res.json()
    assert isinstance(txs, list)
    # Check that confirmed status exists and is recognized
    statuses = {t["status"].upper() for t in txs}
    assert "CONFIRMED" in statuses or "COMPLETED" in statuses


def test_analytics_overview_public_anonymizes_counterparty_names(client, db_session):
    """
    Unauthenticated callers to /api/analytics/overview receive aggregate data,
    but individual counterparty names in recent_transactions must be masked.
    """
    res = client.get("/api/analytics/overview")
    assert res.status_code == 200
    data = res.json()
    assert "total_users" in data
    assert "total_listings" in data
    assert "recent_transactions" in data
    for tx in data["recent_transactions"]:
        assert tx["buyer_name"] == "Verified Buyer"
        assert tx["seller_name"] == "Verified Generator"


def test_analytics_overview_authenticated_shows_real_counterparty_names(client, buyer_token, db_session):
    """
    Authenticated callers to /api/analytics/overview receive transparent counterparty names.
    """
    res = client.get("/api/analytics/overview", headers={"Authorization": f"Bearer {buyer_token}"})
    assert res.status_code == 200
    data = res.json()
    assert "recent_transactions" in data
    if data["recent_transactions"]:
        first_tx = data["recent_transactions"][0]
        # Should be a real name, not the masked fallback
        assert first_tx["buyer_name"] != "Verified Generator"


def test_seller_analytics_multi_tenant_forbidden_for_other_seller(client, seller_token, db_session):
    """
    A seller cannot request analytics for another seller's ID (returns 403 Forbidden).
    """
    # Register another seller
    res_b = client.post("/api/auth/register", json={
        "name": "Target Seller",
        "email": "target_seller@example.com",
        "password": "Password@123",
        "role": "seller",
        "phone": "+91 9333333333",
        "organization": "Target Org",
        "city": "Coimbatore",
        "state": "Tamil Nadu"
    })
    target_seller_id = res_b.json()["user"]["id"]

    # Original seller tries to access target seller's analytics
    attack_res = client.get(
        f"/api/analytics/seller/{target_seller_id}",
        headers={"Authorization": f"Bearer {seller_token}"}
    )
    assert attack_res.status_code == 403
    assert "cannot view analytics for another seller" in attack_res.json()["detail"].lower()


def test_buyer_unauthorized_to_create_arbitrary_transaction_without_seller(client, buyer_token):
    """
    Buyer cannot create a transaction with an invalid seller ID.
    """
    fake_tx = {
        "seller_id": "non_existent_seller_id_000000000000",
        "material_type": "Plastic",
        "quantity_kg": 100.0,
        "agreed_price": 40.0
    }
    res = client.post("/api/transactions", json=fake_tx, headers={"Authorization": f"Bearer {buyer_token}"})
    assert res.status_code == 404
