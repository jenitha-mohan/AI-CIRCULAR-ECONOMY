"""
Transaction Schemas
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from backend.app.schemas.user import UserResponse
from backend.app.schemas.listing import ListingResponse


class TransactionCreate(BaseModel):
    listing_id: Optional[str] = None
    offer_id: Optional[str] = None
    seller_id: str
    material_type: str
    quantity_kg: float
    agreed_price: float


class TransactionPickupSchedule(BaseModel):
    pickup_location: str
    pickup_date: datetime
    pickup_instructions: Optional[str] = None


class TransactionStatusUpdate(BaseModel):
    status: str  # CONFIRMED, PICKUP_SCHEDULED, IN_TRANSIT, DELIVERED, COMPLETED, CANCELLED


class TransactionResponse(BaseModel):
    id: str
    buyer_id: str
    seller_id: str
    listing_id: Optional[str] = None
    offer_id: Optional[str] = None
    material_type: str
    quantity_kg: float
    agreed_price: float
    total_amount: float
    status: str  # CONFIRMED, PICKUP_SCHEDULED, IN_TRANSIT, DELIVERED, COMPLETED, CANCELLED
    pickup_location: Optional[str] = None
    pickup_date: Optional[datetime] = None
    pickup_instructions: Optional[str] = None
    co2_avoided_kg: float
    landfill_diverted_kg: float
    created_at: datetime
    updated_at: Optional[datetime] = None
    buyer: Optional[UserResponse] = None
    seller: Optional[UserResponse] = None
    listing: Optional[ListingResponse] = None

    class Config:
        from_attributes = True

