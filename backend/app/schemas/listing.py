"""
Listing Schemas
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from backend.app.schemas.user import UserResponse
from backend.app.schemas.material import MaterialResponse


class ListingCreate(BaseModel):
    material_id: str
    quantity_available: float
    unit: Optional[str] = "kg"
    asking_price: float
    min_acceptable_price: Optional[float] = None
    ai_estimated_min_price: Optional[float] = None
    ai_estimated_max_price: Optional[float] = None
    status: Optional[str] = "active"


class ListingUpdate(BaseModel):
    quantity_available: Optional[float] = None
    unit: Optional[str] = None
    asking_price: Optional[float] = None
    min_acceptable_price: Optional[float] = None
    ai_estimated_min_price: Optional[float] = None
    ai_estimated_max_price: Optional[float] = None
    status: Optional[str] = None


class ListingResponse(BaseModel):
    id: str
    seller_id: str
    material_id: str
    quantity_available: float
    unit: str = "kg"
    asking_price: float
    min_acceptable_price: Optional[float] = None
    ai_estimated_min_price: Optional[float] = None
    ai_estimated_max_price: Optional[float] = None
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    seller: Optional[UserResponse] = None
    material: Optional[MaterialResponse] = None

    class Config:
        from_attributes = True

