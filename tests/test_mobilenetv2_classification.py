"""
STEP 3H — MobileNetV2 Integration Tests
========================================
Tests the real inference service end-to-end through the FastAPI test client.

Rules:
- Real model inference is used for every successful-prediction test.
- Predictions are NEVER mocked or patched for the "valid image" tests.
- All existing auth / seller tests must continue to pass.
"""

import io
import os
import math
import pytest
from pathlib import Path
from PIL import Image

BASE_DIR = Path(__file__).resolve().parent.parent

# ── Credentials for test users ────────────────────────────────────────────────
SELLER_CREDS = {
    "name": "MNet Test Seller",
    "email": "mnet_seller@step3h.com",
    "password": "Password@123",
    "role": "seller",
    "organization": "MNet Seller Corp",
    "business_type": "Recycler",
    "phone": "9876543210",
    "city": "Coimbatore",
    "state": "Tamil Nadu",
}

BUYER_CREDS = {
    "name": "MNet Test Buyer",
    "email": "mnet_buyer@step3h.com",
    "password": "Password@123",
    "role": "buyer",
    "organization": "MNet Buyer Ltd",
    "materials_interested": "Plastic, Glass",
    "phone": "9876543211",
    "city": "Chennai",
    "state": "Tamil Nadu",
}


@pytest.fixture(scope="module")
def seller_auth_token(client):
    r = client.post("/api/auth/register", json=SELLER_CREDS)
    if r.status_code == 200:
        return r.json()["access_token"]
    login = client.post("/api/auth/login", json={
        "email": SELLER_CREDS["email"],
        "password": SELLER_CREDS["password"]
    })
    return login.json()["access_token"]


@pytest.fixture(scope="module")
def buyer_auth_token(client):
    r = client.post("/api/auth/register", json=BUYER_CREDS)
    if r.status_code == 200:
        return r.json()["access_token"]
    login = client.post("/api/auth/login", json={
        "email": BUYER_CREDS["email"],
        "password": BUYER_CREDS["password"]
    })
    return login.json()["access_token"]


# ── Helpers ────────────────────────────────────────────────────────────────────

def _make_jpeg_bytes(width=224, height=224, color=(120, 160, 80)) -> bytes:
    """Create a minimal valid JPEG in memory."""
    buf = io.BytesIO()
    Image.new("RGB", (width, height), color=color).save(buf, format="JPEG")
    buf.seek(0)
    return buf.read()


def _make_png_bytes(width=224, height=224, color=(80, 120, 200)) -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (width, height), color=color).save(buf, format="PNG")
    buf.seek(0)
    return buf.read()


def _read_real_test_image(class_name: str) -> bytes:
    """Read the first available image from the prepared test split."""
    test_dir = BASE_DIR / "datasets" / "material_images" / "test" / class_name
    for ext in ("*.jpg", "*.jpeg", "*.png", "*.webp"):
        files = list(test_dir.glob(ext))
        if files:
            return files[0].read_bytes()
    return _make_jpeg_bytes()


# ── 1. Service-level tests ────────────────────────────────────────────────────

class TestClassificationServiceLoad:

    def test_model_is_loaded_and_ready(self):
        """Model must load successfully at service startup."""
        from backend.app.services.classification_service import classification_service
        assert classification_service._model_ready is True, (
            f"Model not ready: {classification_service._load_error}"
        )

    def test_class_names_match_metadata(self):
        """class_names must be the 7 trained classes in alphabetical order."""
        from backend.app.services.classification_service import classification_service
        expected = ["Cardboard", "E-waste", "Glass", "Other", "Paper", "Plastic", "Textile"]
        assert classification_service.supported_classes == expected

    def test_metadata_reports_7_classes(self):
        """Metadata num_classes field must be 7."""
        from backend.app.services.classification_service import classification_service
        assert classification_service._metadata.get("num_classes") == 7

    def test_model_version_is_populated(self):
        from backend.app.services.classification_service import classification_service
        assert classification_service.model_version is not None
        assert len(classification_service.model_version) > 0


