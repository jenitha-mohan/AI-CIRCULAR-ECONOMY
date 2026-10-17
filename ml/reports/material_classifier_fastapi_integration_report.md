# STEP 3H — FastAPI 7-Class Material Classifier Integration Report

**Date:** 2026-10-17  
**Project:** AI Circular Economy Marketplace  
**Phase:** STEP 3H — FastAPI Model Integration  

---

## 1. Executive Summary

The genuine MobileNetV2 7-class material classification model has been integrated into the FastAPI backend.

- **Checkpoints Integrated:**
  - Weights: `ml/models/material_classifier_mobilenetv2_7class.pth` (8.7 MB)
  - Metadata: `ml/models/material_classifier_7class_metadata.json`
- **Supported Material Classes (7):**
  `Cardboard`, `E-waste`, `Glass`, `Other`, `Paper`, `Plastic`, `Textile`
- **Excluded Metal Classes (3):**
  `Aluminum`, `Copper`, `Steel` (no training data; zero synthetic data used; disclosed clearly in responses and limitations fields)
- **Test Results:** 57 of 57 integration and regression tests passed (`100% pass rate`).

---

## 2. Endpoints Implemented and Available

### A. Dedicated Classification Endpoint (Public / Unrestricted)
- **Method & Path:** `POST /api/classification/predict`
- **Purpose:** Public AI material classification for recyclable materials.
- **Payload:** `multipart/form-data` with field `file` (JPG, PNG, or WEBP, max 10 MB).
- **Response Schema:** `MaterialClassificationPredictResponse`
```json
{
  "predicted_class": "Cardboard",
  "confidence": 0.8982,
  "top_predictions": [
    {"material": "Cardboard", "confidence": 0.8982, "category": "Fibre"},
    {"material": "Paper", "confidence": 0.0592, "category": "Fibre"},
    {"material": "Other", "confidence": 0.0188, "category": "Mixed"}
  ],
  "model_version": "7class-mobilenetv2-v1",
  "supported_classes": ["Cardboard", "E-waste", "Glass", "Other", "Paper", "Plastic", "Textile"],
  "prototype": true,
  "limitations": "This is a 7-class prototype. Aluminum, Copper, and Steel are not supported as dedicated output classes. Images of these metals may be misclassified as Other or another class.",
  "category": "Fibre",
  "model_name": "MobileNetV2"
}
```

### B. Seller Listing Classification Endpoint (Role-Protected)
- **Method & Path:** `POST /api/seller/materials/classify`
- **Security:** Requires valid JWT with role `seller` or `admin`. Buyers receive HTTP 403 Forbidden. Unauthenticated requests receive HTTP 401 Unauthorized.
- **Safe File Storage:** Saves uploaded images using UUID-generated filenames in `uploads/materials/` to prevent path traversal and arbitrary code execution.
- **Response:** Includes material classification, top-3 predictions, confidence, safe image URL, prototype flags, and limitations.

---

## 3. Real Inference & Security Architecture

1. **Single Startup Model Loading:**
   The `MaterialClassificationService` singleton loads PyTorch weights and class metadata once at import/application startup into memory. No per-request re-initialization or retraining occurs.
2. **Deterministic Preprocessing:**
   Exactly reproduces training transforms:
   - Resize(256) -> CenterCrop(224)
   - ToTensor()
   - Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
3. **Upload Validation:**
   - Allowed extensions: `.jpg`, `.jpeg`, `.png`, `.webp`
   - Allowed MIME types: `image/jpeg`, `image/png`, `image/webp`
   - File size ceiling: 10 MB (rejects with HTTP 413)
   - Empty files rejected with HTTP 422
   - Corrupted/unidentifiable image payloads handled safely with HTTP 422 Unprocessable Entity
4. **No Price Predictions & Price Separation:**
   No price estimates are returned by the vision classifier. Asking prices remain 100% seller-controlled.

---

## 4. Test Verification Summary

Command executed:
```powershell
python -m pytest tests/test_mobilenetv2_classification.py tests/test_ai_classification.py tests/test_seller_listing.py -v
```

### Results
- **Total Tests Executed:** 57
- **Passed:** 57 (100%)
- **Failed:** 0
- **Duration:** 17.86s

### Breakdown:
1. `tests/test_mobilenetv2_classification.py`: 32 passed
   - Service initialization & metadata verification: 4 tests
   - Real inference on actual dataset images (Cardboard, E-waste, Glass, Plastic, Textile): 8 tests
   - Validation & error handling (corrupted image, bad mime, empty file, oversized file): 6 tests
   - Role-based access control (401 unauth, 403 buyer): 2 tests
   - API endpoints structure & semantics: 7 tests
   - Existing endpoints regression (root, auth register/login, materials, seller dashboard): 5 tests
2. `tests/test_ai_classification.py`: 11 passed
   - Seller upload, manual override, asking price independence, no price leak in classify response
3. `tests/test_seller_listing.py`: 14 passed
   - Seller listing lifecycle, role boundaries, image upload integration

---

## 5. Files Changed / Created

| File | Status | Description |
|---|---|---|
| `backend/app/services/classification_service.py` | Modified | Replaced heuristic classifier with real MobileNetV2 PyTorch inference engine |
| `backend/app/api/classification.py` | Created | Added dedicated `POST /api/classification/predict` router |
| `backend/app/api/seller_classify.py` | Modified | Updated response to expose top-3 predictions, prototype flag, supported classes, and metal limitations |
| `backend/app/api/materials.py` | Modified | Added safe error fallback handling for image upload endpoint |
| `backend/app/schemas/prediction.py` | Modified | Added `MaterialClassificationPredictResponse` and `PredictionItem` Pydantic schemas |
| `backend/app/schemas/user.py` | Modified | Added `country` field to `UserRegister` schema for robust registration handling |
| `backend/app/main.py` | Modified | Registered `classification_router` |
| `tests/test_mobilenetv2_classification.py` | Created | Full 32-test integration test suite with genuine PyTorch inference |
| `tests/test_ai_classification.py` | Modified | Used valid dynamically generated JPEG bytes in place of truncated sample |

---

## 6. How to Start the Backend

```powershell
# Activate your python environment if applicable
# Start the FastAPI application with Uvicorn
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```
Interactive API docs are available at `http://localhost:8000/docs`.
