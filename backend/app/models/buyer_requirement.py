"""
Buyer Requirement Model
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.database import Base


class BuyerRequirement(Base):
    __tablename__ = "buyer_requirements"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    buyer_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    material_type = Column(String(100), nullable=False, index=True)
    min_quantity = Column(Float, nullable=False)
    max_quantity = Column(Float, nullable=False)
    quality = Column(String(50), default="Any")  # High, Medium, Low, Industrial Grade, Any
    purpose = Column(String(100), default="Recycling")  # Recycling, Upcycling, Direct Reuse, Repurposing
    max_price_per_kg = Column(Float, nullable=False)
    location_id = Column(String(36), ForeignKey("locations.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    buyer = relationship("User", back_populates="buyer_requirements", lazy="joined")
    location = relationship("Location", lazy="joined")