# ── 2. Real-inference service tests ───────────────────────────────────────────

class TestClassificationServiceInference:

    def test_valid_jpeg_returns_real_prediction(self):
        """Real JPEG -> real model output. No mocking."""
        from backend.app.services.classification_service import classification_service
        img_bytes = _read_real_test_image("Plastic")
        result = classification_service.classify_image(img_bytes, filename="test.jpg")

        assert "material" in result
        assert "confidence" in result
        assert "top_predictions" in result
        assert isinstance(result["top_predictions"], list)
        assert len(result["top_predictions"]) == 3
        assert 0.0 <= result["confidence"] <= 1.0
        assert result["is_fallback"] is False
        assert result["prototype"] is True

    def test_top_predictions_are_ordered(self):
        """Probabilities must be in descending order."""
        from backend.app.services.classification_service import classification_service
        img_bytes = _read_real_test_image("Cardboard")
        result = classification_service.classify_image(img_bytes)
        probs = [p["confidence"] for p in result["top_predictions"]]
        assert probs == sorted(probs, reverse=True), "Top-3 not in descending order"

    def test_top_prediction_matches_material_field(self):
        """result['material'] must equal top_predictions[0]['material']."""
        from backend.app.services.classification_service import classification_service
        img_bytes = _read_real_test_image("Glass")
        result = classification_service.classify_image(img_bytes)
        assert result["material"] == result["top_predictions"][0]["material"]
        assert result["confidence"] == result["top_predictions"][0]["confidence"]

    def test_all_probabilities_are_finite(self):
        from backend.app.services.classification_service import classification_service
        img_bytes = _read_real_test_image("Textile")
        result = classification_service.classify_image(img_bytes)
        for pred in result["top_predictions"]:
            assert math.isfinite(pred["confidence"]), f"Non-finite probability: {pred}"

    def test_supported_classes_in_response(self):
        from backend.app.services.classification_service import classification_service
        img_bytes = _make_jpeg_bytes()
        result = classification_service.classify_image(img_bytes)
        assert "supported_classes" in result
        assert "Aluminum" not in result["supported_classes"]
        assert "Copper" not in result["supported_classes"]
        assert "Steel" not in result["supported_classes"]

    def test_limitations_field_mentions_metals(self):
        from backend.app.services.classification_service import classification_service
        img_bytes = _make_jpeg_bytes()
        result = classification_service.classify_image(img_bytes)
        limitations = result.get("limitations", "").lower()
        assert "aluminum" in limitations or "copper" in limitations or "steel" in limitations

    def test_png_image_works(self):
        from backend.app.services.classification_service import classification_service
        img_bytes = _make_png_bytes()
        result = classification_service.classify_image(img_bytes, filename="test.png")
        assert result["material"] in classification_service.supported_classes

    def test_corrupted_bytes_raises_error(self):
        from backend.app.services.classification_service import classification_service
        with pytest.raises((ValueError, RuntimeError)):
            classification_service.classify_image(b"not an image", filename="bad.jpg")


# ── 3. Seller Classify Endpoint Tests (/api/seller/materials/classify) ────────

CLASSIFY_URL = "/api/seller/materials/classify"


class TestClassifyEndpointAuth:

    def test_unauthenticated_request_returns_401(self, client):
        img_bytes = _make_jpeg_bytes()
        res = client.post(
            CLASSIFY_URL,
            files={"file": ("test.jpg", io.BytesIO(img_bytes), "image/jpeg")},
        )
        assert res.status_code == 401

    def test_buyer_gets_403(self, client, buyer_auth_token):
        img_bytes = _make_jpeg_bytes()
        res = client.post(
            CLASSIFY_URL,
            files={"file": ("test.jpg", io.BytesIO(img_bytes), "image/jpeg")},
            headers={"Authorization": f"Bearer {buyer_auth_token}"},
        )
        assert res.status_code == 403


