"""
Tests for Offer & Negotiation System
Validates offer creation, validation rules, multi-round counter-offers,
negotiation history audit trails, inventory control, and deal acceptance.
"""

import pytest
from backend.app.models.listing import Listing
from backend.app.models.material import Material
from backend.app.models.offer import Offer, OfferHistory
from backend.app.models.transaction import Transaction


def test_create_offer_success(client, buyer_token, db_session):
    # Find an active listing
    listing = db_session.query(Listing).filter(Listing.status == "active").first()
    assert listing is not None

    payload = {
        "listing_id": listing.id,
        "offered_quantity": 50.0,
        "offered_price": 185.0,
        "message": "Interested in procurement of 50 kg batch."
    }

    res = client.post("/api/offers", json=payload, headers={"Authorization": f"Bearer {buyer_token}"})
    assert res.status_code == 201
    data = res.json()
    assert data["status"] == "PENDING"
    assert data["offered_price"] == 185.0
    assert data["offered_quantity"] == 50.0
    assert data["listing_id"] == listing.id


def test_create_offer_seller_cannot_offer_own_listing(client, seller_token, db_session):
    # Seller tries to submit offer on their own listing
    listing = db_session.query(Listing).filter(Listing.status == "active").first()
    assert listing is not None

    payload = {
        "listing_id": listing.id,
        "offered_quantity": 20.0,
        "offered_price": 100.0,
        "message": "Attempting invalid self-offer"
    }

    res = client.post("/api/offers", json=payload, headers={"Authorization": f"Bearer {seller_token}"})
    # Must be forbidden or bad request
    assert res.status_code in [400, 403]


def test_create_offer_invalid_quantity_or_price(client, buyer_token, db_session):
    listing = db_session.query(Listing).filter(Listing.status == "active").first()
    assert listing is not None

    # Negative price
    res1 = client.post("/api/offers", json={
        "listing_id": listing.id,
        "offered_quantity": 50.0,
        "offered_price": -10.0,
        "message": "Negative price"
    }, headers={"Authorization": f"Bearer {buyer_token}"})
    assert res1.status_code == 422

    # Zero quantity
    res2 = client.post("/api/offers", json={
        "listing_id": listing.id,
        "offered_quantity": 0.0,
        "offered_price": 50.0,
        "message": "Zero quantity"
    }, headers={"Authorization": f"Bearer {buyer_token}"})
    assert res2.status_code == 422

    # Exceeding quantity available
    res3 = client.post("/api/offers", json={
        "listing_id": listing.id,
        "offered_quantity": 9999999.0,
        "offered_price": 50.0,
        "message": "Excessive quantity"
    }, headers={"Authorization": f"Bearer {buyer_token}"})
    assert res3.status_code in [400, 422]


def test_multi_round_negotiation_and_acceptance(client, buyer_token, seller_token, db_session):
    listing = db_session.query(Listing).filter(Listing.status == "active").first()
    initial_qty = listing.quantity_available
    trade_qty = 100.0

    # Step 1: Buyer creates Offer at ₹185/kg
    create_res = client.post("/api/offers", json={
        "listing_id": listing.id,
        "offered_quantity": trade_qty,
        "offered_price": 185.0,
        "message": "Initial buyer offer at 185"
    }, headers={"Authorization": f"Bearer {buyer_token}"})
    assert create_res.status_code == 201
    offer_id = create_res.json()["id"]

    # Step 2: Seller counters at ₹195/kg
    counter1 = client.post(f"/api/offers/{offer_id}/counter", json={
        "counter_price": 195.0,
        "counter_quantity": trade_qty,
        "message": "Seller counter offer: Can provide for 195/kg."
    }, headers={"Authorization": f"Bearer {seller_token}"})
    assert counter1.status_code == 200
    assert counter1.json()["status"] == "COUNTERED"
    assert counter1.json()["offered_price"] == 195.0

    # Step 3: Buyer counters at ₹190/kg
    counter2 = client.post(f"/api/offers/{offer_id}/counter", json={
        "counter_price": 190.0,
        "counter_quantity": trade_qty,
        "message": "Buyer final counter: Best I can do is 190/kg."
    }, headers={"Authorization": f"Bearer {buyer_token}"})
    assert counter2.status_code == 200
    assert counter2.json()["offered_price"] == 190.0

    # Step 4: Verify negotiation history audit trail has 3 chronological steps
    history_res = client.get(f"/api/offers/{offer_id}/history", headers={"Authorization": f"Bearer {seller_token}"})
    assert history_res.status_code == 200
    history = history_res.json()
    assert len(history) == 3
    assert history[0]["action"] == "OFFER" and history[0]["price"] == 185.0
    assert history[1]["action"] == "COUNTER" and history[1]["price"] == 195.0
    assert history[2]["action"] == "COUNTER" and history[2]["price"] == 190.0

    # Step 5: Seller accepts offer at ₹190/kg
    accept_res = client.post(f"/api/offers/{offer_id}/accept", headers={"Authorization": f"Bearer {seller_token}"})
    assert accept_res.status_code == 200
    accept_data = accept_res.json()
    assert accept_data["success"] is True
    assert accept_data["offer"]["status"] == "ACCEPTED"
    assert accept_data["offer"]["agreed_price"] == 190.0

    # Step 6: Verify Transaction details
    txn = accept_data["transaction"]
    assert txn["agreed_price"] == 190.0
    assert txn["quantity_kg"] == trade_qty
    assert txn["total_amount"] == 190.0 * trade_qty
    assert txn["status"] == "CONFIRMED"

    # Step 7: Verify Listing inventory was decremented
    db_session.expire_all()
    updated_listing = db_session.query(Listing).filter(Listing.id == listing.id).first()
    assert updated_listing.quantity_available == initial_qty - trade_qty
