"""
AI Recommendations API Router
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models.material import Material
from backend.app.models.user import User
from backend.app.schemas.recommendation import BuyerRecommendationItem, MaterialRecommendationItem
from backend.app.services.recommendation_service import recommendation_service

router = APIRouter(prefix="/api/recommendations", tags=["Recommendations"])


@router.get("/buyers/{material_id}", response_model=List[BuyerRecommendationItem])
def get_buyer_recommendations_for_material(
    material_id: str,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    material = db.query(Material).filter(Material.id == material_id).first()
    if not material:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Material not found")

    return recommendation_service.recommend_buyers_for_material(db, material, limit=limit)


@router.get("/materials/{buyer_id}", response_model=List[MaterialRecommendationItem])
def get_material_recommendations_for_buyer(
    buyer_id: str,
    limit: int = 12,
    db: Session = Depends(get_db)
):
    buyer = db.query(User).filter(User.id == buyer_id).first()
    if not buyer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Buyer not found")

    return recommendation_service.recommend_materials_for_buyer(db, buyer_id, limit=limit)