class TestClassifyEndpointValidation:

    def test_unsupported_extension_rejected(self, client, seller_auth_token):
        res = client.post(
            CLASSIFY_URL,
            files={"file": ("test.gif", io.BytesIO(b"GIF89a"), "image/gif")},
            headers={"Authorization": f"Bearer {seller_auth_token}"},
        )
        assert res.status_code == 422

    def test_wrong_mime_type_rejected(self, client, seller_auth_token):
        img_bytes = _make_jpeg_bytes()
        res = client.post(
            CLASSIFY_URL,
            files={"file": ("test.jpg", io.BytesIO(img_bytes), "application/octet-stream")},
            headers={"Authorization": f"Bearer {seller_auth_token}"},
        )
        assert res.status_code == 422

    def test_empty_file_rejected(self, client, seller_auth_token):
        res = client.post(
            CLASSIFY_URL,
            files={"file": ("test.jpg", io.BytesIO(b""), "image/jpeg")},
            headers={"Authorization": f"Bearer {seller_auth_token}"},
        )
        assert res.status_code == 422

    def test_oversized_file_rejected(self, client, seller_auth_token):
        big = b"\xff\xd8\xff" + b"X" * (11 * 1024 * 1024)  # 11 MB pseudo-JPEG
        res = client.post(
            CLASSIFY_URL,
            files={"file": ("big.jpg", io.BytesIO(big), "image/jpeg")},
            headers={"Authorization": f"Bearer {seller_auth_token}"},
        )
        assert res.status_code == 413


class TestClassifyEndpointRealInference:

    def test_valid_jpeg_returns_200_with_real_prediction(self, client, seller_auth_token):
        """Real JPEG through the API. No mocking."""
        img_bytes = _read_real_test_image("Cardboard")
        res = client.post(
            CLASSIFY_URL,
            files={"file": ("cardboard_test.jpg", io.BytesIO(img_bytes), "image/jpeg")},
            headers={"Authorization": f"Bearer {seller_auth_token}"},
        )
        assert res.status_code == 200
        data = res.json()

        # Required fields
        assert "material" in data
        assert "confidence" in data
        assert "top_predictions" in data
        assert "model_name" in data
        assert "model_version" in data
        assert "prototype" in data
        assert "supported_classes" in data
        assert "limitations" in data
        assert "image_url" in data

        # Semantics
        assert data["prototype"] is True
        assert data["is_fallback"] is False
        assert 0.0 <= data["confidence"] <= 1.0
        assert len(data["top_predictions"]) == 3
        assert data["material"] in data["supported_classes"]

        # Metals must not be in supported_classes
        for metal in ("Aluminum", "Copper", "Steel"):
            assert metal not in data["supported_classes"]

    def test_valid_png_returns_200(self, client, seller_auth_token):
        img_bytes = _make_png_bytes()
        res = client.post(
            CLASSIFY_URL,
            files={"file": ("sample.png", io.BytesIO(img_bytes), "image/png")},
            headers={"Authorization": f"Bearer {seller_auth_token}"},
        )
        assert res.status_code == 200
        assert res.json()["material"] is not None

    def test_top_predictions_ordered_via_api(self, client, seller_auth_token):
        img_bytes = _read_real_test_image("Textile")
        res = client.post(
            CLASSIFY_URL,
            files={"file": ("textile.jpg", io.BytesIO(img_bytes), "image/jpeg")},
            headers={"Authorization": f"Bearer {seller_auth_token}"},
        )
        assert res.status_code == 200
        preds = res.json()["top_predictions"]
        confs = [p["confidence"] for p in preds]
        assert confs == sorted(confs, reverse=True)

    def test_response_material_matches_top_prediction(self, client, seller_auth_token):
        img_bytes = _read_real_test_image("Glass")
        res = client.post(
            CLASSIFY_URL,
            files={"file": ("glass.jpg", io.BytesIO(img_bytes), "image/jpeg")},
            headers={"Authorization": f"Bearer {seller_auth_token}"},
        )
        assert res.status_code == 200
        data = res.json()
        assert data["material"] == data["top_predictions"][0]["material"]

    def test_ewaste_image_returns_supported_class(self, client, seller_auth_token):
        img_bytes = _read_real_test_image("E-waste")
        res = client.post(
            CLASSIFY_URL,
            files={"file": ("ewaste.jpg", io.BytesIO(img_bytes), "image/jpeg")},
            headers={"Authorization": f"Bearer {seller_auth_token}"},
        )
        assert res.status_code == 200
        data = res.json()
        assert data["material"] in [
            "Cardboard", "E-waste", "Glass", "Other", "Paper", "Plastic", "Textile"
        ]


