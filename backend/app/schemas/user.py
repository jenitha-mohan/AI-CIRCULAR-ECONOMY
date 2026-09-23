"""
User Schemas
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr


class LocationBase(BaseModel):
    city: str
    state: str
    country: Optional[str] = "India"
    latitude: float
    longitude: float
    postal_code: Optional[str] = None


class LocationResponse(LocationBase):
    id: str

    class Config:
        from_attributes = True


class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str = "seller"  # 'seller', 'buyer', 'admin'
    phone: Optional[str] = None
    organization: Optional[str] = None
    business_type: Optional[str] = None  # Manufacturer, Recycler, Trader, Municipality, Individual
    materials_interested: Optional[str] = None  # Comma-separated or JSON list
    city: Optional[str] = "Coimbatore"
    state: Optional[str] = "Tamil Nadu"
    latitude: Optional[float] = 11.0168
    longitude: Optional[float] = 76.9558


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    role: str
    phone: Optional[str] = None
    organization: Optional[str] = None
    business_type: Optional[str] = None
    materials_interested: Optional[str] = None
    location_id: Optional[str] = None
    location: Optional[LocationResponse] = None
    created_at: datetime

    class Config:
        from_attributes = True

