"""
Analytics Schemas
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class OverviewAnalyticsResponse(BaseModel):
    total_users: int
    total_sellers: int
    total_buyers: int
    total_listings: int
    total_transactions: int
    materials_recovered_kg: float
    materials_reused_kg: float
    materials_recycled_kg: float
    landfill_diverted_kg: float
    estimated_co2_avoided_kg: float
    total_marketplace_value_inr: float
    recent_transactions: List[Dict[str, Any]]
    monthly_trends: List[Dict[str, Any]]


class MaterialAnalyticsResponse(BaseModel):
    material_distribution: List[Dict[str, Any]]
    pricing_by_category: List[Dict[str, Any]]
    top_demanded_materials: List[Dict[str, Any]]


class SustainabilityAnalyticsResponse(BaseModel):
    materials_recovered_kg: float
    materials_reused_kg: float
    materials_recycled_kg: float
    landfill_diverted_kg: float
    estimated_co2_avoided_kg: float
    completed_transactions_count: int
    impact_by_material: List[Dict[str, Any]]
    conversion_factors: Dict[str, float]
    disclaimer: str = "Estimates calculated using peer-reviewed circular conversion coefficients."
