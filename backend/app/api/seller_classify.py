"""
Seller Material Classification API
Dedicated endpoint: POST /api/seller/materials/classify
Returns AI material identification result for seller-uploaded images.

Security:
- JWT authentication required
- SELLER role required (buyers get 403)
- MIME type + extension + size validation
- Safe filename generation (uuid4)
- No path traversal (saved to controlled directory)
- No price prediction in this module
"""

import os
import uuid
import aiofiles
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from backend.app.config import settings
from backend.app.models.user import User
from backend.app.dependencies import require_role
from backend.app.services.classification_service import classification_service

router = APIRouter(prefix="/api/seller/materials", tags=["Seller - Material Classification"])

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


@router.post(
    "/classify",
    summary="AI Material Identification",
    description=(
        "Upload a waste material image. The AI will identify the material type, "
        "category, and confidence. The seller must verify and can override the result "
        "before creating a listing. No price prediction is performed."
    ),
)
async def classify_material_image(
    file: UploadFile = File(..., description="JPG / JPEG / PNG / WEBP image, max 10 MB"),
    current_user: User = Depends(require_role(["seller", "admin"])),
):
    """
    Protected endpoint — SELLER role only.

    Returns:
        material  : detected material name
        category  : broad waste category (Metal, Polymer, Fibre …)
        confidence: float 0–1
        model info: model_name, model_version
    """
    # ── 1. Extension validation ──────────────────────────────────────────────
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No filename provided.",
        )
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Unsupported file type '{ext}'. Please upload a JPG, PNG, or WEBP image.",
        )

    # ── 2. MIME type validation ───────────────────────────────────────────────
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid content type '{file.content_type}'. Allowed: image/jpeg, image/png, image/webp.",
        )

    # ── 3. Read & size check ─────────────────────────────────────────────────
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Image is too large. Maximum allowed size is 10 MB.",
        )
    if len(content) == 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Uploaded file is empty.",
        )

    # ── 4. Safe filename + save ───────────────────────────────────────────────
    safe_name = f"{uuid.uuid4()}{ext}"          # no original filename used
    save_dir = os.path.join(settings.UPLOAD_DIR, "materials")
    os.makedirs(save_dir, exist_ok=True)
    file_path = os.path.join(save_dir, safe_name)

    async with aiofiles.open(file_path, "wb") as f:
        await f.write(content)

    # ── 5. AI Classification ─────────────────────────────────────────────────
    try:
        result = classification_service.classify_image(content, filename=file.filename)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Material identification failed. Please try another image.",
        ) from exc

    # ── 6. Return clean response (no price fields) ───────────────────────────
    return {
        "material":         result["material"],
        "category":         result.get("category", "Mixed"),
        "confidence":       result["confidence"],
        "image_url":        f"/uploads/materials/{safe_name}",
        "secondary_classes": result.get("secondary_classes", []),
        "model_name":       result.get("model_name"),
        "model_version":    result.get("model_version"),
        "is_fallback":      result.get("is_fallback", False),
        # seller_id is NEVER returned — no sensitive data leakage
    }
