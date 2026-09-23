"""
Offer & OfferHistory Models for Buyer/Seller Negotiation
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.database import Base


class Offer(Base):
    __tablename__ = "offers"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    listing_id = Column(String(36), ForeignKey("seller_listings.id"), nullable=False, index=True)
    buyer_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    seller_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    offered_quantity = Column(Float, nullable=False)
    offered_price = Column(Float, nullable=False)  # Current proposed price per unit (INR)
    message = Column(Text, nullable=True)
    status = Column(String(50), default="PENDING", index=True)  # PENDING, COUNTERED, ACCEPTED, REJECTED, CANCELLED, EXPIRED
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    listing = relationship("Listing", back_populates="offers", lazy="joined")
    buyer = relationship("User", foreign_keys=[buyer_id], lazy="joined")
    seller = relationship("User", foreign_keys=[seller_id], lazy="joined")
    history = relationship("OfferHistory", back_populates="offer", cascade="all, delete-orphan", order_by="OfferHistory.created_at.asc()")
    transaction = relationship("Transaction", back_populates="offer", uselist=False)


class OfferHistory(Base):
    __tablename__ = "offer_history"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    offer_id = Column(String(36), ForeignKey("offers.id"), nullable=False, index=True)
    sender_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    receiver_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    price = Column(Float, nullable=False)  # Proposed price per unit (INR)
    quantity = Column(Float, nullable=False)
    message = Column(Text, nullable=True)
    action = Column(String(50), nullable=False)  # OFFER, COUNTER, ACCEPT, REJECT, CANCEL
    created_at = Column(DateTime, default=datetime.utcnow)

    offer = relationship("Offer", back_populates="history")
    sender = relationship("User", foreign_keys=[sender_id], lazy="joined")
    receiver = relationship("User", foreign_keys=[receiver_id], lazy="joined")
