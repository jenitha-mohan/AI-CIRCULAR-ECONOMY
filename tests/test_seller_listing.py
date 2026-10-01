"""
Seller Module Tests — Step 1
Tests exactly 10 items as specified:
1. Seller Dashboard
2. My Listings
3. Add Waste (create material + listing)
4. Image upload
5. Material details
6. Seller-entered asking price
7. Create listing
8. View seller's own listings
9. Seller role/ownership security
10. Tests (pytest)
"""

import io
import pytest


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

SELLER_A = {
    "name": "Seller A Industries",
    "email": "seller_a@testco.com",
    "password": "Password@123",
    "role": "seller",
    "organization": "Seller A Pvt Ltd",
    "business_type": "Manufacturer",
    "phone": "9876543210",
    "city": "Coimbatore",
    "state": "Tamil Nadu",
}

SELLER_B = {
    "name": "Seller B Corp",
    "email": "seller_b@testco.com",
    "password": "Password@123",
    "role": "seller",
    "organization": "Seller B Corp",
    "business_type": "Recycler",
    "phone": "9876543211",
    "city": "Chennai",
    "state": "Tamil Nadu",
}

BUYER_X = {
    "name": "Buyer X Ltd",
    "email": "buyer_x@testco.com",
    "password": "Password@123",
    "role": "buyer",
    "organization": "Buyer X Trading",
    "materials_interested": "Aluminum, Steel",
    "phone": "9876543212",
    "city": "Bengaluru",
    "state": "Karnataka",
}


def register_and_login(client, payload):
    reg = client.post("/api/auth/register", json=payload)
    assert reg.status_code == 200, f"Registration failed: {reg.text}"
    return reg.json()["access_token"]


# ─────────────────────────────────────────────
# TEST 1: Seller Dashboard — requires auth
# ─────────────────────────────────────────────

def test_1_seller_dashboard_requires_auth(client):
    """Unauthenticated access to seller materials endpoint should return 401."""
    res = client.get("/api/listings/seller/me")
    assert res.status_code == 401, f"Expected 401, got {res.status_code}"


# ─────────────────────────────────────────────
# TEST 2: My Listings — empty for new seller
# ─────────────────────────────────────────────

