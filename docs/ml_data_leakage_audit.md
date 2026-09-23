# AI Circular Economy Marketplace — Machine Learning Data Leakage Audit

**Audit Date**: September 21, 2026  
**Audited Artifacts**:
- `datasets/material_prices.csv`
- `datasets/material_demand.csv`
- `ml/training/train_price_model.py`
- `ml/training/train_demand_model.py`
- `ml/preprocessing/pipeline.py`

---

## Executive Summary

A comprehensive data leakage audit was conducted across all datasets, feature engineering pipelines, preprocessing transformers, model training routines, and validation strategies.

One critical split flaw was identified in the time-series demand forecasting pipeline (`train_demand_model.py`) where row-index slicing on material-grouped data created an inadvertent entity split rather than a temporal chronological split. This has been **fixed**, the time-series split has been **restructured chronologically by date**, and the models have been **retrained and evaluated on genuinely held-out test data**.

---

## 1. Detailed Verification Across the 7 Audit Pillars

### Pillar 1: Train/Test Split Timing & Target-Derived Features
- **Price Regression**:
  - `material_prices.csv` contains raw independent feature records without dynamic target-derived aggregates.
  - The dataset is split into Train (70%), Validation (15%), and Test (15%) using `train_test_split(random_state=42)` before fitting any preprocessor.
  - *Verdict: PASSED.*
- **Demand Forecasting**:
  - **Issue Identified**: In `pipeline.py`, `create_demand_features` sorts the dataset by `["material_type", "date"]`. In the original `train_demand_model.py`, a simple index-based slice `iloc[:split_idx]` was executed. Because rows were grouped by material type, the first 80% of rows took 100% of the timeline (Jan–Dec 2025) for 8 materials (Aluminum to Plastic), leaving 100% of the timeline for the last 2 materials (Steel and Textile) in the test set.
  - **Remediation**: Refactored the split to use **strict chronological cutoff by date** across all 10 material series:
    - **Train**: Jan 31, 2025 to Sep 2, 2025 (64% of timeline, 2,140 samples across all 10 materials)
    - **Validation**: Sep 2, 2025 to Oct 26, 2025 (16% of timeline, 540 samples across all 10 materials)
    - **Held-Out Test**: Oct 26, 2025 to Dec 31, 2025 (20% of timeline, 670 samples across all 10 materials)
  - *Verdict: FIXED & VERIFIED.*

---

### Pillar 2: Target Information in Input Features
- **Price Regression**:
  - Target: `price_per_kg`.
  - Feature set: `['weight_kg', 'historical_price', 'processing_cost', 'transportation_distance', 'month', 'buyer_demand', 'material_type', 'quality', 'location', 'demand_level', 'seller_type', 'material_condition']`.
  - `historical_price` is an external market benchmark quote, not the transaction price.
  - **Ablation Validation**: When `historical_price` is completely removed from the feature set, the model still achieves $R^2 = 0.9944$ and Test MAE = ₹5.79 using `material_type` + `quality` + `condition`, confirming the model is learning genuine domain dynamics rather than relying on target leakage.
  - *Verdict: PASSED.*
- **Demand Forecasting**:
  - Target: `quantity_requested`.
  - Features used: Calendar features (`month`, `quarter`, `day_of_week`, `day_of_year`) and past lags (`lag_1`, `lag_7`, `lag_30`, `rolling_mean_7`, `rolling_mean_30`, `rolling_std_7`).
  - Contemporaneous variables from the CSV (`quantity_sold`, `number_of_buyers`, `number_of_transactions`) are strictly **excluded** from training features because they are downstream outcomes unknown at forecast time.
  - *Verdict: PASSED.*

---

### Pillar 3: Temporal Availability of Historical Features
- **Demand Forecasting**:
  - In `ml/preprocessing/pipeline.py`:
    ```python
    df["lag_1"] = material_groups[target_col].shift(1)
    df["lag_7"] = material_groups[target_col].shift(7)
    df["lag_30"] = material_groups[target_col].shift(30)
    df["rolling_mean_7"] = material_groups[target_col].transform(lambda x: x.shift(1).rolling(7, min_periods=1).mean())
    df["rolling_mean_30"] = material_groups[target_col].transform(lambda x: x.shift(1).rolling(30, min_periods=1).mean())
    df["rolling_std_7"] = material_groups[target_col].transform(lambda x: x.shift(1).rolling(7, min_periods=1).std()).fillna(0)
    ```
  - Because `shift(1)` is explicitly applied prior to rolling window aggregation, all historical features for prediction point $t$ only contain data from $t-1$ and earlier. No information from time step $t$ or future steps is accessible.
  - *Verdict: PASSED.*

---

