"""
Analytics API Router
"""

from typing import Dict, Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.models.material import Material
from backend.app.models.listing import Listing
from backend.app.models.transaction import Transaction
from backend.app.models.category import MaterialCategory
from backend.app.schemas.analytics import (
    OverviewAnalyticsResponse,
    MaterialAnalyticsResponse,
    SustainabilityAnalyticsResponse
)
from backend.app.services.sustainability_service import sustainability_service
from backend.app.services.demand_prediction_service import demand_prediction_service

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


@router.get("/overview", response_model=OverviewAnalyticsResponse)
def get_overview_analytics(db: Session = Depends(get_db)):
    total_users = db.query(User).count()
    total_sellers = db.query(User).filter(User.role == "seller").count()
    total_buyers = db.query(User).filter(User.role == "buyer").count()
    total_listings = db.query(Listing).count()
    total_txs = db.query(Transaction).count()

    sust_overview = sustainability_service.get_overview_metrics(db)

    txs = db.query(Transaction).order_by(Transaction.created_at.desc()).limit(10).all()
    recent_txs = [
        {
            "id": tx.id,
            "material_type": tx.material_type,
            "quantity_kg": tx.quantity_kg,
            "agreed_price": tx.agreed_price,
            "total_amount": tx.total_amount,
            "status": tx.status,
            "buyer_name": tx.buyer.name if tx.buyer else "Buyer",
            "seller_name": tx.seller.name if tx.seller else "Seller",
            "created_at": tx.created_at.isoformat()
        }
        for tx in txs
    ]

    # Calculate total marketplace value from all transactions
    all_txs = db.query(Transaction).all()
    total_val = sum(tx.total_amount for tx in all_txs) if all_txs else 0.0

    # Build real monthly trends from transaction data
    from collections import defaultdict
    import calendar
    monthly_data = defaultdict(lambda: {"volume_kg": 0.0, "co2_avoided_kg": 0.0, "transactions": 0})
    for tx in all_txs:
        month_key = tx.created_at.strftime("%b")
        monthly_data[month_key]["volume_kg"] += tx.quantity_kg
        monthly_data[month_key]["co2_avoided_kg"] += (tx.co2_avoided_kg or 0.0)
        monthly_data[month_key]["transactions"] += 1

    # Order by calendar month (only months with data)
    month_order = list(calendar.month_abbr)[1:]  # Jan, Feb, ..., Dec
    monthly_trends = [
        {
            "month": month,
            "volume_kg": round(monthly_data[month]["volume_kg"], 1),
            "co2_avoided_kg": round(monthly_data[month]["co2_avoided_kg"], 1),
            "transactions": monthly_data[month]["transactions"]
        }
        for month in month_order
        if month in monthly_data
    ]

    # If no real transaction data yet, show empty list (no fake data)
    return {
        "total_users": total_users,
        "total_sellers": total_sellers,
        "total_buyers": total_buyers,
        "total_listings": total_listings,
        "total_transactions": total_txs,
        "materials_recovered_kg": sust_overview["materials_recovered_kg"],
        "materials_reused_kg": sust_overview["materials_reused_kg"],
        "materials_recycled_kg": sust_overview["materials_recycled_kg"],
        "landfill_diverted_kg": sust_overview["landfill_diverted_kg"],
        "estimated_co2_avoided_kg": sust_overview["estimated_co2_avoided_kg"],
        "total_marketplace_value_inr": total_val,
        "recent_transactions": recent_txs,
        "monthly_trends": monthly_trends
    }


@router.get("/materials", response_model=MaterialAnalyticsResponse)
def get_material_analytics(db: Session = Depends(get_db)):
    materials = db.query(Material).all()

    dist = {}
    prices = {}
    for m in materials:
        m_type = m.material_type
        dist[m_type] = dist.get(m_type, 0) + m.quantity_kg
        if m_type not in prices:
            prices[m_type] = []
        if m.predicted_price:
            prices[m_type].append(m.predicted_price)

    material_distribution = [
        {"material": k, "total_quantity_kg": round(v, 1)}
        for k, v in dist.items()
    ]

    pricing_by_category = [
        {"material": k, "avg_price_per_kg": round(sum(v) / len(v), 2) if v else 25.0}
        for k, v in prices.items()
    ]

    MATERIAL_TYPES = ["Copper", "Aluminum", "Plastic", "Cardboard", "Steel", "Paper", "Glass", "Textile", "E-waste", "Other"]

    # Compute top demanded materials using the demand forecasting model
    demand_forecasts = []
    for mat in MATERIAL_TYPES:
        forecast = demand_prediction_service.predict_demand(mat)
        demand_forecasts.append({
            "material": mat,
            "predicted_demand_kg": forecast["predicted_demand_kg"],
            "trend": forecast["trend"],
            "demand_category": forecast["demand_category"]
        })

    # Sort by predicted_demand_kg descending and derive demand_index (0-100)
    demand_forecasts.sort(key=lambda x: x["predicted_demand_kg"], reverse=True)
    max_demand = demand_forecasts[0]["predicted_demand_kg"] if demand_forecasts else 1.0
    top_demanded = [
        {
            "material": d["material"],
            "demand_index": round((d["predicted_demand_kg"] / max_demand) * 100),
            "trend": d["trend"],
            "demand_category": d["demand_category"]
        }
        for d in demand_forecasts[:5]
    ]

    return {
        "material_distribution": material_distribution,
        "pricing_by_category": pricing_by_category,
        "top_demanded_materials": top_demanded
    }


@router.get("/demand")
def get_demand_forecast_analytics():
    materials = ["Aluminum", "Copper", "Steel", "Plastic", "Paper", "Cardboard", "Glass", "Textile", "E-waste", "Other"]
    forecasts = [
        demand_prediction_service.predict_demand(mat)
        for mat in materials
    ]
    return {"forecasts": forecasts}


@router.get("/sustainability", response_model=SustainabilityAnalyticsResponse)
def get_sustainability_analytics(db: Session = Depends(get_db)):
    return sustainability_service.get_overview_metrics(db)


@router.get("/seller/{seller_id}")
def get_seller_analytics(seller_id: str, db: Session = Depends(get_db)):
    """Per-seller analytics: materials, transactions, estimated inventory value."""
    from backend.app.dependencies import get_current_user
    seller_materials = db.query(Material).filter(Material.seller_id == seller_id).all()
    seller_txs = db.query(Transaction).filter(Transaction.seller_id == seller_id).all()
    completed = [t for t in seller_txs if t.status == "completed"]

    total_volume = sum(m.quantity_kg for m in seller_materials)
    inventory_value = sum((m.predicted_price or 40.0) * m.quantity_kg for m in seller_materials)
    sold_volume = sum(t.quantity_kg for t in completed)
    revenue = sum(t.total_amount for t in completed)

    return {
        "total_materials": len(seller_materials),
        "total_volume_kg": round(total_volume, 1),
        "estimated_inventory_value_inr": round(inventory_value, 2),
        "total_transactions": len(seller_txs),
        "completed_transactions": len(completed),
        "sold_volume_kg": round(sold_volume, 1),
        "total_revenue_inr": round(revenue, 2),
    }