# ── 4. Dedicated Classification Route Tests (/api/classification/predict) ─────

PREDICT_URL = "/api/classification/predict"


class TestDedicatedClassificationPredictEndpoint:

    def test_predict_endpoint_valid_image(self, client):
        """Public predict endpoint returns structured MaterialClassificationPredictResponse."""
        img_bytes = _read_real_test_image("Plastic")
        res = client.post(
            PREDICT_URL,
            files={"file": ("plastic_test.jpg", io.BytesIO(img_bytes), "image/jpeg")},
        )
        assert res.status_code == 200
        data = res.json()

        assert "predicted_class" in data
        assert "confidence" in data
        assert "top_predictions" in data
        assert "model_version" in data
        assert "supported_classes" in data
        assert "prototype" in data
        assert "limitations" in data

        assert data["prototype"] is True
        assert len(data["top_predictions"]) == 3
        assert data["predicted_class"] in data["supported_classes"]
        assert 0.0 <= data["confidence"] <= 1.0

    def test_predict_endpoint_unsupported_extension(self, client):
        res = client.post(
            PREDICT_URL,
            files={"file": ("test.bmp", io.BytesIO(b"BM"), "image/bmp")},
        )
        assert res.status_code == 422

    def test_predict_endpoint_empty_file(self, client):
        res = client.post(
            PREDICT_URL,
            files={"file": ("empty.jpg", io.BytesIO(b""), "image/jpeg")},
        )
        assert res.status_code == 422

    def test_predict_endpoint_corrupted_image(self, client):
        res = client.post(
            PREDICT_URL,
            files={"file": ("corrupt.jpg", io.BytesIO(b"NOT_AN_IMAGE_DATA"), "image/jpeg")},
        )
        assert res.status_code == 422


# ── 5. Regression: existing endpoints still work ──────────────────────────────

class TestExistingEndpointsUnaffected:

    def test_root_status(self, client):
        res = client.get("/")
        assert res.status_code == 200
        assert res.json()["status"] == "operational"

    def test_auth_register_and_login(self, client):
        """Registration and login still work after classification service change."""
        reg_payload = {
            "name": "3H Test Seller Unique",
            "email": "unique_step3h_seller@test.com",
            "password": "Password@123",
            "role": "seller",
            "phone": "9876543219",
            "organization": "3H Corp",
            "city": "Hyderabad",
            "state": "Telangana",
        }
        reg = client.post("/api/auth/register", json=reg_payload)
        assert reg.status_code == 200

        login = client.post("/api/auth/login", json={
            "email": reg_payload["email"],
            "password": reg_payload["password"],
        })
        assert login.status_code == 200
        assert "access_token" in login.json()

    def test_list_materials_public(self, client):
        res = client.get("/api/materials")
        assert res.status_code == 200
        assert isinstance(res.json(), list)

    def test_seller_listings_require_auth(self, client):
        res = client.get("/api/listings/seller/me")
        assert res.status_code == 401

    def test_seller_dashboard_accessible_with_token(self, client, seller_auth_token):
        res = client.get("/api/listings/seller/me",
                         headers={"Authorization": f"Bearer {seller_auth_token}"})
        assert res.status_code == 200
