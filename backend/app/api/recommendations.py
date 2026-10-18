from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models.material import Material
from backend.app.models.user import User
from backend.app.schemas.recommendation import BuyerRecommendationItem, MaterialRecommendationItem
from backend.app.services.recommendation_service import recommendation_service
from backend.app.dependencies import get_current_user

router = APIRouter(prefix="/api/recommendations", tags=["Recommendations"])


@router.get("/buyers/{material_id}", response_model=List[BuyerRecommendationItem])
def get_buyer_recommendations_for_material(
    material_id: str,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Find matching buyers for a given material lot.
    Authorized seller or admin only.
    """
    material = db.query(Material).filter(Material.id == material_id).first()
    if not material:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Material not found")

    if current_user.role != "admin" and material.seller_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view matching buyers for another seller's material.")

    return recommendation_service.recommend_buyers_for_material(db, material, limit=limit)


@router.get("/materials/{buyer_id}", response_model=List[MaterialRecommendationItem])
def get_material_recommendations_for_buyer(
    buyer_id: str,
    limit: int = 12,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve personalized feedstock recommendations for an authenticated buyer.
    Strictly isolated: a buyer can only request their own recommendations.
    """
    if current_user.role != "admin" and current_user.id != buyer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: You cannot view recommendations for another buyer."
        )

    buyer = db.query(User).filter(User.id == buyer_id).first()
    if not buyer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Buyer not found")

    return recommendation_service.recommend_materials_for_buyer(db, buyer_id, limit=limit)

