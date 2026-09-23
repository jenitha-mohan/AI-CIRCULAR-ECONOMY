import io
import pytest


def test_list_materials(client):
    res = client.get("/api/materials")
    assert res.status_code == 200
    materials = res.json()
    assert isinstance(materials, list)
    assert len(materials) > 0


def test_create_material_seller_success(client, seller_token):
    headers = {"Authorization": f"Bearer {seller_token}"}
    payload = {
        "material_type": "Aluminum",
        "description": "High purity 6063 aluminum scrap",
        "quantity_kg": 750.0,
        "quality": "High",
        "condition": "Clean",
        "intended_purpose": "Recycling",
        "asking_price": 195.0,
    }
    res = client.post("/api/materials?asking_price=195.0", json=payload, headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["material_type"] == "Aluminum"
    assert data["quantity_kg"] == 750.0
    assert "id" in data

    # Verify that an active listing was automatically created
    listings_res = client.get(f"/api/listings?material_type=Aluminum")
    assert listings_res.status_code == 200
    listings = listings_res.json()
    assert any(l["material_id"] == data["id"] for l in listings)


def test_create_material_buyer_forbidden(client, buyer_token):
    headers = {"Authorization": f"Bearer {buyer_token}"}
    payload = {
        "material_type": "Copper",
        "description": "Scrap",
        "quantity_kg": 100.0,
        "quality": "Medium",
        "condition": "Sorted",
        "intended_purpose": "Recycling",
    }
    res = client.post("/api/materials", json=payload, headers=headers)
    assert res.status_code == 403


def test_upload_image_invalid_extension(client, seller_token):
    headers = {"Authorization": f"Bearer {seller_token}"}
    files = {
        "file": ("script.exe", io.BytesIO(b"malicious_bytes"), "application/x-msdownload")
    }
    res = client.post("/api/materials/upload-image", files=files, headers=headers)
    assert res.status_code == 400
    assert "Invalid file extension" in res.json()["message"]


def test_upload_image_valid(client, seller_token):
    from PIL import Image
    import io

    # Generate a small test image in memory
    img = Image.new("RGB", (100, 100), color=(128, 128, 128))
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format="JPEG")
    img_bytes = img_byte_arr.getvalue()

    headers = {"Authorization": f"Bearer {seller_token}"}
    files = {
        "file": ("aluminum_scrap.jpg", io.BytesIO(img_bytes), "image/jpeg")
    }
    res = client.post("/api/materials/upload-image", files=files, headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "file_path" in data
    assert "classification" in data
    assert "material" in data["classification"]
    assert "confidence" in data["classification"]
