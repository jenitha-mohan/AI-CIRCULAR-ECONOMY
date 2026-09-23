"""
Buyer Requirements API Router
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.models.buyer_requirement import BuyerRequirement
from backend.app.schemas.buyer_requirement import (
    BuyerRequirementCreate,
    BuyerRequirementUpdate,
    BuyerRequirementResponse
)
from backend.app.dependencies import get_current_user, require_role

router = APIRouter(prefix="/api/buyers", tags=["Buyer Requirements"])


@router.post("/requirements", response_model=BuyerRequirementResponse)
def create_buyer_requirement(
    req_in: BuyerRequirementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["buyer", "admin"]))
):
    requirement = BuyerRequirement(
        buyer_id=current_user.id,
        material_type=req_in.material_type,
        min_quantity=req_in.min_quantity,
        max_quantity=req_in.max_quantity,
        quality=req_in.quality or "Any",
        purpose=req_in.purpose or "Recycling",
        max_price_per_kg=req_in.max_price_per_kg,
        location_id=current_user.location_id,
        is_active=req_in.is_active if req_in.is_active is not None else True
    )
    db.add(requirement)
    db.commit()
    db.refresh(requirement)
    return requirement


@router.get("/requirements", response_model=List[BuyerRequirementResponse])
def get_buyer_requirements(
    material_type: Optional[str] = None,
    buyer_id: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    query = db.query(BuyerRequirement)
    if material_type:
        query = query.filter(BuyerRequirement.material_type.ilike(f"%{material_type}%"))
    if buyer_id:
        query = query.filter(BuyerRequirement.buyer_id == buyer_id)
    if is_active is not None:
        query = query.filter(BuyerRequirement.is_active == is_active)

    return query.order_by(BuyerRequirement.created_at.desc()).all()


@router.get("/requirements/{req_id}", response_model=BuyerRequirementResponse)
def get_requirement_by_id(req_id: str, db: Session = Depends(get_db)):
    requirement = db.query(BuyerRequirement).filter(BuyerRequirement.id == req_id).first()
    if not requirement:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Requirement not found")
    return requirement


@router.put("/requirements/{req_id}", response_model=BuyerRequirementResponse)
def update_buyer_requirement(
    req_id: str,
    req_in: BuyerRequirementUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    requirement = db.query(BuyerRequirement).filter(BuyerRequirement.id == req_id).first()
    if not requirement:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Requirement not found")

    if requirement.buyer_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to edit this requirement")

    update_data = req_in.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(requirement, field, val)

    db.commit()
    db.refresh(requirement)
    return requirement


@router.delete("/requirements/{req_id}")
def delete_buyer_requirement(
    req_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    requirement = db.query(BuyerRequirement).filter(BuyerRequirement.id == req_id).first()
    if not requirement:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Requirement not found")

    if requirement.buyer_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this requirement")

    db.delete(requirement)
    db.commit()
    return {"success": True, "message": "Buyer requirement deleted successfully"}
