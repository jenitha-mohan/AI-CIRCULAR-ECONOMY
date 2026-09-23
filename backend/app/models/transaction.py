"""
Transaction Model
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    buyer_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    seller_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    listing_id = Column(String(36), ForeignKey("seller_listings.id"), nullable=True, index=True)
    offer_id = Column(String(36), ForeignKey("offers.id"), nullable=True, index=True)
    material_type = Column(String(100), nullable=False)
    quantity_kg = Column(Float, nullable=False)
    agreed_price = Column(Float, nullable=False)  # Final negotiated INR / kg
    total_amount = Column(Float, nullable=False)  # INR (quantity_kg * agreed_price)
    status = Column(String(50), default="CONFIRMED", index=True)  # CONFIRMED, PICKUP_SCHEDULED, IN_TRANSIT, DELIVERED, COMPLETED, CANCELLED
    pickup_location = Column(String(255), nullable=True)
    pickup_date = Column(DateTime, nullable=True)
    pickup_instructions = Column(String(1000), nullable=True)
    co2_avoided_kg = Column(Float, default=0.0)
    landfill_diverted_kg = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    buyer = relationship("User", foreign_keys=[buyer_id], lazy="joined")
    seller = relationship("User", foreign_keys=[seller_id], lazy="joined")
    listing = relationship("Listing", back_populates="transactions", lazy="joined")
    offer = relationship("Offer", back_populates="transaction", lazy="joined")
    messages = relationship("ChatMessage", back_populates="transaction", cascade="all, delete-orphan", order_by="ChatMessage.created_at.asc()")

