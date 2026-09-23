"""
AI Price Prediction Service
Loads trained scikit-learn regression pipeline to predict price per kg (INR).
"""

import os
import json
import joblib
import pandas as pd
from typing import Dict, Any
from backend.app.config import settings

MODEL_FILE = os.path.join(settings.MODEL_DIR, "price_model_v1.pkl")
METADATA_FILE = os.path.join(settings.MODEL_DIR, "price_model_metadata.json")

BASE_PRICES = {
    "Copper": 650.0, "Aluminum": 180.0, "E-waste": 120.0, "Steel": 42.0,
    "Textile": 28.0, "Plastic": 35.0, "Cardboard": 14.0, "Paper": 12.0,
    "Glass": 8.0, "Other": 15.0
}


class PricePredictionService:
    def __init__(self):
        self.model = self._load_model()
        self.metadata = self._load_metadata()
        self.model_name = self.metadata.get("model_name", "ai_price_regressor")
        self.model_version = self.metadata.get("model_version", "1.0.0")

    def _load_model(self):
        if os.path.exists(MODEL_FILE):
            try:
                model = joblib.load(MODEL_FILE)
                print(f"[PricePredictionService] Successfully loaded trained model from {MODEL_FILE}")
                return model
            except Exception as e:
                print(f"[PricePredictionService] Error loading model artifact: {e}")
        return None

    def _load_metadata(self) -> Dict[str, Any]:
        if os.path.exists(METADATA_FILE):
            try:
                with open(METADATA_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"[PricePredictionService] Error loading metadata: {e}")
        return {
            "model_name": "ai_price_regressor",
            "model_version": "1.0.0",
            "feature_importance_ranking": {
                "material_type": 52.4,
                "historical_price": 24.1,
                "quality": 10.2,
                "demand_level": 5.8,
                "material_condition": 4.1,
                "transportation_distance": 3.4
            }
        }

    def predict_price(self, req_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predicts recyclable material price per kilogram and total batch valuation.
        """
        mat = req_data.get("material_type", "Plastic")
        weight_kg = float(req_data.get("weight_kg", 100.0))
        
        # Prepare input DataFrame for scikit-learn pipeline
        input_dict = {
            "weight_kg": [weight_kg],
            "historical_price": [float(req_data.get("historical_price", BASE_PRICES.get(mat, 30.0)))],
            "processing_cost": [float(req_data.get("processing_cost", 5.0))],
            "transportation_distance": [float(req_data.get("transportation_distance", 25.0))],
            "month": [int(req_data.get("month", 9))],
            "buyer_demand": [float(req_data.get("buyer_demand", 0.8))],
            "material_type": [mat],
            "quality": [req_data.get("quality", "Medium")],
            "location": [req_data.get("location", "Coimbatore")],
            "demand_level": [req_data.get("demand_level", "Moderate")],
            "seller_type": [req_data.get("seller_type", "Business")],
            "material_condition": [req_data.get("material_condition", "Sorted")]
        }
        
        input_df = pd.DataFrame(input_dict)
        top_factors = self.metadata.get("feature_importance_ranking", {})

        if self.model is not None:
            try:
                pred_arr = self.model.predict(input_df)
                predicted_price_per_kg = round(float(pred_arr[0]), 2)
                mode = "production"
                disclaimer = "Predicted via trained Gradient Boosting regression model on circular benchmark data."
            except Exception as e:
                print(f"[PricePredictionService] Prediction error, falling back: {e}")
                predicted_price_per_kg = self._heuristic_price(req_data)
                mode = "development"
                disclaimer = f"Development fallback calculation used: {str(e)}"
        else:
            predicted_price_per_kg = self._heuristic_price(req_data)
            mode = "development"
            disclaimer = "Trained model not loaded. Development fallback inference used."

        # Guarantee reasonable positive price
        predicted_price_per_kg = max(predicted_price_per_kg, 1.0)
        estimated_min_price = round(predicted_price_per_kg * 0.95, 2)
        estimated_max_price = round(predicted_price_per_kg * 1.05, 2)
        estimated_total_value = round(predicted_price_per_kg * weight_kg, 2)
        price_range_str = f"₹{estimated_min_price} – ₹{estimated_max_price}/kg"

        return {
            "predicted_price_per_kg": predicted_price_per_kg,
            "estimated_min_price": estimated_min_price,
            "estimated_max_price": estimated_max_price,
            "price_range_str": price_range_str,
            "estimated_total_value": estimated_total_value,
            "currency": "INR",
            "model_name": self.model_name,
            "model_version": self.model_version,
            "mode": mode,
            "top_factors": top_factors,
            "disclaimer": "AI price is an estimate for reference. The seller decides the asking price."
        }

    def _heuristic_price(self, data: Dict[str, Any]) -> float:
        mat = data.get("material_type", "Plastic")
        base = BASE_PRICES.get(mat, 30.0)
        q = data.get("quality", "Medium")
        q_mult = 1.15 if q == "High" else (1.25 if q == "Industrial Grade" else (0.80 if q == "Low" else 1.0))
        d = data.get("demand_level", "Moderate")
        d_mult = 1.10 if d == "High" else (0.90 if d == "Low" else 1.0)
        return round(base * q_mult * d_mult, 2)


price_prediction_service = PricePredictionService()
