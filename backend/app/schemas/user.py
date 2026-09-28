"""
User Schemas with Strong Validation and Role Access Constraints
"""

import re
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict


class LocationBase(BaseModel):
    city: str = Field(..., min_length=2, max_length=100)
    state: str = Field(..., min_length=2, max_length=100)
    country: Optional[str] = "India"
    latitude: float = Field(default=11.0168, ge=-90.0, le=90.0)
    longitude: float = Field(default=76.9558, ge=-180.0, le=180.0)
    postal_code: Optional[str] = None


class LocationResponse(LocationBase):
    id: str
    model_config = ConfigDict(from_attributes=True)


class UserRegister(BaseModel):
    name: str = Field(..., min_length=2, max_length=150, description="Full name or representative name")
    email: EmailStr = Field(..., description="Unique email address")
    password: str = Field(..., min_length=8, max_length=128, description="Strong password")
    role: str = Field(default="seller", description="Role: 'seller', 'buyer', or 'admin'")
    phone: str = Field(..., max_length=25, description="Contact phone number (Required)")
    organization: str = Field(..., max_length=200, description="Company or business name (Required)")
    business_type: Optional[str] = Field(default=None, max_length=100, description="Manufacturer, Recycler, Trader, etc.")
    materials_interested: Optional[str] = Field(default=None, max_length=500, description="Categories interested in (Buyers)")
    city: str = Field(..., description="Location City (Required)")
    state: str = Field(default="Tamil Nadu", description="Location State")
    latitude: Optional[float] = 11.0168
    longitude: Optional[float] = 76.9558

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v_clean = v.strip()
        if not v_clean or len(v_clean) < 2:
            raise ValueError("Name must be at least 2 characters long and not empty spaces.")
        return v_clean

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long.")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter.")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter.")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit.")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>\-_+=\[\]\\/~`']", v):
            raise ValueError("Password must contain at least one special character.")
        return v

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        v_clean = str(v).strip().lower()
        if v_clean not in ["seller", "buyer"]:
            raise ValueError("Role must be 'seller' or 'buyer'. Admins cannot be registered publicly.")
        return v_clean

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        v_clean = re.sub(r"[^\d+\-\s()]", "", v.strip())
        digits_only = re.sub(r"\D", "", v_clean)
        # Assuming Indian phone numbers are usually 10 digits (without country code) or 12/13 with code
        if len(digits_only) < 10 or len(digits_only) > 15:
            raise ValueError("Phone number must contain between 10 and 15 digits.")
        return v_clean

    @field_validator("organization")
    @classmethod
    def validate_organization(cls, v: str) -> str:
        v_clean = v.strip()
        if not v_clean:
            raise ValueError("Company name is required.")
        return v_clean

    def get_company_name(self) -> str:
        return self.organization


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1)


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
    company_name: Optional[str] = None
    business_type: Optional[str] = None
    materials_interested: Optional[str] = None
    location_id: Optional[str] = None
    location: Optional[LocationResponse] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
