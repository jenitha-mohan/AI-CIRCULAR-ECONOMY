"""
Prediction and ML Schemas
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field


class PricePredictionRequest(BaseModel):
    material_type: str = Field(..., example="Aluminum")
    weight_kg: float = Field(..., example=500.0)
    quality: str = Field(..., example="High")
    location: str = Field(..., example="Coimbatore")
    demand_level: str = Field(..., example="High")
    historical_price: float = Field(..., example=180.0)
    processing_cost: float = Field(..., example=5.0)
    transportation_distance: float = Field(..., example=20.0)
    month: int = Field(..., example=9)
    seller_type: str = Field(..., example="Business")
    buyer_demand: float = Field(..., example=0.85)
    material_condition: str = Field(..., example="Good")


class PricePredictionResponse(BaseModel):
    predicted_price_per_kg: float
    estimated_min_price: float
    estimated_max_price: float
    price_range_str: str
    estimated_total_value: float
    currency: str = "INR"
    model_name: str
    model_version: str
    mode: str  # 'production' or 'development'
    top_factors: Optional[Dict[str, float]] = None
    disclaimer: str



class ClassificationResponse(BaseModel):
    material: str
    confidence: float
    secondary_classes: Optional[List[Dict[str, Any]]] = None
    model_name: str
    model_version: str
    mode: str
    is_fallback: Optional[bool] = False
    message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class DemandPredictionRequest(BaseModel):
    material_type: str = Field(..., example="Copper")
    forecast_period: Optional[str] = "next_month"
    location: Optional[str] = "Coimbatore"


class DemandPredictionResponse(BaseModel):
    material: str
    forecast_period: str
    predicted_demand_kg: float
    demand_category: str  # High, Moderate, Low
    trend: str  # increasing, stable, decreasing
    model_version: str
    mode: str
    disclaimer: str


class MLPerformanceResponse(BaseModel):
    price_model: Dict[str, Any]
    classification_model: Dict[str, Any]
    demand_model: Dict[str, Any]
    system_status: Dict[str, Any]
