"""
Material & MaterialImage Models
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.database import Base


class Material(Base):
    __tablename__ = "materials"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    seller_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    category_id = Column(String(36), ForeignKey("material_categories.id"), nullable=True)
    material_type = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    quantity_kg = Column(Float, nullable=False)
    quality = Column(String(50), default="Medium")  # High, Medium, Low, Industrial Grade
    condition = Column(String(50), default="Sorted")  # Clean, Contaminated, Sorted, Mixed, Baled
    intended_purpose = Column(String(100), default="Recycling")  # Recycling, Upcycling, Direct Reuse, Repurposing
    image_url = Column(String(500), nullable=True)
    predicted_price = Column(Float, nullable=True)
    status = Column(String(50), default="available")  # draft, available, in_negotiation, sold
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    seller = relationship("User", back_populates="materials")
    category = relationship("MaterialCategory", lazy="joined")
    images = relationship("MaterialImage", back_populates="material", cascade="all, delete-orphan")
    listings = relationship("Listing", back_populates="material", cascade="all, delete-orphan")


class MaterialImage(Base):
    __tablename__ = "material_images"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    material_id = Column(String(36), ForeignKey("materials.id"), nullable=False)
    file_path = Column(String(500), nullable=False)
    detected_class = Column(String(100), nullable=True)
    confidence = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    material = relationship("Material", back_populates="images")
