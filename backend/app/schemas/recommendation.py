"""
Recommendation Schemas
"""

from typing import List, Optional
from pydantic import BaseModel
from backend.app.schemas.user import UserResponse
from backend.app.schemas.material import MaterialResponse


class BuyerRecommendationItem(BaseModel):
    buyer_id: str
    buyer_name: str
    organization: Optional[str] = None
    material: str
    match_score: float  # Scale 0.0 to 1.0 (or %)
    distance_km: float
    required_quantity: float
    required_quality: str
    reasons: List[str]
    buyer: Optional[UserResponse] = None


class MaterialRecommendationItem(BaseModel):
    material_id: str
    material_type: str
    seller_name: str
    seller_organization: Optional[str] = None
    quantity_kg: float
    quality: str
    condition: str
    asking_price: Optional[float] = None
    predicted_price: Optional[float] = None
    match_score: float
    distance_km: float
    reasons: List[str]
    material: Optional[MaterialResponse] = None
