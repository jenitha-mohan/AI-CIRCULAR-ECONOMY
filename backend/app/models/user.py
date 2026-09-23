"""
User Model
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(150), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), default="seller", nullable=False)  # 'seller', 'buyer', 'admin'
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
