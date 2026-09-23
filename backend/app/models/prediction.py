"""
Prediction Models (Price Predictions & Demand Predictions)
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, JSON, DateTime, ForeignKey
from backend.app.database import Base


class PricePrediction(Base):
    __tablename__ = "price_predictions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    material_id = Column(String(36), ForeignKey("materials.id"), nullable=True)
    predicted_price_per_kg = Column(Float, nullable=False)
    estimated_total_value = Column(Float, nullable=False)
    input_features = Column(JSON, nullable=True)
    top_factors = Column(JSON, nullable=True)
    model_version = Column(String(50), default="1.0.0")
    created_at = Column(DateTime, default=datetime.utcnow)


class DemandPrediction(Base):
    __tablename__ = "demand_predictions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    material_type = Column(String(100), nullable=False)
    forecast_period = Column(String(50), default="next_month")
    predicted_quantity_kg = Column(Float, nullable=False)
    trend = Column(String(50), default="increasing")  # increasing, stable, decreasing
    demand_category = Column(String(50), default="High")  # High, Moderate, Low
    model_version = Column(String(50), default="1.0.0")
    created_at = Column(DateTime, default=datetime.utcnow)
