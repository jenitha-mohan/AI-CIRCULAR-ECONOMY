"""
User Model with Role-Based Access Control and Company Mapping
"""

import uuid
from enum import Enum
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from backend.app.database import Base


class UserRole(str, Enum):
    SELLER = "seller"
    BUYER = "buyer"
    ADMIN = "admin"

    @classmethod
    def from_str(cls, value: str):
        if not value:
            return cls.SELLER
        val_lower = str(value).strip().lower()
        for member in cls:
            if member.value == val_lower:
                return member
        return cls.SELLER


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(150), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), default=UserRole.SELLER.value, index=True, nullable=False)  # 'seller', 'buyer', 'admin'
    phone = Column(String(50), nullable=True)
    organization = Column(String(200), nullable=True)
    business_type = Column(String(100), nullable=True)  # Manufacturer, Recycler, Trader, Municipality, Individual
    materials_interested = Column(String(500), nullable=True)  # Comma-separated list or JSON
    location_id = Column(String(36), ForeignKey("locations.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    location = relationship("Location", lazy="joined")
    materials = relationship("Material", back_populates="seller", cascade="all, delete-orphan")
    buyer_requirements = relationship("BuyerRequirement", back_populates="buyer", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_users_email_role", "email", "role"),
    )

    @property
    def company_name(self) -> str:
        """Alias for organization."""
        return self.organization or ""

    @company_name.setter
    def company_name(self, value: str):
        self.organization = value

    def to_safe_dict(self) -> dict:
        """Serialize user object without sensitive credentials."""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "phone": self.phone,
            "company_name": self.organization,
            "organization": self.organization,
            "business_type": self.business_type,
            "materials_interested": self.materials_interested,
            "city": self.location.city if self.location else None,
            "state": self.location.state if self.location else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"
