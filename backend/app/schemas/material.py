"""
Material Schemas
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel
from backend.app.schemas.user import UserResponse


class CategoryResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    co2_factor_kg_per_kg: float
    landfill_diversion_factor: float

    class Config:
        from_attributes = True


class MaterialImageResponse(BaseModel):
    id: str
    file_path: str
    detected_class: Optional[str] = None
    confidence: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True


class MaterialCreate(BaseModel):
    material_type: str
    description: Optional[str] = None
    quantity_kg: float
    quality: str = "Medium"  # High, Medium, Low, Industrial Grade
    condition: str = "Sorted"  # Clean, Contaminated, Sorted, Mixed, Baled
    intended_purpose: str = "Recycling"  # Recycling, Upcycling, Direct Reuse, Repurposing
    image_url: Optional[str] = None
    predicted_price: Optional[float] = None
    status: Optional[str] = "available"


class MaterialUpdate(BaseModel):
    material_type: Optional[str] = None
    description: Optional[str] = None
    quantity_kg: Optional[float] = None
    quality: Optional[str] = None
    condition: Optional[str] = None
    intended_purpose: Optional[str] = None
    image_url: Optional[str] = None
    predicted_price: Optional[float] = None
    status: Optional[str] = None


class MaterialResponse(BaseModel):
    id: str
    seller_id: str
    category_id: Optional[str] = None
    material_type: str
    description: Optional[str] = None
    quantity_kg: float
    quality: str
    condition: str
    intended_purpose: str
    image_url: Optional[str] = None
    predicted_price: Optional[float] = None
    status: str
    created_at: datetime
    seller: Optional[UserResponse] = None
    category: Optional[CategoryResponse] = None
    images: Optional[List[MaterialImageResponse]] = []

    class Config:
        from_attributes = True
