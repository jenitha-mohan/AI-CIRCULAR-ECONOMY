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
    from backend.app.models.user import User
    seller = db_session.query(User).filter(User.email == "seller@ecotextiles.com").first()
    listing = db_session.query(Listing).filter(Listing.seller_id == seller.id, Listing.status == "active").first()
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


def test_offers_isolated_between_different_sellers(client, buyer_token, seller_token, db_session):
    """
    Offers made to Seller A must NOT appear in Seller B's offers list.
    """
    from backend.app.models.user import User
    from backend.app.models.material import Material

    # Create another seller
    seller_b_reg = client.post("/api/auth/register", json={
        "name": "Different Seller",
        "email": "seller_b_unique@test.com",
        "password": "Password@123",
        "role": "seller",
        "phone": "+91 9111111111",
        "organization": "Seller B Org",
        "city": "Chennai",
        "state": "Tamil Nadu"
    })
    seller_b_token = seller_b_reg.json()["access_token"]
    seller_b_id = seller_b_reg.json()["user"]["id"]

    # Listing belongs to original seller (seller@ecotextiles.com)
    seller_a = db_session.query(User).filter(User.email == "seller@ecotextiles.com").first()
    listing_a = db_session.query(Listing).filter(Listing.seller_id == seller_a.id, Listing.status == "active").first()
    assert listing_a is not None

    # Buyer creates offer on Listing A
    create_res = client.post("/api/offers", json={
        "listing_id": listing_a.id,
        "offered_quantity": 25.0,
        "offered_price": 185.0,
        "message": "Offer for seller A only"
    }, headers={"Authorization": f"Bearer {buyer_token}"})
    assert create_res.status_code == 201
    offer_id = create_res.json()["id"]

    # Seller A sees this offer
    res_a = client.get("/api/offers/seller/me", headers={"Authorization": f"Bearer {seller_token}"})
    assert res_a.status_code == 200
    assert any(o["id"] == offer_id for o in res_a.json())

    # Seller B does NOT see this offer
    res_b = client.get("/api/offers/seller/me", headers={"Authorization": f"Bearer {seller_b_token}"})
    assert res_b.status_code == 200
    assert not any(o["id"] == offer_id for o in res_b.json())


def test_seller_counter_offer_and_buyer_acceptance(client, buyer_token, seller_token, db_session):
    """
    Test full buyer-acceptance flow:
    1. Buyer places offer.
    2. Seller counters the offer.
    3. Verify offer history shows sender_id is the seller.
    4. Buyer accepts the seller's counter-offer.
    5. Verify transaction is confirmed and offer is ACCEPTED.
    """
    from backend.app.models.user import User

    seller = db_session.query(User).filter(User.email == "seller@ecotextiles.com").first()
    listing = db_session.query(Listing).filter(Listing.seller_id == seller.id, Listing.status == "active").first()
    assert listing is not None

    # Step 1: Buyer creates offer at 170.0
    create_res = client.post("/api/offers", json={
        "listing_id": listing.id,
        "offered_quantity": 30.0,
        "offered_price": 170.0,
        "message": "Initial buyer bid"
    }, headers={"Authorization": f"Bearer {buyer_token}"})
    assert create_res.status_code == 201
    offer_id = create_res.json()["id"]

    # Step 2: Seller counters at 180.0
    counter_res = client.post(f"/api/offers/{offer_id}/counter", json={
        "counter_price": 180.0,
        "counter_quantity": 30.0,
        "message": "Seller counter proposal at 180/kg"
    }, headers={"Authorization": f"Bearer {seller_token}"})
    assert counter_res.status_code == 200
    assert counter_res.json()["status"] == "COUNTERED"
    assert counter_res.json()["offered_price"] == 180.0

    # Step 3: Verify history shows last entry was sent by seller
    hist_res = client.get(f"/api/offers/{offer_id}/history", headers={"Authorization": f"Bearer {buyer_token}"})
    assert hist_res.status_code == 200
    history = hist_res.json()
    assert len(history) == 2
    last_step = history[-1]
    assert last_step["action"] == "COUNTER"
    assert last_step["price"] == 180.0
    assert last_step["sender_id"] == seller.id

    # Step 4: Unauthorized user (another seller) cannot accept this offer
    other_seller_reg = client.post("/api/auth/register", json={
        "name": "Unauthorized Third Party",
        "email": "thirdparty@test.com",
        "password": "Password@123",
        "role": "seller",
        "phone": "+91 9222222222",
        "organization": "Third Party Org",
        "city": "Chennai",
        "state": "Tamil Nadu"
    })
    third_token = other_seller_reg.json()["access_token"]
    unauth_accept = client.post(f"/api/offers/{offer_id}/accept", headers={"Authorization": f"Bearer {third_token}"})
    assert unauth_accept.status_code == 403

    # Step 5: Buyer accepts the seller's counter-offer
    accept_res = client.post(f"/api/offers/{offer_id}/accept", headers={"Authorization": f"Bearer {buyer_token}"})
    assert accept_res.status_code == 200
    data = accept_res.json()
    assert data["success"] is True
    assert data["offer"]["status"] == "ACCEPTED"
    assert data["offer"]["agreed_price"] == 180.0
    assert data["transaction"]["status"] == "CONFIRMED"
    assert data["transaction"]["agreed_price"] == 180.0
    assert data["transaction"]["quantity_kg"] == 30.0

