import pytest
from backend.app.models.user import User
from backend.app.models.listing import Listing


def test_create_transaction_and_impact(client, buyer_token, db_session):
    # Find a seller and active listing
    seller = db_session.query(User).filter(User.role == "seller").first()
    listing = db_session.query(Listing).filter(Listing.status == "active").first()
    initial_qty = listing.quantity_available

    headers = {"Authorization": f"Bearer {buyer_token}"}
    payload = {
        "listing_id": listing.id,
        "seller_id": seller.id,
        "material_type": "Aluminum",
        "quantity_kg": 100.0,
        "agreed_price": 180.0,
    }

    res = client.post("/api/transactions", json=payload, headers=headers)
    assert res.status_code == 200
    tx = res.json()
    assert tx["material_type"] == "Aluminum"
    assert tx["quantity_kg"] == 100.0
    assert tx["agreed_price"] == 180.0
    assert tx["total_amount"] == 18000.0
    assert tx["co2_avoided_kg"] > 0
    assert tx["landfill_diverted_kg"] > 0

    # Verify listing quantity was decremented
    listing_res = client.get(f"/api/listings/{listing.id}")
    assert listing_res.status_code == 200
    updated_listing = listing_res.json()
    assert updated_listing["quantity_available"] == initial_qty - 100.0


def test_sustainability_analytics(client):
    res = client.get("/api/analytics/sustainability")
    assert res.status_code == 200
    data = res.json()
    assert "estimated_co2_avoided_kg" in data
    assert "landfill_diverted_kg" in data
    assert "impact_by_material" in data
    assert "conversion_factors" in data
    assert "disclaimer" in data
