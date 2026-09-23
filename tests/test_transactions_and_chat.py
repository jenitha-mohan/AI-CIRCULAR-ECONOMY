"""
Tests for Transaction Lifecycle, Pickup Scheduling, and In-Platform Chat
"""

import pytest
from datetime import datetime, timedelta
from backend.app.models.transaction import Transaction
from backend.app.models.listing import Listing


def test_transaction_lifecycle_and_pickup_flow(client, seller_token, buyer_token, db_session):
    # 1. Fetch transaction between test seller and buyer
    txn = db_session.query(Transaction).filter(
        Transaction.seller.has(email="seller@ecotextiles.com"),
        Transaction.buyer.has(email="buyer@greenplast.com")
    ).first()
    if not txn:
        txn = db_session.query(Transaction).first()
    assert txn is not None

    # 2. Seller schedules pickup
    pickup_date = (datetime.utcnow() + timedelta(days=2)).isoformat()
    sched_res = client.post(f"/api/transactions/{txn.id}/schedule-pickup", json={
        "pickup_location": "Coimbatore Warehouse Hub 4, Industrial Area",
        "pickup_date": pickup_date,
        "pickup_instructions": "Gate 2 entry. Bring heavy transport vehicle."
    }, headers={"Authorization": f"Bearer {seller_token}"})
    assert sched_res.status_code == 200
    sched_data = sched_res.json()
    assert sched_data["status"] == "PICKUP_SCHEDULED"
    assert "Warehouse Hub 4" in sched_data["pickup_location"]

    # 3. Update status to IN_TRANSIT
    status_res = client.post(f"/api/transactions/{txn.id}/update-status", json={
        "status": "IN_TRANSIT"
    }, headers={"Authorization": f"Bearer {seller_token}"})
    assert status_res.status_code == 200
    assert status_res.json()["status"] == "IN_TRANSIT"

    # 4. Mark transaction COMPLETED (buyer confirms receipt)
    complete_res = client.post(f"/api/transactions/{txn.id}/complete", headers={"Authorization": f"Bearer {buyer_token}"})
    assert complete_res.status_code == 200
    assert complete_res.json()["status"] == "COMPLETED"


def test_chat_messaging_participants(client, seller_token, buyer_token, db_session):
    txn = db_session.query(Transaction).filter(
        Transaction.seller.has(email="seller@ecotextiles.com"),
        Transaction.buyer.has(email="buyer@greenplast.com")
    ).first()
    if not txn:
        txn = db_session.query(Transaction).first()
    assert txn is not None

    # Step 1: Seller sends chat message
    msg1_res = client.post(f"/api/transactions/{txn.id}/messages", json={
        "message": "When can you arrange pickup?"
    }, headers={"Authorization": f"Bearer {seller_token}"})
    assert msg1_res.status_code == 201
    assert msg1_res.json()["message"] == "When can you arrange pickup?"

    # Step 2: Buyer sends reply message
    msg2_res = client.post(f"/api/transactions/{txn.id}/messages", json={
        "message": "Our vehicle will come tomorrow at 10 AM."
    }, headers={"Authorization": f"Bearer {buyer_token}"})
    assert msg2_res.status_code == 201
    assert msg2_res.json()["message"] == "Our vehicle will come tomorrow at 10 AM."

    # Step 3: Retrieve messages list
    list_res = client.get(f"/api/transactions/{txn.id}/messages", headers={"Authorization": f"Bearer {buyer_token}"})

    assert list_res.status_code == 200
    messages = list_res.json()
    assert len(messages) >= 2
    assert any("arrange pickup" in m["message"] for m in messages)
    assert any("tomorrow at 10 AM" in m["message"] for m in messages)


def test_chat_conversations_list(client, buyer_token):
    res = client.get("/api/chat/conversations", headers={"Authorization": f"Bearer {buyer_token}"})
    assert res.status_code == 200
    convs = res.json()
    assert isinstance(convs, list)
