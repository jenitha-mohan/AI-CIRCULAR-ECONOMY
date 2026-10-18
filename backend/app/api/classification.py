"""
Material Classification API Router
Dedicated routes for 7-class MobileNetV2 material classification.
Supports POST /api/classification/predict
"""

import os
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from backend.app.schemas.prediction import MaterialClassificationPredictResponse
from backend.app.services.classification_service import classification_service

router = APIRouter(prefix="/api/classification", tags=["Material Classification"])

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


@router.post(
    "/predict",
    response_model=MaterialClassificationPredictResponse,
    summary="Predict Recyclable Material (7-Class MobileNetV2 Prototype)",
    description=(
        "Upload an image of recyclable waste material. Evaluated using a genuine "
        "trained MobileNetV2 PyTorch transfer-learning prototype. "
        "Supported classes: Cardboard, E-waste, Glass, Other, Paper, Plastic, Textile. "
        "Limitation: Aluminum, Copper, and Steel are excluded from dedicated output classes."
    ),
)
async def predict_material(
    file: UploadFile = File(..., description="JPG, PNG, or WEBP image (max 10 MB)")
):
    # 1. Filename & Extension validation
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No filename provided.",
        )
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Unsupported file extension '{ext}'. Allowed extensions: {sorted(ALLOWED_EXTENSIONS)}",
        )

    # 2. MIME type validation
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid MIME type '{file.content_type}'. Allowed types: {sorted(ALLOWED_MIME_TYPES)}",
        )

    # 3. Read & file size validation
    content = await file.read()
    if len(content) == 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Uploaded file is empty.",
        )
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File size exceeds maximum allowed 10 MB limit.",
        )

    # 4. Run real inference
    try:
        raw_res = classification_service.classify_image(content, filename=file.filename)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Material classification failed: {str(exc)}",
        ) from exc

    # 5. Format structured response matching MaterialClassificationPredictResponse
    return {
        "predicted_class": raw_res["material"],
        "confidence": raw_res["confidence"],
        "top_predictions": raw_res.get("top_predictions", []),
        "model_version": raw_res.get("model_version", "7class-mobilenetv2-v1"),
        "supported_classes": raw_res.get("supported_classes", []),
        "prototype": raw_res.get("prototype", True),
        "limitations": raw_res.get("limitations", ""),
        "category": raw_res.get("category", "Mixed"),
        "model_name": raw_res.get("model_name", "MobileNetV2"),
        "is_uncertain": raw_res.get("is_uncertain", False),
        "uncertainty_warning": raw_res.get("uncertainty_warning"),
    }
