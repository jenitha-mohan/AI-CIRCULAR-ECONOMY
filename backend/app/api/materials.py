"""
Materials Management API Router
"""

import os
import uuid
import aiofiles
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from sqlalchemy.orm import Session

from backend.app.config import settings
from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.models.material import Material, MaterialImage
from backend.app.models.listing import Listing
from backend.app.models.category import MaterialCategory
from backend.app.schemas.material import MaterialCreate, MaterialUpdate, MaterialResponse
from backend.app.dependencies import get_current_user, require_role
from backend.app.services.classification_service import classification_service
from backend.app.services.price_prediction_service import price_prediction_service

router = APIRouter(prefix="/api/materials", tags=["Materials"])

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


@router.post("/upload-image")
async def upload_material_image(
    file: UploadFile = File(...),
    current_user: User = Depends(require_role(["seller", "admin"]))
):
    # 1. Validate extension
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file extension '{ext}'. Allowed: {list(ALLOWED_EXTENSIONS)}"
        )

    # 2. Validate MIME type
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid MIME type '{file.content_type}'. Allowed: {list(ALLOWED_MIME_TYPES)}"
        )

    # 3. Read content and check size
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds maximum allowed 10MB limit."
        )

    # 4. Generate unique filename
    unique_name = f"{uuid.uuid4()}{ext}"
    save_dir = os.path.join(settings.UPLOAD_DIR, "materials")
    os.makedirs(save_dir, exist_ok=True)
    file_path = os.path.join(save_dir, unique_name)

    async with aiofiles.open(file_path, "wb") as f:
        await f.write(content)

    # 5. Run AI Material Classification
    classification_res = classification_service.classify_image(content, filename=file.filename)

    rel_url = f"/uploads/materials/{unique_name}"
    return {
        "file_path": rel_url,
        "filename": unique_name,
        "classification": classification_res
    }


@router.post("", response_model=MaterialResponse)
def create_material(
    material_in: MaterialCreate,
    asking_price: Optional[float] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["seller", "admin"]))
):
    # Match category
    cat = db.query(MaterialCategory).filter(
        MaterialCategory.name.ilike(f"%{material_in.material_type}%")
    ).first()

    ai_res = price_prediction_service.predict_price({
        "material_type": material_in.material_type,
        "weight_kg": material_in.quantity_kg,
        "quality": material_in.quality,
        "location": current_user.location.city if current_user.location else "Coimbatore",
        "demand_level": "Moderate",
        "historical_price": material_in.predicted_price or 40.0,
        "processing_cost": 5.0,
        "transportation_distance": 20.0,
        "month": 9,
        "seller_type": "Business",
        "buyer_demand": 0.8,
        "material_condition": material_in.condition
    })
    ai_pred = ai_res["predicted_price_per_kg"]
    ai_min = ai_res.get("estimated_min_price", round(ai_pred * 0.95, 2))
    ai_max = ai_res.get("estimated_max_price", round(ai_pred * 1.05, 2))

    material = Material(
        seller_id=current_user.id,
        category_id=cat.id if cat else None,
        material_type=material_in.material_type,
        description=material_in.description,
        quantity_kg=material_in.quantity_kg,
        quality=material_in.quality,
        condition=material_in.condition,
        intended_purpose=material_in.intended_purpose,
        image_url=material_in.image_url,
        predicted_price=material_in.predicted_price or ai_pred,
        status=material_in.status or "available"
    )
    db.add(material)
    db.flush()

    # Automatically create marketplace listing
    final_ask_price = asking_price if asking_price is not None else (material_in.predicted_price or ai_pred)
    listing = Listing(
        seller_id=current_user.id,
        material_id=material.id,
        quantity_available=material.quantity_kg,
        asking_price=final_ask_price,
        ai_estimated_min_price=ai_min,
        ai_estimated_max_price=ai_max,
        status="active"
    )
    db.add(listing)

    db.commit()
    db.refresh(material)
    return material


@router.get("", response_model=List[MaterialResponse])
def list_materials(
    material_type: Optional[str] = None,
    quality: Optional[str] = None,
    condition: Optional[str] = None,
    status: Optional[str] = None,
    seller_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Material)
    if material_type:
        query = query.filter(Material.material_type.ilike(f"%{material_type}%"))
    if quality:
        query = query.filter(Material.quality == quality)
    if condition:
        query = query.filter(Material.condition == condition)
    if status:
        query = query.filter(Material.status == status)
    if seller_id:
        query = query.filter(Material.seller_id == seller_id)

    return query.order_by(Material.created_at.desc()).all()


@router.get("/{material_id}", response_model=MaterialResponse)
def get_material_by_id(material_id: str, db: Session = Depends(get_db)):
    material = db.query(Material).filter(Material.id == material_id).first()
    if not material:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Material not found")
    return material


@router.put("/{material_id}", response_model=MaterialResponse)
def update_material(
    material_id: str,
    material_in: MaterialUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    material = db.query(Material).filter(Material.id == material_id).first()
    if not material:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Material not found")

    if material.seller_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to edit this material")

    update_data = material_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(material, field, value)

    db.commit()
    db.refresh(material)
    return material


@router.delete("/{material_id}")
def delete_material(
    material_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    material = db.query(Material).filter(Material.id == material_id).first()
    if not material:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Material not found")

    if material.seller_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this material")

    db.delete(material)
    db.commit()
    return {"success": True, "message": "Material deleted successfully"}
