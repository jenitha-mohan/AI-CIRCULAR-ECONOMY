# AI-Powered Circular Economy Marketplace 🔄🌿

An end-to-end circular economy B2B platform connecting industrial scrap generators (Sellers), certified recyclers (Buyers), and remanufacturers. The platform features machine learning price estimation ranges, time-series demand forecasting, computer vision material classification, geospatial Haversine matching, multi-round negotiation, transaction logistics lifecycle management, in-platform transaction chat, and automated carbon offset accounting.

---

## Key Platform Capabilities

- **Strict Price Separation**: The AI model provides an advisory estimated market price range ($\text{Min} - \text{Max}$). The seller decides their manual `asking_price`, the buyer submits `offered_price`, and `agreed_price` is established strictly by mutual human agreement.
- **Multi-Round Offer & Counter-Offer Negotiation**: Full bidirectional negotiation with immutable chronological audit logging (`OfferHistory`).
- **Confirmed Transaction Lifecycle**: Automated status progression (`CONFIRMED` $\to$ `PICKUP_SCHEDULED` $\to$ `IN_TRANSIT` $\to$ `DELIVERED` $\to$ `COMPLETED`).
- **In-Platform Transaction Chat**: Secure, auditable messaging attached directly to confirmed orders for coordinating weighbridge slips, vehicle registrations, and gate passes.
- **Sustainability Analytics**: Real-time calculation of landfill mass diverted (kg) and avoided $\text{CO}_2$ emissions (kg) using peer-reviewed circular conversion factors.
- **Geospatial Haversine Matching**: 5-factor weighted matching algorithm optimizing transport emissions and lot compatibility.

---

## Architecture Overview

- **Backend**: FastAPI, SQLAlchemy 2.0 ORM, Pydantic v2, Python-Jose (JWT), BCrypt, SQLite/PostgreSQL.
- **Machine Learning**: Scikit-Learn (Gradient Boosting Regressors), Pillow, Joblib, Transfer Learning MobileNetV2.
- **Frontend**: React 18, Vite, Tailwind CSS, Lucide Icons, Recharts, Axios.
- **Persistence**: Relational database schema with full foreign-key constraints and transactional integrity.

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

# Run FastAPI backend server (auto-seeds database on first startup)
python -m uvicorn backend.app.main:app --reload --port 8000
```

Verify backend health:
- API Root: `http://127.0.0.1:8000/`
- Interactive Swagger UI: `http://127.0.0.1:8000/docs`
- OpenAPI Specification: `http://127.0.0.1:8000/openapi.json`

### 3. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install Node dependencies
npm install

# Start Vite development server
npm run dev
```

Visit the web application at: `http://localhost:5173`

---

## Demo Credentials (Auto-Seeded)

| Role | Email | Password | Primary Capabilities |
|------|-------|----------|----------------------|
| **Admin** | `admin@circulareconomy.com` | `Admin@123` | Full control center, ML registry, global analytics |
| **Seller** | `seller@ecotextiles.com` | `Seller@123` | AI Material Studio, inventory lots, offer countering |
| **Buyer** | `buyer@greenplast.com` | `Buyer@123` | Geospatial sourcing, bidding, purchase dispatches |

---

## Running Automated Tests

Run the complete 33-case test suite covering auth, RBAC, ML inference, multi-round negotiation, transaction logistics, chat, sustainability, and full end-to-end marketplace flow:

```bash
pytest tests/ -v
```

### Test Suite Structure:
- `tests/test_auth.py` (9 tests) - Registration, JWT login, role authorization guards
- `tests/test_materials.py` (5 tests) - Material listing CRUD, AI price estimation
- `tests/test_ml.py` (5 tests) - Price prediction, demand prediction, classification inference
- `tests/test_matching_and_recommendations.py` (4 tests) - Geospatial compatibility engine
- `tests/test_offers_and_negotiation.py` (4 tests) - Bidding, multi-round counter-offers, acceptance
- `tests/test_transactions.py` (2 tests) - Impact calculation, sustainability analytics
- `tests/test_transactions_and_chat.py` (3 tests) - Order lifecycle, pickup scheduling, chat
- `tests/test_e2e_flow.py` (1 test) - Full 23-step end-to-end marketplace validation

---

## Production Deployment with Docker Compose

Run the full stack (FastAPI Backend + React Nginx SPA + PostgreSQL 15 Database):

```bash
docker compose up --build -d
```

Services:
- Frontend Web App: `http://localhost:80`
- Backend API: `http://localhost:8000`
- PostgreSQL: `localhost:5432`

---

## Machine Learning Pipelines

Modular training scripts located in `ml/training/`:

```bash
# Train price regression model (Gradient Boosting Regressor, R² = 0.9979)
python ml/training/train_price_model.py

# Train demand forecasting model (R² = 0.8101)
python ml/training/train_demand_model.py

# Evaluate models and generate model_metrics.json
python ml/training/train_classification_model.py
```

---

## Detailed Documentation

- [Complete End-to-End Marketplace Flow (23 Steps)](docs/marketplace_flow.md)
- [System Architecture](docs/architecture.md)
- [Authentication & RBAC](docs/authentication.md)
- [Multi-Round Negotiation Engine](docs/negotiation.md)
- [AI Price & Demand Estimation](docs/ai_price_prediction.md)
- [Transaction Lifecycle, Logistics & Chat](docs/transaction_flow.md)
- [ML Data Leakage Audit Report](docs/ml_data_leakage_audit.md)