### Pillar 4: Preprocessing Isolation (Fit on Train Only)
- **Price Regression**:
  - `create_price_preprocessor()` returns an unfitted `ColumnTransformer` with `SimpleImputer`, `StandardScaler`, and `OneHotEncoder`.
  - Wrapped inside a `sklearn.pipeline.Pipeline`, meaning `fit()` is called **only on `X_train`** during candidate selection and **`X_train_val`** for the final artifact.
  - `X_val` and `X_test` are strictly transformed via `predict()`.
  - *Verdict: PASSED.*
- **Demand Forecasting**:
  - `ColumnTransformer` with `StandardScaler` for numerical features and `OneHotEncoder(handle_unknown="ignore")` for `material_type`.
  - Integrated into a `Pipeline` fitted strictly on chronological `X_train`, then refitted on chronological `X_train_val`.
  - *Verdict: PASSED.*

---

### Pillar 5: Test Data Isolation During Model Selection
- Both training scripts evaluate multiple model architectures (Random Forest, Gradient Boosting, Ridge, Linear Regression).
- Model selection is governed exclusively by validation scores (`val_r2` on `X_val`).
- The held-out test set (`X_test`, `y_test`) is never used to tune hyperparameters or select the winner.
- *Verdict: PASSED.*

---

### Pillar 6: Cross-Validation Integrity
- **Price Regression**:
  - Evaluated using 5-Fold Cross-Validation with nested preprocessing pipelines.
  - **Results**: Mean $R^2 = 0.9965 \pm 0.0012$, Mean MAE = ₹$4.62 \pm 1.04$.
- **Demand Forecasting**:
  - Evaluated across sequential chronological validation blocks.
  - *Verdict: PASSED.*

---

## 2. Genuine Holdout Test Performance (Post-Remediation)

### A. Price Prediction Regressor (`price_model_v1.pkl`)
- **Algorithm**: Gradient Boosting Regressor (`n_estimators=150, learning_rate=0.08, max_depth=6`)
- **Holdout Test Set Evaluation (375 samples)**:

| Metric | Validation Set | Held-Out Test Set |
|--------|----------------|-------------------|
| **$R^2$ Score** | **0.9945** | **0.9979** |
| **MAE (₹/kg)** | **₹6.16** | **₹3.74** |
| **RMSE (₹/kg)** | **₹15.84** | **₹8.80** |

#### Candidate Model Comparison on Held-Out Test Set:
| Model | Test MAE (₹/kg) | Test RMSE (₹/kg) | Test $R^2$ |
|-------|-----------------|------------------|------------|
| **Gradient Boosting** | **₹3.74** | **₹8.80** | **0.9979** |
| Random Forest | ₹6.82 | ₹15.36 | 0.9936 |
| Ridge Regression | ₹25.88 | ₹47.60 | 0.9384 |
| Linear Regression | ₹25.95 | ₹47.70 | 0.9381 |

---

### B. Time-Series Demand Forecaster (`demand_model_v1.pkl`)
- **Algorithm**: Gradient Boosting Forecaster (`n_estimators=120, learning_rate=0.08, max_depth=5`)
- **Holdout Test Set Evaluation (Oct 26 – Dec 31, 2025 across all 10 material streams, 670 samples)**:

| Metric | Validation Set (Sep–Oct) | Held-Out Test Set (Oct–Dec) |
|--------|--------------------------|-----------------------------|
| **$R^2$ Score** | **0.9763** | **0.9718** |
| **MAE (kg)** | **290.12 kg** | **354.02 kg** |
| **RMSE (kg)** | **436.94 kg** | **521.00 kg** |

#### Candidate Model Comparison on Chronological Held-Out Test Set:
| Model | Test MAE (kg) | Test RMSE (kg) | Test $R^2$ |
|-------|---------------|----------------|------------|
| **Gradient Boosting Forecaster** | **354.02 kg** | **521.00 kg** | **0.9718** |
| Random Forest Forecaster | 355.85 kg | 506.05 kg | 0.9734 |
| Ridge Forecaster | 451.41 kg | 581.84 kg | 0.9648 |

---

## 3. Summary of Remediations Applied

1. **Fixed Temporal Slicing in `train_demand_model.py`**:
   - Replaced row-index slicing (`iloc`) with strict date-based chronological boolean masking (`dates < cutoff`).
2. **Updated Preprocessing & Metadata Registry**:
   - Regenerated `ml/models/price_model_metadata.json` and `ml/models/demand_model_metadata.json`.
   - Updated platform aggregate registry `ml/reports/model_metrics.json`.
3. **Confirmed Non-Leakage via Feature Ablation**:
   - Verified that the price regression pipeline maintains $R^2 > 0.99$ even without benchmark price quotes.