def test_2_my_listings_empty_for_new_seller(client):
    """A brand new seller should have 0 listings."""
    token = register_and_login(client, SELLER_A)
    res = client.get("/api/listings/seller/me", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert isinstance(res.json(), list)
    assert len(res.json()) == 0


# ─────────────────────────────────────────────
# TEST 3: Add Waste — create material + listing
# ─────────────────────────────────────────────

def test_3_add_waste_creates_material_and_listing(client):
    """Creating a material auto-creates a listing with seller's asking price."""
    token = register_and_login(client, {**SELLER_A, "email": "seller_a2@testco.com"})
    
    res = client.post(
        "/api/materials?asking_price=150.0",
        json={
            "material_type": "Aluminum",
            "quantity_kg": 300.0,
            "quality": "High",
            "condition": "Clean",
            "intended_purpose": "Recycling",
            "description": "Clean aluminum scrap from manufacturing.",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    material = res.json()
    assert material["material_type"] == "Aluminum"
    assert material["quantity_kg"] == 300.0
    assert "id" in material

    # Verify listing was auto-created
    listings = client.get("/api/listings/seller/me", headers={"Authorization": f"Bearer {token}"}).json()
    assert len(listings) == 1
    assert listings[0]["asking_price"] == 150.0


# ─────────────────────────────────────────────
# TEST 4: Image Upload — upload endpoint works
# ─────────────────────────────────────────────

def test_4_image_upload(client):
    """Image upload endpoint returns a file path and classification."""
    token = register_and_login(client, {**SELLER_A, "email": "seller_a3@testco.com"})

    # Fake 1x1 pixel JPEG
    fake_image = io.BytesIO(
        b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00"
        b"\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c"
        b"\xff\xd9"
    )
    res = client.post(
        "/api/materials/upload-image",
        files={"file": ("test_material.jpg", fake_image, "image/jpeg")},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert "file_path" in data
    assert data["file_path"].startswith("/uploads/")
    assert "classification" in data


# ─────────────────────────────────────────────
# TEST 5: Material Details — fetched by ID
# ─────────────────────────────────────────────

def test_5_material_details_by_id(client):
    """Material details can be retrieved by ID."""
    token = register_and_login(client, {**SELLER_A, "email": "seller_a4@testco.com"})

    create_res = client.post(
        "/api/materials?asking_price=200.0",
        json={
            "material_type": "Steel",
            "quantity_kg": 500.0,
            "quality": "Medium",
            "condition": "Sorted",
            "intended_purpose": "Recycling",
            "description": "HR steel coil scrap.",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert create_res.status_code == 200
    material_id = create_res.json()["id"]

    detail_res = client.get(f"/api/materials/{material_id}")
    assert detail_res.status_code == 200
    detail = detail_res.json()
    assert detail["id"] == material_id
    assert detail["material_type"] == "Steel"
    assert detail["quantity_kg"] == 500.0
    assert detail["description"] == "HR steel coil scrap."


# ─────────────────────────────────────────────
# TEST 6: Seller-Entered Asking Price
# ─────────────────────────────────────────────

def test_6_seller_sets_asking_price_manually(client):
    """Asking price must be set by seller. AI price must NOT appear in the response."""
    token = register_and_login(client, {**SELLER_A, "email": "seller_a5@testco.com"})

    SELLER_ASK = 185.5
    res = client.post(
        f"/api/materials?asking_price={SELLER_ASK}",
        json={
            "material_type": "Copper",
            "quantity_kg": 100.0,
            "quality": "High",
            "condition": "Clean",
            "intended_purpose": "Recycling",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    material = res.json()

    # No AI price fields should exist
    assert "predicted_price" not in material
    assert "ai_estimated_min_price" not in material
    assert "ai_estimated_max_price" not in material

    # Listing must carry the seller's exact price
    listings = client.get("/api/listings/seller/me", headers={"Authorization": f"Bearer {token}"}).json()
    assert len(listings) == 1
    assert listings[0]["asking_price"] == SELLER_ASK

    # Listing response must not carry AI fields
    assert "ai_estimated_min_price" not in listings[0]
    assert "ai_estimated_max_price" not in listings[0]


# ─────────────────────────────────────────────
# TEST 7: Create Listing — asking_price required
# ─────────────────────────────────────────────

def test_7_create_material_requires_asking_price(client):
    """Creating a material without asking_price should return 422."""
    token = register_and_login(client, {**SELLER_A, "email": "seller_a6@testco.com"})

    res = client.post(
        "/api/materials",  # No ?asking_price query param
        json={
            "material_type": "Glass",
            "quantity_kg": 50.0,
            "quality": "Low",
            "condition": "Mixed",
            "intended_purpose": "Recycling",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 422  # FastAPI missing required query param


def test_7b_create_listing_asking_price_must_be_positive(client):
    """Listing with asking_price = 0 should be rejected."""
    token = register_and_login(client, {**SELLER_A, "email": "seller_a7@testco.com"})

    # Create material first
    mat_res = client.post(
        "/api/materials?asking_price=100.0",
        json={"material_type": "Paper", "quantity_kg": 200.0, "quality": "Medium", "condition": "Sorted", "intended_purpose": "Recycling"},
        headers={"Authorization": f"Bearer {token}"},
    )
    material_id = mat_res.json()["id"]

    # Try to create a listing with price = 0
    res = client.post(
        "/api/listings",
        json={"material_id": material_id, "quantity_available": 200.0, "asking_price": 0.0},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 422


# ─────────────────────────────────────────────
# TEST 8: View Seller's Own Listings
# ─────────────────────────────────────────────

def test_8_seller_sees_only_own_listings(client):
    """Each seller must only see their own listings, not others'."""
    token_a = register_and_login(client, SELLER_B)
    token_b = register_and_login(client, {**SELLER_B, "email": "seller_b2@testco.com"})

    # Seller A creates 2 listings
    for i in range(2):
        client.post(
            f"/api/materials?asking_price={100 + i * 10}.0",
            json={"material_type": "Plastic", "quantity_kg": 100.0 + i, "quality": "Medium", "condition": "Sorted", "intended_purpose": "Recycling"},
            headers={"Authorization": f"Bearer {token_a}"},
        )

    # Seller B creates 1 listing
    client.post(
        "/api/materials?asking_price=80.0",
        json={"material_type": "Paper", "quantity_kg": 50.0, "quality": "Low", "condition": "Mixed", "intended_purpose": "Recycling"},
        headers={"Authorization": f"Bearer {token_b}"},
    )

    listings_a = client.get("/api/listings/seller/me", headers={"Authorization": f"Bearer {token_a}"}).json()
    listings_b = client.get("/api/listings/seller/me", headers={"Authorization": f"Bearer {token_b}"}).json()

    assert len(listings_a) == 2
    assert len(listings_b) == 1

    # Ensure A's listings don't appear in B's
    a_ids = {l["id"] for l in listings_a}
    b_ids = {l["id"] for l in listings_b}
    assert a_ids.isdisjoint(b_ids)


# ─────────────────────────────────────────────
# TEST 9: Seller Role/Ownership Security
# ─────────────────────────────────────────────

def test_9a_buyer_cannot_create_listing(client):
    """A buyer must not be allowed to create material listings."""
    token = register_and_login(client, BUYER_X)

    res = client.post(
        "/api/materials?asking_price=100.0",
        json={"material_type": "Aluminum", "quantity_kg": 100.0, "quality": "High", "condition": "Clean", "intended_purpose": "Recycling"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 403


def test_9b_seller_cannot_edit_other_sellers_listing(client):
    """Seller A must not be able to edit Seller B's listing."""
    token_a = register_and_login(client, {**SELLER_A, "email": "seller_sec_a@testco.com"})
    token_b = register_and_login(client, {**SELLER_A, "email": "seller_sec_b@testco.com"})

    # Seller B creates a listing
    mat_res = client.post(
        "/api/materials?asking_price=120.0",
        json={"material_type": "Steel", "quantity_kg": 200.0, "quality": "High", "condition": "Sorted", "intended_purpose": "Recycling"},
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert mat_res.status_code == 200

    listings_b = client.get("/api/listings/seller/me", headers={"Authorization": f"Bearer {token_b}"}).json()
    listing_id = listings_b[0]["id"]

    # Seller A tries to update Seller B's listing
    update_res = client.put(
        f"/api/listings/{listing_id}",
        json={"asking_price": 999.0},
        headers={"Authorization": f"Bearer {token_a}"},
    )
    assert update_res.status_code == 403


def test_9c_seller_cannot_delete_other_sellers_listing(client):
    """Seller A must not be able to delete Seller B's listing."""
    token_a = register_and_login(client, {**SELLER_A, "email": "seller_del_a@testco.com"})
    token_b = register_and_login(client, {**SELLER_A, "email": "seller_del_b@testco.com"})

    mat_res = client.post(
        "/api/materials?asking_price=90.0",
        json={"material_type": "Plastic", "quantity_kg": 50.0, "quality": "Low", "condition": "Mixed", "intended_purpose": "Recycling"},
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert mat_res.status_code == 200

    listings_b = client.get("/api/listings/seller/me", headers={"Authorization": f"Bearer {token_b}"}).json()
    listing_id = listings_b[0]["id"]

    del_res = client.delete(
        f"/api/listings/{listing_id}",
        headers={"Authorization": f"Bearer {token_a}"},
    )
    assert del_res.status_code == 403


def test_9d_unauthenticated_cannot_create_material(client):
    """No token → 401 on material creation."""
    res = client.post(
        "/api/materials?asking_price=100.0",
        json={"material_type": "Aluminum", "quantity_kg": 100.0, "quality": "High", "condition": "Clean", "intended_purpose": "Recycling"},
    )
    assert res.status_code == 401


# ─────────────────────────────────────────────
# TEST 10: Full Seller Listing Workflow
# ─────────────────────────────────────────────

def test_10_full_seller_listing_workflow(client):
    """
    End-to-end seller flow:
    Register → Create Material → Auto Listing → Update Asking Price → Delete Listing
    """
    token = register_and_login(client, {**SELLER_A, "email": "seller_flow@testco.com"})

    # 1. Create material with seller asking price
    res = client.post(
        "/api/materials?asking_price=175.0",
        json={
            "material_type": "Aluminum",
            "quantity_kg": 400.0,
            "quality": "High",
            "condition": "Clean",
            "intended_purpose": "Upcycling",
            "description": "6063 aluminum extrusion scrap, clean, degreased.",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    material = res.json()
    assert material["material_type"] == "Aluminum"
    assert "predicted_price" not in material

    # 2. Listing is auto-created with correct price
    listings = client.get("/api/listings/seller/me", headers={"Authorization": f"Bearer {token}"}).json()
    assert len(listings) == 1
    listing = listings[0]
    assert listing["asking_price"] == 175.0
    assert listing["status"] == "active"
    assert listing["quantity_available"] == 400.0
    assert listing["material"]["material_type"] == "Aluminum"

    listing_id = listing["id"]

    # 3. Seller updates asking price
    update_res = client.put(
        f"/api/listings/{listing_id}",
        json={"asking_price": 190.0},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert update_res.status_code == 200
    assert update_res.json()["asking_price"] == 190.0

    # 4. Listing appears in public marketplace with updated price
    public_res = client.get("/api/listings?status=active")
    assert public_res.status_code == 200
    public_listing = next((l for l in public_res.json() if l["id"] == listing_id), None)
    assert public_listing is not None
    assert public_listing["asking_price"] == 190.0

    # 5. Seller deletes listing
    del_res = client.delete(
        f"/api/listings/{listing_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert del_res.status_code == 200
    assert del_res.json()["success"] is True

    # 6. Listing gone from seller's view
    listings_after = client.get("/api/listings/seller/me", headers={"Authorization": f"Bearer {token}"}).json()
    assert all(l["id"] != listing_id for l in listings_after)
