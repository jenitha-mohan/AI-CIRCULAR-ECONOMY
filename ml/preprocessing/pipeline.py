"""
AI Circular Economy Marketplace — Preprocessing Pipelines
Standardized scikit-learn transformers and feature engineering.
"""

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer

CATEGORICAL_FEATURES = [
    "material_type",
    "quality",
    "location",
    "demand_level",
    "seller_type",
    "material_condition"
]

NUMERICAL_FEATURES = [
    "weight_kg",
    "historical_price",
    "processing_cost",
    "transportation_distance",
    "month",
    "buyer_demand"
]


def create_price_preprocessor():
    """
    Creates a robust ColumnTransformer pipeline for price prediction features.
    """
    num_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler())
    ])
    
    cat_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="constant", fill_value="Unknown")),
        ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
    ])
    
    preprocessor = ColumnTransformer([
        ("num", num_pipeline, NUMERICAL_FEATURES),
        ("cat", cat_pipeline, CATEGORICAL_FEATURES)
    ], remainder="drop")
    
    return preprocessor


def create_demand_features(df: pd.DataFrame, target_col: str = "quantity_requested") -> pd.DataFrame:
    """
    Feature engineering for time-series demand forecasting:
    - Calendar features: month, quarter, day_of_week
    - Lag features: lag_1, lag_7, lag_30
    - Rolling window aggregates: rolling_mean_7, rolling_mean_30, rolling_std_7
    """
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values(by=["material_type", "date"]).reset_index(drop=True)
    
    # Calendar features
    df["month"] = df["date"].dt.month
    df["quarter"] = df["date"].dt.quarter
    df["day_of_week"] = df["date"].dt.dayofweek
    df["day_of_year"] = df["date"].dt.dayofyear
    
    # Lag and Rolling window features per material
    material_groups = df.groupby("material_type")
    
    df["lag_1"] = material_groups[target_col].shift(1)
    df["lag_7"] = material_groups[target_col].shift(7)
    df["lag_30"] = material_groups[target_col].shift(30)
    
    df["rolling_mean_7"] = material_groups[target_col].transform(lambda x: x.shift(1).rolling(7, min_periods=1).mean())
    df["rolling_mean_30"] = material_groups[target_col].transform(lambda x: x.shift(1).rolling(30, min_periods=1).mean())
    df["rolling_std_7"] = material_groups[target_col].transform(lambda x: x.shift(1).rolling(7, min_periods=1).std()).fillna(0)
    
    # Drop rows with NaN from lags
    df_clean = df.dropna().reset_index(drop=True)
    return df_clean
