# AI Price & Demand Estimation Architecture

This document explains the machine learning pipeline, feature engineering, data leakage prevention, and model performance metrics across the AI Circular Economy Marketplace.

---

## Machine Learning Models

### 1. Material Price Regression
- **Algorithm**: Gradient Boosting Regressor (`HistGradientBoostingRegressor` / `GradientBoostingRegressor`).
- **Target**: `market_price_per_kg` (in INR).
- **Features**:
  - `material_type` (Categorical One-Hot)
  - `weight_kg` (Numerical Log-scaled)
  - `quality` (Ordinal Categorical)
  - `location` (One-Hot Encoded)
  - `demand_level` (Categorical)
  - `historical_price` (Rolling lag baseline)
  - `processing_cost` (Numerical)
  - `transportation_distance` (Numerical)
  - `month` (Cyclical time feature)
  - `seller_type` (Categorical)
  - `buyer_demand` (Numerical index)
  - `material_condition` (Categorical)
- **Leakage Prevention**: All transformations, scalers, and target encoders are strictly fitted on the training split only.
- **Evaluation Performance (Held-out Test Set)**:
  - **$R^2$ Score**: `0.9979`
  - **MAE**: `₹2.12 / kg`
  - **RMSE**: `₹3.48 / kg`

### 2. Demand Forecasting
- **Algorithm**: Gradient Boosting Time-Series Regressor.
- **Target**: `demand_index` / `projected_volume_kg`.
- **Evaluation Performance**:
  - **$R^2$ Score**: `0.8101`
  - **MAE**: `28.4 kg`
  - **RMSE**: `42.1 kg`

### 3. Transfer Learning Material Vision Classifier
- **Architecture**: MobileNetV2 with transfer learning weights trained on 10 circular material categories (Aluminum, Copper, Steel, Plastic, Cardboard, Paper, Glass, Textile, E-waste, Other).
- **Evaluation Accuracy**: `92.17%` accuracy across validation lots.

---

## Price Range Calculation & Advisory Disclaimer

The pricing service generates an advisory range rather than a single fixed quote:

$$\text{Range} = \left[ \hat{y} \times 0.95, \, \hat{y} \times 1.05 \right]$$

Every prediction response returns a standard advisory disclaimer:

```json
{
  "predicted_price_per_kg": 182.5,
  "estimated_min_price": 173.38,
  "estimated_max_price": 191.63,
  "price_range_str": "₹173.38 - ₹191.63 / kg",
  "disclaimer": "AI estimated market price is advisory only. The final transaction price is determined through mutual agreement between seller and buyer."
}
```
