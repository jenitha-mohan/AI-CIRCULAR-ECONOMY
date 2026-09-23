"""
Material Category Model
"""

import uuid
from sqlalchemy import Column, String, Float, Text
from backend.app.database import Base


class MaterialCategory(Base):
    __tablename__ = "material_categories"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    co2_factor_kg_per_kg = Column(Float, default=1.5)  # kg CO2 avoided per kg recycled
    landfill_diversion_factor = Column(Float, default=0.95)  # kg diverted per kg recycled
