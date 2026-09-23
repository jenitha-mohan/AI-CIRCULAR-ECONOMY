"""
Location Model
"""

import uuid
from sqlalchemy import Column, String, Float
from backend.app.database import Base


class Location(Base):
    __tablename__ = "locations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    city = Column(String(100), nullable=False)
    state = Column(String(100), nullable=False)
    country = Column(String(100), default="India")
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    postal_code = Column(String(20), nullable=True)
