import pytest
from backend.app.services.price_prediction_service import price_prediction_service
from backend.app.services.demand_prediction_service import demand_prediction_service
from backend.app.services.classification_service import classification_service


def test_ml_services_loaded():
    assert price_prediction_service is not None
    assert demand_prediction_service is not None
    assert classification_service is not None


def test_predict_price_api(client):
    payload = {
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
        "material_condition": "Good",
    }
    res = client.post("/api/ml/predict-price", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data["predicted_price_per_kg"], (int, float))
    assert data["predicted_price_per_kg"] > 0
    assert data["currency"] == "INR"
    assert "model_version" in data
    assert "estimated_total_value" in data
    assert round(data["predicted_price_per_kg"] * 500.0, 1) == round(data["estimated_total_value"], 1)


def test_predict_demand_api(client):
    payload = {
        "material_type": "Copper",
        "forecast_period": "next_month",
        "location": "Coimbatore",
    }
    res = client.post("/api/ml/predict-demand", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["material"] == "Copper"
    assert isinstance(data["predicted_demand_kg"], (int, float))
    assert data["predicted_demand_kg"] > 0
    assert data["demand_category"] in ["High", "Moderate", "Low"]
    assert data["trend"] in ["increasing", "stable", "decreasing"]


def test_ml_performance_api(client):
    res = client.get("/api/ml/performance")
    assert res.status_code == 200
    data = res.json()
    assert "price_model" in data
    assert "classification_model" in data
    assert "demand_model" in data
    assert "system_status" in data
    assert data["price_model"]["algorithm"] == "Gradient Boosting"
    assert data["price_model"]["evaluation_metrics"]["test_r2"] > 0.9


def test_classify_material_api(client):
    from PIL import Image
    import io

    img = Image.new("RGB", (224, 224), color=(200, 100, 50))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)

    files = {"file": ("copper_wire.png", buf, "image/png")}
    res = client.post("/api/ml/classify-material", files=files)
    assert res.status_code == 200
    data = res.json()
    assert "material" in data
    assert "confidence" in data
    assert 0.0 <= data["confidence"] <= 1.0
    assert "model_version" in data
