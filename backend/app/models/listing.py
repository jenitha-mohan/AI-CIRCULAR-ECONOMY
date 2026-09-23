"""
Listing Model
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.database import Base


class Listing(Base):
    __tablename__ = "seller_listings"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    seller_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    material_id = Column(String(36), ForeignKey("materials.id"), nullable=False, index=True)
    quantity_available = Column(Float, nullable=False)
    unit = Column(String(20), default="kg", nullable=False)
    asking_price = Column(Float, nullable=False)  # Seller-decided asking price per unit (INR)
    min_acceptable_price = Column(Float, nullable=True)  # Optional seller threshold
    ai_estimated_min_price = Column(Float, nullable=True)  # Read-only AI lower guidance
    ai_estimated_max_price = Column(Float, nullable=True)  # Read-only AI upper guidance
    status = Column(String(50), default="active", index=True)  # active, in_negotiation, paused, sold, closed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    seller = relationship("User", lazy="joined")
    material = relationship("Material", back_populates="listings", lazy="joined")
    transactions = relationship("Transaction", back_populates="listing")
    offers = relationship("Offer", back_populates="listing", cascade="all, delete-orphan")

