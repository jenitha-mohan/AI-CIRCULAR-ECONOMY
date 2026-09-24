"""
End-to-End Real-World Scenario Test & Price Separation Verification
Implements the exact 23-step circular marketplace journey specified in Project Objective & Section 46/47:
- Seller (XYZ Manufacturing) & Buyer (ABC Recycling) Registration & Login
- AI Identification & Price Range Guidance (₹180–₹195/kg)
- Seller Manual Asking Price Decision (₹200/kg)
- Buyer Offer (₹185/kg) -> Seller Counter (₹195/kg) -> Buyer Counter (₹190/kg) -> Seller Accept
- Deal Confirmation & Transaction Creation at Agreed Price ₹190/kg (Total ₹95,000)
- In-Platform Chat Messaging, Pickup Scheduling, and Deal Completion
- Strict Verification of Price Separation (AI Estimates vs Asking Price vs Agreed Price)
"""

import pytest


def test_complete_e2e_marketplace_journey_and_price_separation(client, db_session):
    # STEP 1: Register Seller (XYZ Manufacturing, Coimbatore)
    seller_reg = client.post("/api/auth/register", json={
        "name": "XYZ Manufacturing",
        "email": "seller_xyz@manufacturing.com",
        "password": "Password@123",
        "role": "seller",
        "organization": "XYZ Manufacturing Pvt Ltd",
        "business_type": "Manufacturer",
        "city": "Coimbatore",
        "state": "Tamil Nadu"
    })
    assert seller_reg.status_code == 200
    seller_data = seller_reg.json()
    seller_token = seller_data["access_token"]
    seller_id = seller_data["user"]["id"]

    # STEP 2: Seller logs in
    seller_login = client.post("/api/auth/login", json={
        "email": "seller_xyz@manufacturing.com",
        "password": "Password@123"
    })
    assert seller_login.status_code == 200

    # STEP 3 & 4: AI Identification & Price Prediction
    # AI identifies Aluminium Scrap
    classify_res = client.post(
        "/api/ml/classify-material",
        files={"file": ("aluminium_scrap_500.jpg", b"fake image bytes", "image/jpeg")}
    )
    assert classify_res.status_code == 200
    assert "Aluminum" in classify_res.json()["material"] or "Aluminium" in classify_res.json()["material"]


    # STEP 5: AI Predicts Market Estimate Range: e.g. ~₹180/kg
    price_pred_res = client.post("/api/ml/predict-price", json={
        "material_type": "Aluminum",
        "weight_kg": 500.0,
        "quality": "High",
        "location": "Coimbatore",
        "demand_level": "High",
        "historical_price": 180.0,
        "processing_cost": 5.0,
        "transportation_distance": 20.0,
        "month": 9,
        "seller_type": "Business",
        "buyer_demand": 0.85,
        "material_condition": "Sorted"
    })
    assert price_pred_res.status_code == 200
    price_data = price_pred_res.json()
    ai_estimated_price = price_data["predicted_price_per_kg"]
    ai_min = price_data["estimated_min_price"]
    ai_max = price_data["estimated_max_price"]
    assert ai_min <= ai_estimated_price <= ai_max

    # STEP 6: Seller sets Asking Price: ₹200/kg (manually decided by seller, not AI)
    # 1. Create material
    mat_res = client.post("/api/materials", json={
        "material_type": "Aluminum",
        "quantity_kg": 500.0,
        "quality": "High",
        "condition": "Sorted",
        "intended_purpose": "Recycling",
        "description": "Clean aluminium manufacturing scrap from automotive plant.",
        "predicted_price": ai_estimated_price
    }, headers={"Authorization": f"Bearer {seller_token}"})
    assert mat_res.status_code == 200
    material_id = mat_res.json()["id"]

    # 2. Create Listing with explicit seller Asking Price ₹200/kg and AI Range bounds
    listing_res = client.post("/api/listings", json={
        "material_id": material_id,
        "quantity_available": 500.0,
        "unit": "kg",
        "asking_price": 200.0,
        "min_acceptable_price": 180.0,
        "ai_estimated_min_price": ai_min,
        "ai_estimated_max_price": ai_max,
        "status": "active"
    }, headers={"Authorization": f"Bearer {seller_token}"})
    assert listing_res.status_code == 201
    listing_data = listing_res.json()
    listing_id = listing_data["id"]
    assert listing_data["asking_price"] == 200.0
    assert listing_data["ai_estimated_min_price"] == ai_min

    # STEP 7: Register Buyer (ABC Recycling)
    buyer_reg = client.post("/api/auth/register", json={
        "name": "ABC Recycling",
        "email": "buyer_abc@recycling.com",
        "password": "Password@123",
        "role": "buyer",
        "organization": "ABC Circular Recycling Mills",
        "business_type": "Recycler",
        "materials_interested": "Aluminum, Copper, Steel",
        "city": "Coimbatore",
        "state": "Tamil Nadu"
    })
    assert buyer_reg.status_code == 200
    buyer_token = buyer_reg.json()["access_token"]
    buyer_id = buyer_reg.json()["user"]["id"]

    # STEP 8: Buyer logs in
    buyer_login = client.post("/api/auth/login", json={
        "email": "buyer_abc@recycling.com",
        "password": "Password@123"
    })
    assert buyer_login.status_code == 200

    # STEP 9 & 10: Buyer searches and finds listing
    search_res = client.get("/api/listings?material_type=Aluminum&status=active")
    assert search_res.status_code == 200
    active_listings = search_res.json()
    target_listing = next((l for l in active_listings if l["id"] == listing_id), None)
    assert target_listing is not None
    assert target_listing["asking_price"] == 200.0

    # STEP 11: Buyer sends offer (500 kg, ₹185/kg)
    offer_create = client.post("/api/offers", json={
        "listing_id": listing_id,
        "offered_quantity": 500.0,
        "offered_price": 185.0,
        "message": "I can purchase the complete quantity."
    }, headers={"Authorization": f"Bearer {buyer_token}"})
    assert offer_create.status_code == 201
    offer_id = offer_create.json()["id"]

    # STEP 12 & 13: Seller sees offer and counters with ₹195/kg
    seller_offers = client.get("/api/offers/seller/me", headers={"Authorization": f"Bearer {seller_token}"})
    assert seller_offers.status_code == 200
    assert any(o["id"] == offer_id for o in seller_offers.json())

    seller_counter = client.post(f"/api/offers/{offer_id}/counter", json={
        "counter_price": 195.0,
        "message": "Can supply entire lot at ₹195/kg."
    }, headers={"Authorization": f"Bearer {seller_token}"})
    assert seller_counter.status_code == 200
    assert seller_counter.json()["offered_price"] == 195.0

    # STEP 14: Buyer counters back with ₹190/kg
    buyer_counter = client.post(f"/api/offers/{offer_id}/counter", json={
        "counter_price": 190.0,
        "message": "Deal at ₹190/kg works for immediate pickup."
    }, headers={"Authorization": f"Bearer {buyer_token}"})
    assert buyer_counter.status_code == 200
    assert buyer_counter.json()["offered_price"] == 190.0

    # STEP 15: Seller accepts negotiated offer
    accept_res = client.post(f"/api/offers/{offer_id}/accept", headers={"Authorization": f"Bearer {seller_token}"})
    assert accept_res.status_code == 200
    accept_json = accept_res.json()
    assert accept_json["success"] is True
    assert accept_json["offer"]["status"] == "ACCEPTED"
    assert accept_json["offer"]["agreed_price"] == 190.0

    # STEP 16: Verify Confirmed Transaction
    txn = accept_json["transaction"]
    transaction_id = txn["id"]
    assert txn["quantity_kg"] == 500.0
    assert txn["agreed_price"] == 190.0
    assert txn["total_amount"] == 95000.0
    assert txn["status"] == "CONFIRMED"

    # STEP 17: Verify Listing inventory updated (sold out)
    listing_check = client.get(f"/api/listings/{listing_id}")
    assert listing_check.status_code == 200
    assert listing_check.json()["quantity_available"] == 0.0
    assert listing_check.json()["status"] == "sold"

    # STEP 18: Both users can view the transaction
    s_txn = client.get(f"/api/transactions/{transaction_id}", headers={"Authorization": f"Bearer {seller_token}"})
    assert s_txn.status_code == 200
    b_txn = client.get(f"/api/transactions/{transaction_id}", headers={"Authorization": f"Bearer {buyer_token}"})
    assert b_txn.status_code == 200

    # STEP 19 & 20: In-platform Chat communication
    msg_s = client.post(f"/api/transactions/{transaction_id}/messages", json={
        "message": "When can you arrange pickup?"
    }, headers={"Authorization": f"Bearer {seller_token}"})
    assert msg_s.status_code == 201

    msg_b = client.post(f"/api/transactions/{transaction_id}/messages", json={
        "message": "Our vehicle will come tomorrow at 10 AM."
    }, headers={"Authorization": f"Bearer {buyer_token}"})
    assert msg_b.status_code == 201

    chat_history = client.get(f"/api/transactions/{transaction_id}/messages", headers={"Authorization": f"Bearer {buyer_token}"})
    assert chat_history.status_code == 200
    assert len(chat_history.json()) == 2

    # STEP 21: Pickup scheduled
    pickup_res = client.post(f"/api/transactions/{transaction_id}/schedule-pickup", json={
        "pickup_location": "XYZ Manufacturing Plant, Gate 3, Coimbatore",
        "pickup_instructions": "Contact Logistics Mgr at arrival"
    }, headers={"Authorization": f"Bearer {seller_token}"})
    assert pickup_res.status_code == 200
    assert pickup_res.json()["status"] == "PICKUP_SCHEDULED"

    # STEP 22: Transaction completed
    complete_res = client.post(f"/api/transactions/{transaction_id}/complete", headers={"Authorization": f"Bearer {buyer_token}"})
    assert complete_res.status_code == 200
    assert complete_res.json()["status"] == "COMPLETED"

    # STEP 23: Sustainability & Overview Analytics updated
    analytics_res = client.get("/api/analytics/overview")
    assert analytics_res.status_code == 200
    analytics_data = analytics_res.json()
    assert analytics_data["total_transactions"] >= 1
    assert analytics_data["landfill_diverted_kg"] >= 500.0

    sust_res = client.get("/api/analytics/sustainability")
    assert sust_res.status_code == 200
    sust_data = sust_res.json()
    assert sust_data["completed_transactions_count"] >= 1
    assert sust_data["estimated_co2_avoided_kg"] > 0.0

    # =========================================================================
    # CORE BUSINESS RULE / SECTION 47: PRICE SEPARATION VERIFICATION
    # =========================================================================
    # Verify that:
    # 1. AI Estimated Min/Max is stored
    # 2. Seller Asking Price = 200.0
    # 3. Final Agreed Price = 190.0
    # 4. Total Amount = 95,000.0
    # NONE of these overwrite or collide with each other!
    assert target_listing["asking_price"] == 200.0
    assert target_listing["ai_estimated_min_price"] == ai_min
    assert target_listing["ai_estimated_max_price"] == ai_max
    assert txn["agreed_price"] == 190.0
    assert txn["total_amount"] == 95000.0
    assert target_listing["asking_price"] != txn["agreed_price"]
