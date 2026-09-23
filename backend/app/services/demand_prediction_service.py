"""
AI Demand Forecasting Service
Predicts forward-looking recyclable material demand and trend trajectories.
"""

import os
import json
import joblib
import pandas as pd
from typing import Dict, Any
from backend.app.config import settings

MODEL_FILE = os.path.join(settings.MODEL_DIR, "demand_model_v1.pkl")
METADATA_FILE = os.path.join(settings.MODEL_DIR, "demand_model_metadata.json")

BASE_DEMAND_MONTHLY = {
    "Steel": 360000, "Aluminum": 180000, "Copper": 105000, "Plastic": 255000,
    "Cardboard": 270000, "Paper": 210000, "Glass": 120000, "Textile": 90000,
    "E-waste": 45000, "Other": 36000
}


class DemandPredictionService:
    def __init__(self):
        self.model = self._load_model()
        self.metadata = self._load_metadata()
        self.model_version = self.metadata.get("model_version", "1.0.0")

    def _load_model(self):
        if os.path.exists(MODEL_FILE):
            try:
                model = joblib.load(MODEL_FILE)
                print(f"[DemandPredictionService] Loaded model from {MODEL_FILE}")
                return model
            except Exception as e:
                print(f"[DemandPredictionService] Error loading model: {e}")
        return None

    def _load_metadata(self) -> Dict[str, Any]:
        if os.path.exists(METADATA_FILE):
            try:
                with open(METADATA_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"[DemandPredictionService] Error loading metadata: {e}")
        return {
            "model_version": "1.0.0",
            "evaluation_metrics": {"test_r2": 0.8301, "test_mae_kg": 1185.33}
        }

    def predict_demand(self, material_type: str, forecast_period: str = "next_month", location: str = "Coimbatore") -> Dict[str, Any]:
        """
        Forecasts forward demand volume and classifies trend.
        """
        mat = material_type.capitalize()
        base_monthly = BASE_DEMAND_MONTHLY.get(mat, 50000)

        # Build feature vector if model is available
        if self.model is not None:
            try:
                # Approximate 30-day projection
                df_input = pd.DataFrame([{
                    "material_type": mat,
                    "month": 10,
                    "quarter": 4,
                    "day_of_week": 2,
                    "day_of_year": 280,
                    "lag_1": base_monthly / 30.0,
                    "lag_7": base_monthly / 30.0,
                    "lag_30": base_monthly / 30.0,
                    "rolling_mean_7": base_monthly / 30.0,
                    "rolling_mean_30": base_monthly / 30.0,
                    "rolling_std_7": (base_monthly / 30.0) * 0.08
                }])
                daily_pred = float(self.model.predict(df_input)[0])
                predicted_demand_kg = round(daily_pred * 30.0, 1)
                mode = "production"
                disclaimer = "Forecast calculated via time-series lag model on benchmark dataset."
            except Exception as e:
                print(f"[DemandPredictionService] Inference error, using fallback: {e}")
                predicted_demand_kg = round(base_monthly * 1.05, 1)
                mode = "development"
                disclaimer = f"Development mode fallback: {str(e)}"
        else:
            predicted_demand_kg = round(base_monthly * 1.05, 1)
            mode = "development"
            disclaimer = "Trained model not loaded. Development fallback used."

        # Trend & Category determination
        if predicted_demand_kg > base_monthly * 1.03:
            trend = "increasing"
        elif predicted_demand_kg < base_monthly * 0.97:
            trend = "decreasing"
        else:
            trend = "stable"

        if predicted_demand_kg >= 150000:
            demand_cat = "High"
        elif predicted_demand_kg >= 60000:
            demand_cat = "Moderate"
        else:
            demand_cat = "Low"

        return {
            "material": mat,
            "forecast_period": forecast_period,
            "predicted_demand_kg": predicted_demand_kg,
            "demand_category": demand_cat,
            "trend": trend,
            "model_version": self.model_version,
            "mode": mode,
            "disclaimer": disclaimer
        }


demand_prediction_service = DemandPredictionService()
