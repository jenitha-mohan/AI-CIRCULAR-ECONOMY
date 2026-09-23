"""
Sustainability Metric Model
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime
from backend.app.database import Base


class SustainabilityMetric(Base):
    __tablename__ = "sustainability_metrics"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    metric_key = Column(String(100), unique=True, nullable=False, index=True)
    metric_name = Column(String(200), nullable=False)
    value = Column(Float, default=0.0)
    unit = Column(String(50), nullable=False)
    notes = Column(String(500), nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
