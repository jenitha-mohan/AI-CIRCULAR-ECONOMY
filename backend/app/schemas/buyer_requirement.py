"""
Buyer Requirement Schemas
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from backend.app.schemas.user import UserResponse, LocationResponse


class BuyerRequirementCreate(BaseModel):
    material_type: str
    min_quantity: float
    max_quantity: float
    quality: Optional[str] = "Any"
    purpose: Optional[str] = "Recycling"
    max_price_per_kg: float
    is_active: Optional[bool] = True


class BuyerRequirementUpdate(BaseModel):
    material_type: Optional[str] = None
    min_quantity: Optional[float] = None
    max_quantity: Optional[float] = None
    quality: Optional[str] = None
    purpose: Optional[str] = None
    max_price_per_kg: Optional[float] = None
    is_active: Optional[bool] = None


class BuyerRequirementResponse(BaseModel):
    id: str
    buyer_id: str
    material_type: str
    min_quantity: float
    max_quantity: float
    quality: str
    purpose: str
    max_price_per_kg: float
    location_id: Optional[str] = None
    is_active: bool
    created_at: datetime
    buyer: Optional[UserResponse] = None
    location: Optional[LocationResponse] = None

    class Config:
        from_attributes = True
