"""
AI Circular Economy Marketplace — Price Prediction Model Training
Experiments with Linear Regression, Random Forest, and Gradient Boosting.
Evaluates MAE, RMSE, R² on held-out test data and registers selected model.
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
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, root_mean_squared_error, r2_score

from ml.preprocessing.pipeline import (
    create_price_preprocessor,
    CATEGORICAL_FEATURES,
    NUMERICAL_FEATURES
)
DATA_PATH = os.path.join(BASE_DIR, "datasets", "material_prices.csv")
MODEL_DIR = os.path.join(BASE_DIR, "ml", "models")
os.makedirs(MODEL_DIR, exist_ok=True)


def train_and_evaluate_price_models():
    print(f"Loading price dataset from {DATA_PATH}...")
    df = pd.read_csv(DATA_PATH)
    
    X = df[NUMERICAL_FEATURES + CATEGORICAL_FEATURES]
    y = df["price_per_kg"]
    
    # 70% Train, 15% Validation, 15% Test Split (No data leakage)
    X_train_val, X_test, y_train_val, y_test = train_test_split(
        X, y, test_size=0.15, random_state=42
    )
    X_train, X_val, y_train, y_val = train_test_split(
        X_train_val, y_train_val, test_size=0.1765, random_state=42 # 0.1765 * 0.85 approx 15%
    )
    
    print(f"Dataset split: Train={len(X_train)}, Val={len(X_val)}, Test={len(X_test)}")
    
    preprocessor = create_price_preprocessor()
    
    candidate_models = {
        "Linear Regression": LinearRegression(),
        "Ridge Regression": Ridge(alpha=1.0),
        "Random Forest": RandomForestRegressor(n_estimators=120, max_depth=14, random_state=42, n_jobs=-1),
        "Gradient Boosting": GradientBoostingRegressor(n_estimators=150, learning_rate=0.08, max_depth=6, random_state=42)
    }
    
    model_results = {}
    best_model_name = None
    best_val_r2 = -float("inf")
    best_pipeline = None
    
    for name, regressor in candidate_models.items():
        pipe = Pipeline([
            ("preprocessor", create_price_preprocessor()),
            ("regressor", regressor)
        ])
        
        # Train on training set
        pipe.fit(X_train, y_train)
        
        # Evaluate on validation set
        val_preds = pipe.predict(X_val)
        val_mae = mean_absolute_error(y_val, val_preds)
        val_rmse = root_mean_squared_error(y_val, val_preds)
        val_r2 = r2_score(y_val, val_preds)
        
        # Evaluate on test set
        test_preds = pipe.predict(X_test)
        test_mae = mean_absolute_error(y_test, test_preds)
        test_rmse = root_mean_squared_error(y_test, test_preds)
        test_r2 = r2_score(y_test, test_preds)
        
        model_results[name] = {
            "validation": {"mae": round(float(val_mae), 3), "rmse": round(float(val_rmse), 3), "r2": round(float(val_r2), 4)},
            "test": {"mae": round(float(test_mae), 3), "rmse": round(float(test_rmse), 3), "r2": round(float(test_r2), 4)}
        }
        
        print(f"[{name}] Val R²: {val_r2:.4f}, Val MAE: {val_mae:.2f} | Test R²: {test_r2:.4f}, Test MAE: {test_mae:.2f}")
        
        if val_r2 > best_val_r2:
            best_val_r2 = val_r2
            best_model_name = name
            best_pipeline = pipe
            
    print(f"\n>> Selected Best Model: {best_model_name} (Val R²: {best_val_r2:.4f})")
    
    # Retrain best pipeline on combined Train+Val for final deployment artifact
    best_pipeline.fit(X_train_val, y_train_val)
    final_test_preds = best_pipeline.predict(X_test)
    final_test_mae = float(mean_absolute_error(y_test, final_test_preds))
    final_test_rmse = float(root_mean_squared_error(y_test, final_test_preds))
    final_test_r2 = float(r2_score(y_test, final_test_preds))
    
    # Calculate Feature Importances if tree-based
    feature_importances = {}
    reg_obj = best_pipeline.named_steps["regressor"]
    prep_obj = best_pipeline.named_steps["preprocessor"]
    
    if hasattr(reg_obj, "feature_importances_"):
        cat_encoder = prep_obj.named_transformers_["cat"].named_steps["encoder"]
        cat_encoded_names = cat_encoder.get_feature_names_out(CATEGORICAL_FEATURES).tolist()
        all_feature_names = NUMERICAL_FEATURES + cat_encoded_names
        raw_importances = reg_obj.feature_importances_
        
        # Aggregate high-level feature importance
        high_level_importance = {}
        for num_feat in NUMERICAL_FEATURES:
            idx = all_feature_names.index(num_feat)
            high_level_importance[num_feat] = float(raw_importances[idx])
            
        for cat_feat in CATEGORICAL_FEATURES:
            total_cat_imp = sum(
                raw_importances[i] for i, name in enumerate(all_feature_names) if name.startswith(cat_feat + "_")
            )
            high_level_importance[cat_feat] = float(total_cat_imp)
            
        # Normalize sum to 100%
        imp_sum = sum(high_level_importance.values()) or 1.0
        feature_importances = {k: round((v / imp_sum) * 100, 2) for k, v in sorted(high_level_importance.items(), key=lambda x: x[1], reverse=True)}
    
    # Save Model Artifacts
    model_artifact_path = os.path.join(MODEL_DIR, "price_model_v1.pkl")
    joblib.dump(best_pipeline, model_artifact_path)
    print(f"Saved model pipeline to {model_artifact_path}")
    
    metadata = {
        "model_name": "ai_price_regressor",
        "model_version": "1.0.0",
        "algorithm": best_model_name,
        "training_timestamp": datetime.now().isoformat(),
        "evaluation_metrics": {
            "test_mae": round(final_test_mae, 2),
            "test_rmse": round(final_test_rmse, 2),
            "test_r2": round(final_test_r2, 4)
        },
        "model_comparison": model_results,
        "feature_importance_ranking": feature_importances,
        "input_features": {
            "numerical": NUMERICAL_FEATURES,
            "categorical": CATEGORICAL_FEATURES
        },
        "target_currency": "INR",
        "disclaimer": "DEVELOPMENT BENCHMARK MODEL — PREDICTIONS FOR ESTIMATION PURPOSES"
    }
    
    metadata_path = os.path.join(MODEL_DIR, "price_model_metadata.json")
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    print(f"Saved model metadata to {metadata_path}")
    
    return metadata


if __name__ == "__main__":
    train_and_evaluate_price_models()
