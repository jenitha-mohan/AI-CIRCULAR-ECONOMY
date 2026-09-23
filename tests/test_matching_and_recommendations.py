import pytest
from backend.app.services.matching_service import matching_engine


def test_matching_engine_exact_match():
    material = {
        "material_type": "Aluminum",
        "quantity_kg": 500.0,
        "quality": "High",
        "condition": "Clean",
        "intended_purpose": "Recycling"
    }
    buyer_req = {
        "material_type": "Aluminum",
        "min_quantity": 400.0,
        "max_quantity": 700.0,
        "quality": "High",
        "purpose": "Recycling"
    }
    res = matching_engine.compute_match(
        material=material,
        buyer_req=buyer_req,
        seller_lat=11.0168,
        seller_lon=76.9558,
        buyer_lat=11.0168,
        buyer_lon=76.9558
    )
    assert 0.90 <= res["match_score"] <= 1.0
    assert len(res["reasons"]) > 0
    assert "reasons" in res
    assert "components" in res


def test_matching_engine_different_material():
    material = {
        "material_type": "Aluminum",
        "quantity_kg": 500.0,
        "quality": "High",
        "condition": "Clean",
        "intended_purpose": "Recycling"
    }
    buyer_req = {
        "material_type": "Textile",
        "min_quantity": 400.0,
        "max_quantity": 700.0,
        "quality": "High",
        "purpose": "Recycling"
    }
    res = matching_engine.compute_match(material=material, buyer_req=buyer_req)
    # Material similarity is 0%, so score must be low
    assert res["match_score"] < 0.70


def test_buyer_recommendations_for_material(client, seller_token):
    # First get an existing material
    mat_res = client.get("/api/materials")
    assert mat_res.status_code == 200
    materials = mat_res.json()
    assert len(materials) > 0
    mat_id = materials[0]["id"]

    res = client.get(f"/api/recommendations/buyers/{mat_id}")
    assert res.status_code == 200
    recs = res.json()
    assert isinstance(recs, list)
    for rec in recs:
        assert "buyer_id" in rec
        assert "match_score" in rec
        assert 0.0 <= rec["match_score"] <= 1.0
        assert "reasons" in rec
        assert isinstance(rec["reasons"], list)


def test_material_recommendations_for_buyer(client, buyer_token, db_session):
    from backend.app.models.user import User
    buyer = db_session.query(User).filter(User.role == "buyer").first()

    res = client.get(f"/api/recommendations/materials/{buyer.id}")
    assert res.status_code == 200
    recs = res.json()
    assert isinstance(recs, list)
    for rec in recs:
        assert "material_id" in rec
        assert "match_score" in rec
        assert 0.0 <= rec["match_score"] <= 1.0
        assert "reasons" in rec
