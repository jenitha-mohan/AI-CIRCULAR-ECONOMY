"""
Offer & Negotiation Schemas
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
from backend.app.schemas.user import UserResponse
from backend.app.schemas.listing import ListingResponse


class OfferCreate(BaseModel):
    listing_id: str = Field(..., description="ID of the target active seller listing")
    offered_quantity: float = Field(..., gt=0, description="Quantity buyer wishes to procure")
    offered_price: float = Field(..., gt=0, description="Proposed price per unit in INR")
    message: Optional[str] = Field(None, description="Optional note or logistics detail from buyer")


class OfferCounter(BaseModel):
    counter_price: float = Field(..., gt=0, description="Counter-proposed price per unit in INR")
    counter_quantity: Optional[float] = Field(None, gt=0, description="Optionally revised quantity")
    message: Optional[str] = Field(None, description="Message explaining counter-proposal")


class OfferReject(BaseModel):
    message: Optional[str] = Field(None, description="Reason for rejection")


class OfferHistoryResponse(BaseModel):
    id: str
    offer_id: str
    sender_id: str
    receiver_id: str
    price: float
    quantity: float
    message: Optional[str] = None
    action: str  # OFFER, COUNTER, ACCEPT, REJECT, CANCEL
    created_at: datetime
    sender: Optional[UserResponse] = None
    receiver: Optional[UserResponse] = None

    class Config:
        from_attributes = True


class OfferResponse(BaseModel):
    id: str
    listing_id: str
    buyer_id: str
    seller_id: str
    offered_quantity: float
    offered_price: float
    message: Optional[str] = None
    status: str  # PENDING, COUNTERED, ACCEPTED, REJECTED, CANCELLED, EXPIRED
    created_at: datetime
    updated_at: Optional[datetime] = None
    listing: Optional[ListingResponse] = None
    buyer: Optional[UserResponse] = None
    seller: Optional[UserResponse] = None
    history: Optional[List[OfferHistoryResponse]] = None

    class Config:
        from_attributes = True
