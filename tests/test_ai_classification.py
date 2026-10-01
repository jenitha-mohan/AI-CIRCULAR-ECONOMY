"""
STEP 3 — AI Material Identification Tests

Tests exactly the 10 items specified:
1. Seller can upload a valid image.
2. Unauthenticated user gets 401.
3. Buyer gets 403.
4. Invalid image type is rejected.
5. Oversized image is rejected.
6. Classification response contains material/category/confidence.
7. Seller can override the AI classification.
8. Listing stores the seller-selected material.
9. Asking price remains seller-controlled.
10. No AI price prediction is used.
"""

import io
import pytest

# ─── payloads ────────────────────────────────────────────────────────────────

SELLER_PAYLOAD = {
    "name": "Classify Seller",
    "email": "classify_seller@step3.com",
    "password": "Password@123",
    "role": "seller",
    "organization": "Classify Seller Co",
    "business_type": "Manufacturer",
    "phone": "9000000001",
    "city": "Coimbatore",
    "state": "Tamil Nadu",
}

BUYER_PAYLOAD = {
    "name": "Classify Buyer",
    "email": "classify_buyer@step3.com",
    "password": "Password@123",
    "role": "buyer",
    "organization": "Classify Buyer Ltd",
    "materials_interested": "Aluminum",
    "phone": "9000000002",
    "city": "Chennai",
    "state": "Tamil Nadu",
}

# Minimal valid JPEG bytes (single grey pixel)
_JPEG = (
    b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00"
    b"\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t"
    b"\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f"
    b"\xff\xd9"
)

ENDPOINT = "/api/seller/materials/classify"


def _reg_login(client, payload):
    r = client.post("/api/auth/register", json=payload)
    assert r.status_code == 200, f"Registration failed: {r.text}"
    return r.json()["access_token"]


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


def _jpeg_file(name="material.jpg"):
    return {"file": (name, io.BytesIO(_JPEG), "image/jpeg")}


# ─── Test 1: Seller can upload a valid image ─────────────────────────────────

def test_1_seller_can_upload_valid_image(client):
    token = _reg_login(client, SELLER_PAYLOAD)
    res = client.post(ENDPOINT, files=_jpeg_file("aluminum_scrap.jpg"), headers=_auth(token))
    assert res.status_code == 200, res.text


# ─── Test 2: Unauthenticated user gets 401 ───────────────────────────────────

def test_2_unauthenticated_gets_401(client):
    res = client.post(ENDPOINT, files=_jpeg_file())
    assert res.status_code == 401, f"Expected 401, got {res.status_code}: {res.text}"


# ─── Test 3: Buyer gets 403 ──────────────────────────────────────────────────

def test_3_buyer_gets_403(client):
    token = _reg_login(client, BUYER_PAYLOAD)
    res = client.post(ENDPOINT, files=_jpeg_file(), headers=_auth(token))
    assert res.status_code == 403, f"Expected 403, got {res.status_code}: {res.text}"


# ─── Test 4: Invalid image type is rejected (422) ────────────────────────────

def test_4_invalid_image_type_rejected(client):
    token = _reg_login(
        client,
        {**SELLER_PAYLOAD, "email": "sel_inv@step3.com"},
    )
    # Send a .txt file
    res = client.post(
        ENDPOINT,
        files={"file": ("material.txt", io.BytesIO(b"not an image"), "text/plain")},
        headers=_auth(token),
    )
    assert res.status_code == 422, f"Expected 422, got {res.status_code}: {res.text}"


def test_4b_pdf_extension_rejected(client):
    token = _reg_login(
        client,
        {**SELLER_PAYLOAD, "email": "sel_pdf@step3.com"},
    )
    res = client.post(
        ENDPOINT,
        files={"file": ("invoice.pdf", io.BytesIO(b"%PDF"), "application/pdf")},
        headers=_auth(token),
    )
    assert res.status_code == 422


# ─── Test 5: Oversized image is rejected (413) ───────────────────────────────

def test_5_oversized_image_rejected(client):
    token = _reg_login(
        client,
        {**SELLER_PAYLOAD, "email": "sel_big@step3.com"},
    )
    # Create 11 MB of fake data
    oversized = io.BytesIO(b"x" * (11 * 1024 * 1024))
    res = client.post(
        ENDPOINT,
        files={"file": ("big.jpg", oversized, "image/jpeg")},
        headers=_auth(token),
    )
    assert res.status_code == 413, f"Expected 413, got {res.status_code}: {res.text}"


# ─── Test 6: Classification response contains material/category/confidence ───

