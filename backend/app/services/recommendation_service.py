"""
AI Recommendation Service
Generates bi-directional recommendations:
1. Recommends top matching buyers for a seller's material listing.
2. Recommends top matching materials for a buyer's profile or requirement.
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from backend.app.models.material import Material
from backend.app.models.buyer_requirement import BuyerRequirement
from backend.app.models.user import User
from backend.app.services.matching_service import matching_engine


class RecommendationService:
    def recommend_buyers_for_material(
        self,
        db: Session,
        material: Material,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Finds active buyer requirements and ranks them by Match Score.
        """
        requirements = db.query(BuyerRequirement).filter(
            BuyerRequirement.is_active == True
        ).all()

        seller_loc = material.seller.location if material.seller else None
        seller_lat = seller_loc.latitude if seller_loc else 11.0168
        seller_lon = seller_loc.longitude if seller_loc else 76.9558

        results = []
        for req in requirements:
            buyer = req.buyer
            buyer_loc = req.location or (buyer.location if buyer else None)
            b_lat = buyer_loc.latitude if buyer_loc else 11.0168
            b_lon = buyer_loc.longitude if buyer_loc else 76.9558

            mat_dict = {
                "material_type": material.material_type,
                "quantity_kg": material.quantity_kg,
                "quality": material.quality,
                "condition": material.condition,
                "intended_purpose": material.intended_purpose
            }
            req_dict = {
                "material_type": req.material_type,
                "min_quantity": req.min_quantity,
                "max_quantity": req.max_quantity,
                "quality": req.quality,
                "purpose": req.purpose,
                "max_price_per_kg": req.max_price_per_kg
            }

            match_res = matching_engine.compute_match(
                material=mat_dict,
                buyer_req=req_dict,
                seller_lat=seller_lat,
                seller_lon=seller_lon,
                buyer_lat=b_lat,
                buyer_lon=b_lon
            )

            # Only include relevant matches (match_score >= 0.25)
            if match_res["match_score"] >= 0.25:
                results.append({
                    "buyer_id": req.buyer_id,
                    "buyer_name": buyer.name if buyer else "Certified Recycler",
                    "organization": buyer.organization if buyer else None,
                    "material": req.material_type,
                    "match_score": match_res["match_score"],
                    "distance_km": match_res["distance_km"],
                    "required_quantity": req.max_quantity,
                    "required_quality": req.quality,
                    "reasons": match_res["reasons"],
                    "buyer": buyer
                })

        # Sort descending by match score, then ascending by distance
        results.sort(key=lambda x: (x["match_score"], -x["distance_km"]), reverse=True)
        return results[:limit]

    def recommend_materials_for_buyer(
        self,
        db: Session,
        buyer_id: str,
        limit: int = 12
    ) -> List[Dict[str, Any]]:
        """
        Finds available marketplace materials and ranks them for a specific buyer.
        """
        buyer = db.query(User).filter(User.id == buyer_id).first()
        buyer_reqs = db.query(BuyerRequirement).filter(
            BuyerRequirement.buyer_id == buyer_id,
            BuyerRequirement.is_active == True
        ).all()

        available_materials = db.query(Material).filter(
            Material.status == "available"
        ).all()

        buyer_loc = buyer.location if buyer else None
        b_lat = buyer_loc.latitude if buyer_loc else 11.0168
        b_lon = buyer_loc.longitude if buyer_loc else 76.9558

        scored_materials = []
        for mat in available_materials:
            # If buyer has explicit requirements, compare against highest matching requirement
            best_match = {"match_score": 0.40, "distance_km": 50.0, "reasons": ["Available circular material listing"]}
            
            seller_loc = mat.seller.location if mat.seller else None
            s_lat = seller_loc.latitude if seller_loc else 11.0168
            s_lon = seller_loc.longitude if seller_loc else 76.9558

            mat_dict = {
                "material_type": mat.material_type,
                "quantity_kg": mat.quantity_kg,
                "quality": mat.quality,
                "condition": mat.condition,
                "intended_purpose": mat.intended_purpose
            }

            if buyer_reqs:
                for req in buyer_reqs:
                    req_dict = {
                        "material_type": req.material_type,
                        "min_quantity": req.min_quantity,
                        "max_quantity": req.max_quantity,
                        "quality": req.quality,
                        "purpose": req.purpose,
                        "max_price_per_kg": req.max_price_per_kg
                    }
                    res = matching_engine.compute_match(
                        material=mat_dict,
                        buyer_req=req_dict,
                        seller_lat=s_lat,
                        seller_lon=s_lon,
                        buyer_lat=b_lat,
                        buyer_lon=b_lon
                    )
                    if res["match_score"] > best_match["match_score"]:
                        best_match = res
            else:
                # Default heuristic similarity
                res = matching_engine.compute_match(
                    material=mat_dict,
                    buyer_req={"material_type": mat.material_type, "min_quantity": 0, "max_quantity": 10000, "quality": "Any", "purpose": "Recycling"},
                    seller_lat=s_lat,
                    seller_lon=s_lon,
                    buyer_lat=b_lat,
                    buyer_lon=b_lon
                )
                best_match = res

            scored_materials.append({
                "material_id": mat.id,
                "material_type": mat.material_type,
                "seller_name": mat.seller.name if mat.seller else "Eco Seller",
                "seller_organization": mat.seller.organization if mat.seller else None,
                "quantity_kg": mat.quantity_kg,
                "quality": mat.quality,
                "condition": mat.condition,
                "asking_price": mat.listings[0].asking_price if mat.listings else mat.predicted_price,
                "predicted_price": mat.predicted_price,
                "match_score": best_match["match_score"],
                "distance_km": best_match["distance_km"],
                "reasons": best_match["reasons"],
                "material": mat
            })

        scored_materials.sort(key=lambda x: (x["match_score"], -x["distance_km"]), reverse=True)
        return scored_materials[:limit]


recommendation_service = RecommendationService()
