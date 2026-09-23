"""
Machine Learning & AI Services API Router
"""

import os
import json
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.config import settings
from backend.app.database import get_db
from backend.app.schemas.prediction import (
    PricePredictionRequest,
    PricePredictionResponse,
    DemandPredictionRequest,
    DemandPredictionResponse,
    ClassificationResponse,
    MLPerformanceResponse
)
from backend.app.services.price_prediction_service import price_prediction_service
from backend.app.services.classification_service import classification_service
from backend.app.services.demand_prediction_service import demand_prediction_service

router = APIRouter(prefix="/api/ml", tags=["Machine Learning"])


@router.post("/classify-material", response_model=ClassificationResponse)
async def classify_material_image(
    file: UploadFile = File(...)
):
    content = await file.read()
    res = classification_service.classify_image(content, filename=file.filename)
    return res


@router.post("/predict-price", response_model=PricePredictionResponse)
def predict_material_price(
    req: PricePredictionRequest
):
    return price_prediction_service.predict_price(req.model_dump())


@router.post("/predict-demand", response_model=DemandPredictionResponse)
def predict_material_demand(
    req: DemandPredictionRequest
):
    return demand_prediction_service.predict_demand(
        material_type=req.material_type,
        forecast_period=req.forecast_period or "next_month",
        location=req.location or "Coimbatore"
    )


@router.get("/performance", response_model=MLPerformanceResponse)
def get_ml_performance_metrics():
    """
    Returns actual saved model evaluation results from training pipelines.
    No hardcoded fake metrics.
    """
    price_meta_path = os.path.join(settings.MODEL_DIR, "price_model_metadata.json")
    class_meta_path = os.path.join(settings.MODEL_DIR, "classification_metadata.json")
    demand_meta_path = os.path.join(settings.MODEL_DIR, "demand_model_metadata.json")

    price_meta = {}
    if os.path.exists(price_meta_path):
        with open(price_meta_path, "r", encoding="utf-8") as f:
            price_meta = json.load(f)

    class_meta = {}
    if os.path.exists(class_meta_path):
        with open(class_meta_path, "r", encoding="utf-8") as f:
            class_meta = json.load(f)

    demand_meta = {}
    if os.path.exists(demand_meta_path):
        with open(demand_meta_path, "r", encoding="utf-8") as f:
            demand_meta = json.load(f)

    return {
        "price_model": price_meta,
        "classification_model": class_meta,
        "demand_model": demand_meta,
        "system_status": {
            "ml_mode": settings.ML_MODE,
            "models_loaded": {
                "price_model": price_prediction_service.model is not None,
                "classification_model": True,
                "demand_model": demand_prediction_service.model is not None
            }
        }
    }
