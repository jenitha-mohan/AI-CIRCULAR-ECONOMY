"""
Smart Buyer-Seller Matching Engine
Computes transparent weighted matching scores between seller materials and buyer requirements,
featuring Haversine geospatial proximity and natural language explanations.
"""

import math
from typing import Dict, Any, List, Optional, Tuple


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculates great-circle distance between two coordinate pairs in kilometers.
    """
    R = 6371.0  # Earth radius in kilometers
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_phi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * (math.sin(delta_lambda / 2.0) ** 2)
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return round(R * c, 1)


class MatchingEngine:
    QUALITY_RANKS = {
        "Low": 1,
        "Medium": 2,
        "High": 3,
        "Industrial Grade": 4,
        "Any": 0
    }

    def compute_match(
        self,
        material: Dict[str, Any],
        buyer_req: Dict[str, Any],
        seller_lat: Optional[float] = 11.0168,
        seller_lon: Optional[float] = 76.9558,
        buyer_lat: Optional[float] = 11.0168,
        buyer_lon: Optional[float] = 76.9558
    ) -> Dict[str, Any]:
        """
        Computes weighted match score between a material listing and a buyer requirement.
        Formula:
        MatchScore = 0.35 * MaterialSimilarity +
                     0.25 * QuantityCompatibility +
                     0.20 * QualityCompatibility +
                     0.10 * LocationSimilarity +
                     0.10 * PurposeCompatibility
        """
        reasons = []

        # 1. Material Similarity (35%)
        mat_type = material.get("material_type", "").strip().lower()
        req_type = buyer_req.get("material_type", "").strip().lower()
        if mat_type == req_type:
            mat_sim = 1.0
            reasons.append(f"Material type '{material.get('material_type')}' matches exactly")
        elif req_type in mat_type or mat_type in req_type:
            mat_sim = 0.75
            reasons.append(f"Material category is closely related ({material.get('material_type')})")
        else:
            mat_sim = 0.0

        # 2. Quantity Compatibility (25%)
        qty = float(material.get("quantity_kg", 0.0))
        min_qty = float(buyer_req.get("min_quantity", 0.0))
        max_qty = float(buyer_req.get("max_quantity", 1000000.0))

        if min_qty <= qty <= max_qty:
            qty_compat = 1.0
            reasons.append(f"Available quantity ({qty:.0f} kg) fits requirement ({min_qty:.0f}-{max_qty:.0f} kg)")
        elif qty < min_qty:
            ratio = max(0.0, qty / min_qty) if min_qty > 0 else 0.0
            qty_compat = round(ratio * 0.7, 2)
            if qty_compat > 0.4:
                reasons.append(f"Available quantity ({qty:.0f} kg) is slightly below minimum requested batch")
        else:  # qty > max_qty
            ratio = max_qty / qty if qty > 0 else 0.0
            qty_compat = round(0.75 + (ratio * 0.25), 2)
            reasons.append(f"Available quantity ({qty:.0f} kg) can satisfy buyer's full demand in tranches")

        # 3. Quality Compatibility (20%)
        mat_quality = material.get("quality", "Medium")
        req_quality = buyer_req.get("quality", "Any")
        mat_rank = self.QUALITY_RANKS.get(mat_quality, 2)
        req_rank = self.QUALITY_RANKS.get(req_quality, 0)

        if req_quality == "Any" or mat_rank >= req_rank:
            qual_compat = 1.0
            reasons.append(f"Quality grade '{mat_quality}' satisfies buyer specification '{req_quality}'")
        elif mat_rank == req_rank - 1:
            qual_compat = 0.65
            reasons.append(f"Quality grade '{mat_quality}' is one grade below preferred '{req_quality}'")
        else:
            qual_compat = 0.30

        # 4. Location Similarity (10%) & Haversine Distance
        dist_km = haversine_distance(
            seller_lat or 11.0168, seller_lon or 76.9558,
            buyer_lat or 11.0168, buyer_lon or 76.9558
        )

        if dist_km <= 50.0:
            loc_sim = 1.0
            reasons.append(f"Buyer is located nearby ({dist_km} km away, low logistics cost)")
        elif dist_km <= 150.0:
            loc_sim = 0.75
            reasons.append(f"Buyer is in regional transit zone ({dist_km} km away)")
        elif dist_km <= 500.0:
            loc_sim = 0.45
            reasons.append(f"Inter-city transit distance ({dist_km} km)")
        else:
            loc_sim = 0.20

        # 5. Purpose Compatibility (10%)
        mat_purpose = material.get("intended_purpose", "Recycling").strip().lower()
        req_purpose = buyer_req.get("purpose", "Recycling").strip().lower()
        if mat_purpose == req_purpose:
            purpose_compat = 1.0
            reasons.append(f"Intended purpose '{material.get('intended_purpose')}' matches buyer processing plan")
        else:
            purpose_compat = 0.50
            reasons.append("Intended purpose differs but material remains repurposable")

        # Weighted Match Score calculation
        match_score = (
            (0.35 * mat_sim) +
            (0.25 * qty_compat) +
            (0.20 * qual_compat) +
            (0.10 * loc_sim) +
            (0.10 * purpose_compat)
        )

        match_score = round(max(0.0, min(1.0, match_score)), 2)

        return {
            "match_score": match_score,
            "distance_km": dist_km,
            "reasons": reasons,
            "components": {
                "material_similarity": mat_sim,
                "quantity_compatibility": qty_compat,
                "quality_compatibility": qual_compat,
                "location_similarity": loc_sim,
                "purpose_compatibility": purpose_compat
            }
        }


matching_engine = MatchingEngine()
