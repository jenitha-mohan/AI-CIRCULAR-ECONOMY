"""
Listings Management API Router
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.models.listing import Listing
from backend.app.models.material import Material
from backend.app.schemas.listing import ListingCreate, ListingUpdate, ListingResponse
from backend.app.dependencies import get_current_user, require_role

router = APIRouter(prefix="/api/listings", tags=["Listings"])


@router.post("", response_model=ListingResponse)
def create_listing(
    listing_in: ListingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["seller", "admin"]))
):
    if listing_in.asking_price <= 0:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Asking price must be greater than zero")
    if listing_in.quantity_available <= 0:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Quantity must be greater than zero")

    material = db.query(Material).filter(Material.id == listing_in.material_id).first()
    if not material:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Material not found")

    if material.seller_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to list this material")

    listing = Listing(
        seller_id=current_user.id,
        material_id=material.id,
        quantity_available=listing_in.quantity_available,
        unit=listing_in.unit or "kg",
        asking_price=listing_in.asking_price,
        min_acceptable_price=listing_in.min_acceptable_price,
        ai_estimated_min_price=listing_in.ai_estimated_min_price,
        ai_estimated_max_price=listing_in.ai_estimated_max_price,
        status=listing_in.status or "active"
    )
    db.add(listing)
    db.commit()
    db.refresh(listing)
    return listing


@router.get("/seller/me", response_model=List[ListingResponse])
def get_my_seller_listings(
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["seller", "admin"]))
):
    """Retrieve all listings owned by the authenticated seller."""
    query = db.query(Listing).filter(Listing.seller_id == current_user.id)
    if status:
        query = query.filter(Listing.status == status)
    return query.order_by(Listing.created_at.desc()).all()



@router.get("", response_model=List[ListingResponse])
def get_all_listings(
    status: Optional[str] = "active",
    seller_id: Optional[str] = None,
    material_type: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Listing).join(Material)
    if status:
        query = query.filter(Listing.status == status)
    if seller_id:
        query = query.filter(Listing.seller_id == seller_id)
    if material_type:
        query = query.filter(Material.material_type.ilike(f"%{material_type}%"))
    if min_price is not None:
        query = query.filter(Listing.asking_price >= min_price)
    if max_price is not None:
        query = query.filter(Listing.asking_price <= max_price)

    return query.order_by(Listing.created_at.desc()).all()


@router.get("/{listing_id}", response_model=ListingResponse)
def get_listing_by_id(listing_id: str, db: Session = Depends(get_db)):
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found")
    return listing


@router.put("/{listing_id}", response_model=ListingResponse)
def update_listing(
    listing_id: str,
    listing_in: ListingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found")

    if listing.seller_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to edit this listing")

    update_data = listing_in.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(listing, field, val)

    db.commit()
    db.refresh(listing)
    return listing


@router.delete("/{listing_id}")
def delete_listing(
    listing_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found")

    if listing.seller_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this listing")

    db.delete(listing)
    db.commit()
    return {"success": True, "message": "Listing deleted successfully"}
