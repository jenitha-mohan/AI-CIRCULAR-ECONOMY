"""
Listings Management API Router
Enforces strict seller ownership and RBAC. Never trusts client-supplied seller IDs.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.models.listing import Listing
from backend.app.models.material import Material
from backend.app.schemas.listing import ListingCreate, ListingUpdate, ListingResponse
from backend.app.dependencies import get_current_user, require_role, log_security_event

router = APIRouter(prefix="/api/listings", tags=["Listings"])


@router.post("", response_model=ListingResponse, status_code=status.HTTP_201_CREATED)
def create_listing(
    listing_in: ListingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["seller", "admin"]))
):
    """
    Creates a new marketplace listing.
    Strictly assigns seller_id = current_user.id from the verified JWT.
    """
    if listing_in.asking_price <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Asking price must be greater than zero."
        )
    if listing_in.quantity_available <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Quantity must be greater than zero."
        )

    material = db.query(Material).filter(Material.id == listing_in.material_id).first()
    if not material:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Material lot not found.")

    # Ownership check on the underlying material
    if material.seller_id != current_user.id and current_user.role != "admin":
        log_security_event(
            "UNAUTHORIZED_LISTING_ATTEMPT",
            user_id=current_user.id,
            detail=f"Attempted to create listing for material {material.id} owned by {material.seller_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to create a listing for another seller's material lot."
        )

    listing = Listing(
        seller_id=current_user.id,  # ALWAYS current user from JWT
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

    log_security_event("LISTING_CREATED", user_id=current_user.id, detail=f"Listing {listing.id} created")
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
    """Public discovery: Browse active marketplace listings."""
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
    """Retrieve listing details."""
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found")
    return listing


@router.put("/{listing_id}", response_model=ListingResponse)
def update_listing(
    listing_id: str,
    listing_in: ListingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["seller", "admin"]))
):
    """
    Updates an existing listing. Enforces strict seller ownership.
    """
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found")

    if listing.seller_id != current_user.id and current_user.role != "admin":
        log_security_event(
            "UNAUTHORIZED_LISTING_UPDATE",
            user_id=current_user.id,
            detail=f"Attempted to edit listing {listing_id} owned by {listing.seller_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to edit another seller's listing."
        )

    update_data = listing_in.model_dump(exclude_unset=True)
    # Prevent tampering with immutable identifiers
    update_data.pop("seller_id", None)
    update_data.pop("id", None)

    for field, val in update_data.items():
        setattr(listing, field, val)

    db.commit()
    db.refresh(listing)
    return listing


@router.delete("/{listing_id}")
def delete_listing(
    listing_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["seller", "admin"]))
):
    """
    Deletes a listing. Enforces strict seller ownership.
    """
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found")

    if listing.seller_id != current_user.id and current_user.role != "admin":
        log_security_event(
            "UNAUTHORIZED_LISTING_DELETE",
            user_id=current_user.id,
            detail=f"Attempted to delete listing {listing_id} owned by {listing.seller_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to delete another seller's listing."
        )

    db.delete(listing)
    db.commit()
    return {"success": True, "message": "Listing deleted successfully"}
