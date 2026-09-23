"""
AI Circular Economy Marketplace — Time-Series Demand Forecasting Model Training
Features: Month, Quarter, Day of Week, Lags (1, 7, 30), Rolling Means (7, 30), Rolling Std (7)
Target: quantity_requested (kg)
"""

import os
import sys
import json
import joblib
import numpy as np
import pandas as pd
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.metrics import mean_absolute_error, root_mean_squared_error, r2_score

from ml.preprocessing.pipeline import create_demand_features

DATA_PATH = os.path.join(BASE_DIR, "datasets", "material_demand.csv")
MODEL_DIR = os.path.join(BASE_DIR, "ml", "models")
os.makedirs(MODEL_DIR, exist_ok=True)


def train_and_evaluate_demand_model():
    print(f"Loading demand time-series data from {DATA_PATH}...")
    raw_df = pd.read_csv(DATA_PATH)
    
    # Generate lag and rolling window features
    df = create_demand_features(raw_df, target_col="quantity_requested")
    print(f"Engineered time-series dataset shape: {df.shape}")
    
    feature_cols = [
        "material_type", "month", "quarter", "day_of_week", "day_of_year",
        "lag_1", "lag_7", "lag_30", "rolling_mean_7", "rolling_mean_30", "rolling_std_7"
    ]
    
    X = df[feature_cols]
    y = df["quantity_requested"]
    
    # Temporal Train/Validation/Test split by date (Strict chronological split, no future leakage)
    # 64% Train, 16% Validation, 20% Held-out Test across all material time-series
    dates = pd.to_datetime(df["date"])
    unique_dates = np.sort(dates.unique())
    train_val_cutoff = unique_dates[int(len(unique_dates) * 0.80)]
    val_cutoff = unique_dates[int(len(unique_dates) * 0.64)]
    
    train_mask = dates < val_cutoff
    val_mask = (dates >= val_cutoff) & (dates < train_val_cutoff)
    test_mask = dates >= train_val_cutoff
    train_val_mask = dates < train_val_cutoff
    
    X_train, y_train = X[train_mask], y[train_mask]
    X_val, y_val = X[val_mask], y[val_mask]
    X_test, y_test = X[test_mask], y[test_mask]
    X_train_val, y_train_val = X[train_val_mask], y[train_val_mask]
    
    print(f"Chronological split dates: Train < {val_cutoff}, Val: {val_cutoff} to {train_val_cutoff}, Test >= {train_val_cutoff}")
    print(f"Time-series splits: Train={len(X_train)}, Val={len(X_val)}, Test={len(X_test)}")
    
    num_cols = ["month", "quarter", "day_of_week", "day_of_year", "lag_1", "lag_7", "lag_30", "rolling_mean_7", "rolling_mean_30", "rolling_std_7"]
    cat_cols = ["material_type"]
    
    preprocessor = ColumnTransformer([
        ("num", StandardScaler(), num_cols),
        ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), cat_cols)
    ])
    
    models = {
        "Random Forest Forecaster": RandomForestRegressor(n_estimators=100, max_depth=12, random_state=42),
        "Gradient Boosting Forecaster": GradientBoostingRegressor(n_estimators=120, learning_rate=0.08, max_depth=5, random_state=42)
    }
    
    best_name = None
    best_pipe = None
    best_r2 = -float("inf")
    results = {}
    
    for name, reg in models.items():
        pipe = Pipeline([
            ("prep", preprocessor),
            ("reg", reg)
        ])
        
        pipe.fit(X_train, y_train)
        val_preds = pipe.predict(X_val)
        val_mae = mean_absolute_error(y_val, val_preds)
        val_rmse = root_mean_squared_error(y_val, val_preds)
        val_r2 = r2_score(y_val, val_preds)
        
        test_preds = pipe.predict(X_test)
        test_mae = mean_absolute_error(y_test, test_preds)
        test_rmse = root_mean_squared_error(y_test, test_preds)
        test_r2 = r2_score(y_test, test_preds)
        
        results[name] = {
            "val_mae": round(float(val_mae), 2), "val_rmse": round(float(val_rmse), 2), "val_r2": round(float(val_r2), 4),
            "test_mae": round(float(test_mae), 2), "test_rmse": round(float(test_rmse), 2), "test_r2": round(float(test_r2), 4)
        }
        print(f"[{name}] Val R²: {val_r2:.4f}, Test R²: {test_r2:.4f}, Test MAE: {test_mae:.2f} kg")
        
        if val_r2 > best_r2:
            best_r2 = val_r2
            best_name = name
            best_pipe = pipe
            
    # Refit best on combined train+val
    best_pipe.fit(X_train_val, y_train_val)
    final_test_preds = best_pipe.predict(X_test)
    final_test_mae = float(mean_absolute_error(y_test, final_test_preds))
    final_test_rmse = float(root_mean_squared_error(y_test, final_test_preds))
    final_test_r2 = float(r2_score(y_test, final_test_preds))
    
    # Save Model Artifact
    model_artifact_path = os.path.join(MODEL_DIR, "demand_model_v1.pkl")
    joblib.dump(best_pipe, model_artifact_path)
    print(f"Saved demand forecasting model to {model_artifact_path}")
    
    metadata = {
        "model_name": "ai_demand_forecaster",
        "model_version": "1.0.0",
        "algorithm": best_name,
        "training_timestamp": datetime.now().isoformat(),
        "evaluation_metrics": {
            "test_mae_kg": round(final_test_mae, 2),
            "test_rmse_kg": round(final_test_rmse, 2),
            "test_r2": round(final_test_r2, 4)
        },
        "model_comparison": results,
        "features": feature_cols,
        "disclaimer": "DEVELOPMENT BENCHMARK MODEL — DEMAND PROJECTIONS"
    }
    
    metadata_path = os.path.join(MODEL_DIR, "demand_model_metadata.json")
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    print(f"Saved demand model metadata to {metadata_path}")
    return metadata


if __name__ == "__main__":
    train_and_evaluate_demand_model()