def test_6_classification_response_fields(client):
    token = _reg_login(
        client,
        {**SELLER_PAYLOAD, "email": "sel_fields@step3.com"},
    )
    res = client.post(
        ENDPOINT,
        files=_jpeg_file("copper_wire.jpg"),
        headers=_auth(token),
    )
    assert res.status_code == 200, res.text
    data = res.json()

    # Required fields
    assert "material"   in data, "missing 'material'"
    assert "category"   in data, "missing 'category'"
    assert "confidence" in data, "missing 'confidence'"
    assert "image_url"  in data, "missing 'image_url'"

    # Types
    assert isinstance(data["material"],   str)
    assert isinstance(data["category"],   str)
    assert isinstance(data["confidence"], float)
    assert 0.0 <= data["confidence"] <= 1.0

    # Material must be from known list
    valid = {
        "Plastic", "Aluminum", "Copper", "Steel", "Paper",
        "Glass", "Textile", "E-waste", "Cardboard", "Other",
    }
    assert data["material"] in valid, f"Unknown material '{data['material']}'"

    # No price fields must exist
    assert "predicted_price"        not in data
    assert "ai_estimated_min_price" not in data
    assert "ai_estimated_max_price" not in data


# ─── Test 7: Seller can override the AI classification ───────────────────────

def test_7_seller_can_override_material(client):
    """
    After classification, seller sends a different material when creating the listing.
    The listing must store the seller-chosen material, not the AI result.
    """
    token = _reg_login(
        client,
        {**SELLER_PAYLOAD, "email": "sel_override@step3.com"},
    )

    # Step 1: classify
    classify_res = client.post(
        ENDPOINT,
        files=_jpeg_file("unknown.jpg"),
        headers=_auth(token),
    )
    assert classify_res.status_code == 200
    image_url = classify_res.json()["image_url"]

    # Step 2: seller overrides material to "Steel" regardless of AI result
    SELLER_CHOSEN = "Steel"
    create_res = client.post(
        "/api/materials?asking_price=120.0",
        json={
            "material_type":    SELLER_CHOSEN,
            "quantity_kg":      200.0,
            "quality":          "High",
            "condition":        "Sorted",
            "intended_purpose": "Recycling",
            "image_url":        image_url,
        },
        headers=_auth(token),
    )
    assert create_res.status_code == 200
    assert create_res.json()["material_type"] == SELLER_CHOSEN


# ─── Test 8: Listing stores the seller-selected material ─────────────────────

def test_8_listing_stores_seller_selected_material(client):
    token = _reg_login(
        client,
        {**SELLER_PAYLOAD, "email": "sel_store@step3.com"},
    )

    classify_res = client.post(
        ENDPOINT,
        files=_jpeg_file("glass_bottles.jpg"),
        headers=_auth(token),
    )
    assert classify_res.status_code == 200
    image_url = classify_res.json()["image_url"]

    # Seller chooses "Glass"
    create_res = client.post(
        "/api/materials?asking_price=30.0",
        json={
            "material_type":    "Glass",
            "quantity_kg":      100.0,
            "quality":          "Medium",
            "condition":        "Clean",
            "intended_purpose": "Recycling",
            "image_url":        image_url,
        },
        headers=_auth(token),
    )
    assert create_res.status_code == 200
    material_id = create_res.json()["id"]

    # Retrieve and confirm
    detail = client.get(f"/api/materials/{material_id}").json()
    assert detail["material_type"] == "Glass"


# ─── Test 9: Asking price remains seller-controlled ──────────────────────────

def test_9_asking_price_is_seller_controlled(client):
    token = _reg_login(
        client,
        {**SELLER_PAYLOAD, "email": "sel_price@step3.com"},
    )

    classify_res = client.post(
        ENDPOINT,
        files=_jpeg_file("aluminum_scrap.jpg"),
        headers=_auth(token),
    )
    assert classify_res.status_code == 200
    image_url = classify_res.json()["image_url"]

    SELLER_PRICE = 187.5
    create_res = client.post(
        f"/api/materials?asking_price={SELLER_PRICE}",
        json={
            "material_type":    "Aluminum",
            "quantity_kg":      400.0,
            "quality":          "High",
            "condition":        "Clean",
            "intended_purpose": "Recycling",
            "image_url":        image_url,
        },
        headers=_auth(token),
    )
    assert create_res.status_code == 200

    # Check the auto-created listing carries seller's price exactly
    listings = client.get(
        "/api/listings/seller/me", headers=_auth(token)
    ).json()
    assert len(listings) >= 1
    matching = [l for l in listings if l["asking_price"] == SELLER_PRICE]
    assert len(matching) == 1, "Seller's asking price not preserved in listing"

    # Confirm no AI price fields in listing
    assert "ai_estimated_min_price" not in listings[0]
    assert "ai_estimated_max_price" not in listings[0]


# ─── Test 10: No AI price prediction is used ─────────────────────────────────

def test_10_no_ai_price_prediction_in_classify_response(client):
    token = _reg_login(
        client,
        {**SELLER_PAYLOAD, "email": "sel_noprice@step3.com"},
    )

    res = client.post(
        ENDPOINT,
        files=_jpeg_file("steel_scrap.jpg"),
        headers=_auth(token),
    )
    assert res.status_code == 200
    data = res.json()

    # Strict: none of these must appear
    forbidden = [
        "predicted_price",
        "ai_estimated_min_price",
        "ai_estimated_max_price",
        "price_prediction",
        "suggested_price",
        "recommended_price",
        "market_price",
    ]
    for field in forbidden:
        assert field not in data, (
            f"Price prediction field '{field}' found in classify response — must not exist."
        )
