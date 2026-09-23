# AI-Powered Circular Economy Marketplace 🔄🌿

An end-to-end circular economy B2B platform connecting industrial scrap generators, certified recyclers, and remanufacturers. The platform features machine learning price regression, demand forecasting, transfer-learning-ready material vision classification, and an intelligent geospatial matching engine.

---

## Architecture Overview

- **Backend**: FastAPI, SQLAlchemy ORM, Pydantic v2, Python-Jose (JWT), BCrypt.
- **Machine Learning**: Scikit-Learn (Gradient Boosting Price Regressor & Demand Forecaster), Pillow, Joblib.
- **Frontend**: React 18, Vite, Tailwind CSS, Lucide Icons, Recharts.
- **Database**: PostgreSQL (Production) / SQLite (Zero-config local development).
- **Matching Engine**: 5-Factor Weighted Compatibility Model (Material, Quantity, Quality, Geospatial Haversine Distance, Circular Purpose).

---

## Quick Start (Local Development)

### 1. Prerequisites
- Python 3.10+
- Node.js 18+ and npm
- Git

### 2. Backend Setup

```bash
# Navigate to project root
cd CircularEconomy

# Install Python dependencies
pip install -r backend/requirements.txt

# Copy environment variables
cp .env.example .env

# Run FastAPI backend server (auto-seeds SQLite database on first startup)
python -m uvicorn backend.app.main:app --reload --port 8000
```

Verify backend health:
- API Root: `http://127.0.0.1:8000/`
- Interactive Swagger UI: `http://127.0.0.1:8000/docs`
- OpenAPI Specification: `http://127.0.0.1:8000/openapi.json`

### 3. Frontend Setup

```bash
# Navigate to frontend
cd frontend

# Install Node dependencies
npm install

# Start Vite development server
npm run dev
```

Visit the application at: `http://localhost:5173`

---

## Demo Credentials (Auto-Seeded)

| Role | Email | Password |
|------|-------|----------|
| **Admin** | `admin@circulareconomy.com` | `Admin@123` |
| **Seller** | `seller@ecotextiles.com` | `Seller@123` |
| **Buyer** | `buyer@greenplast.com` | `Buyer@123` |

---

## Running Automated Tests

A comprehensive 25-case test suite tests authentication, role authorization, material workflows, ML inference, and matching algorithms:

```bash
python -m pytest tests/ -v
```

---

## Production Deployment with Docker Compose

Run the entire stack (FastAPI Backend + React Nginx SPA + PostgreSQL 15 Database) with one command:

```bash
docker compose up --build -d
```

Services will be accessible at:
- Frontend Web App: `http://localhost:80`
- Backend API: `http://localhost:8000`
- PostgreSQL: `localhost:5432`

---

## Machine Learning Pipelines

The platform includes modular training and evaluation scripts in `ml/training/`:

```bash
# Train price regression model (outputs price_model_v1.pkl & metadata)
python ml/training/train_price_model.py

# Train demand forecasting model (outputs demand_model_v1.pkl & metadata)
python ml/training/train_demand_model.py

# Evaluate models and generate model_metrics.json
python ml/training/train_classification_model.py
```

Model artifacts and evaluations are stored in `ml/models/` and `ml/reports/model_metrics.json`.
