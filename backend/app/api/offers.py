"""
Offer & Negotiation API Router
Handles multi-round price and quantity negotiations between buyers and sellers.
Ensures AI only provides advisory pricing, while final deal is strictly determined by mutual agreement.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.models.listing import Listing
from backend.app.models.offer import Offer, OfferHistory
from backend.app.models.transaction import Transaction
from backend.app.schemas.offer import OfferCreate, OfferCounter, OfferReject, OfferResponse, OfferHistoryResponse
from backend.app.schemas.transaction import TransactionResponse
from backend.app.dependencies import get_current_user, require_role
from backend.app.services.sustainability_service import sustainability_service

router = APIRouter(prefix="/api/offers", tags=["Offers & Negotiation"])


@router.post("", response_model=OfferResponse, status_code=status.HTTP_201_CREATED)
def create_offer(
    offer_in: OfferCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["buyer", "admin"]))
):
    """
    Buyer submits an offer on an active seller listing.
    """
    if offer_in.offered_price <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Offered price must be greater than zero."
        )
    if offer_in.offered_quantity <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Offered quantity must be greater than zero."
        )

    listing = db.query(Listing).filter(Listing.id == offer_in.listing_id).first()
    if not listing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found.")

    if listing.status != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot submit offer on listing with status '{listing.status}'."
        )

    if listing.seller_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sellers cannot submit offers on their own listings."
        )

    if offer_in.offered_quantity > listing.quantity_available:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Offered quantity ({offer_in.offered_quantity} kg) exceeds available quantity ({listing.quantity_available} kg)."
        )

    # Create Offer entity
    offer = Offer(
        listing_id=listing.id,
        buyer_id=current_user.id,
        seller_id=listing.seller_id,
        offered_quantity=offer_in.offered_quantity,
        offered_price=offer_in.offered_price,
        message=offer_in.message,
        status="PENDING"
    )
    db.add(offer)
    db.flush()

    # Record initial history action
    history_entry = OfferHistory(
        offer_id=offer.id,
        sender_id=current_user.id,
        receiver_id=listing.seller_id,
        price=offer_in.offered_price,
        quantity=offer_in.offered_quantity,
        message=offer_in.message,
        action="OFFER"
    )
    db.add(history_entry)
    db.commit()
    db.refresh(offer)

    return offer


@router.get("/buyer/me", response_model=List[OfferResponse])
@router.get("/buyer", response_model=List[OfferResponse])
def get_my_buyer_offers(
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["buyer", "admin"]))
):
    """
    Retrieve all offers submitted by the current buyer.
    """
    query = db.query(Offer).filter(Offer.buyer_id == current_user.id)
    if status_filter:
        query = query.filter(Offer.status == status_filter.upper())
    return query.order_by(Offer.updated_at.desc()).all()


@router.get("/seller/me", response_model=List[OfferResponse])
@router.get("/seller", response_model=List[OfferResponse])
def get_my_seller_offers(
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["seller", "admin"]))
):
    """
    Retrieve all offers received by the current seller.
    """
    query = db.query(Offer).filter(Offer.seller_id == current_user.id)
    if status_filter:
        query = query.filter(Offer.status == status_filter.upper())
    return query.order_by(Offer.updated_at.desc()).all()


@router.get("/{offer_id}", response_model=OfferResponse)
def get_offer_by_id(
    offer_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve offer details and its full negotiation history.
    """
    offer = db.query(Offer).filter(Offer.id == offer_id).first()
    if not offer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Offer not found.")

    if current_user.id not in [offer.buyer_id, offer.seller_id] and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this offer.")

    return offer


@router.get("/{offer_id}/history", response_model=List[OfferHistoryResponse])
def get_offer_history(
    offer_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve chronological audit trail of all negotiation rounds for this offer.
    """
    offer = db.query(Offer).filter(Offer.id == offer_id).first()
    if not offer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Offer not found.")

    if current_user.id not in [offer.buyer_id, offer.seller_id] and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view negotiation history.")

    return db.query(OfferHistory).filter(OfferHistory.offer_id == offer_id).order_by(OfferHistory.created_at.asc()).all()


@router.post("/{offer_id}/counter", response_model=OfferResponse)
def counter_offer(
    offer_id: str,
    counter_in: OfferCounter,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Submit a counter-offer with revised price or quantity.
    Either buyer or seller can counter in negotiation rounds.
    """
    if counter_in.counter_price <= 0:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Counter price must be greater than zero.")

    offer = db.query(Offer).filter(Offer.id == offer_id).first()
    if not offer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Offer not found.")

    if current_user.id not in [offer.buyer_id, offer.seller_id] and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to negotiate this offer.")

    if offer.status in ["ACCEPTED", "REJECTED", "CANCELLED", "EXPIRED"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot counter offer that is already {offer.status}."
        )

    # Determine receiver
    receiver_id = offer.seller_id if current_user.id == offer.buyer_id else offer.buyer_id
    new_qty = counter_in.counter_quantity if counter_in.counter_quantity and counter_in.counter_quantity > 0 else offer.offered_quantity

    offer.offered_price = counter_in.counter_price
    offer.offered_quantity = new_qty
    offer.status = "COUNTERED"

    history_entry = OfferHistory(
        offer_id=offer.id,
        sender_id=current_user.id,
        receiver_id=receiver_id,
        price=counter_in.counter_price,
        quantity=new_qty,
        message=counter_in.message or f"Counter-offer submitted: ₹{counter_in.counter_price}/kg",
        action="COUNTER"
    )
    db.add(history_entry)
    db.commit()
    db.refresh(offer)

    return offer


@router.post("/{offer_id}/accept")
def accept_offer(
    offer_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Accept the negotiated offer.
    Confirms deal, locks agreed price, decrements listing inventory, and creates official Transaction.
    """
    offer = db.query(Offer).filter(Offer.id == offer_id).first()
    if not offer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Offer not found.")

    if current_user.id not in [offer.buyer_id, offer.seller_id] and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to accept this offer.")

    if offer.status in ["ACCEPTED", "REJECTED", "CANCELLED", "EXPIRED"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Offer has already been {offer.status}."
        )

    listing = db.query(Listing).filter(Listing.id == offer.listing_id).first()
    if not listing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Associated listing not found.")

    if listing.quantity_available < offer.offered_quantity:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Insufficient quantity remaining ({listing.quantity_available} kg available vs {offer.offered_quantity} kg requested)."
        )

    # 1. Update Offer status
    offer.status = "ACCEPTED"
    receiver_id = offer.seller_id if current_user.id == offer.buyer_id else offer.buyer_id
    history_entry = OfferHistory(
        offer_id=offer.id,
        sender_id=current_user.id,
        receiver_id=receiver_id,
        price=offer.offered_price,
        quantity=offer.offered_quantity,
        message=f"Deal accepted at agreed price of ₹{offer.offered_price}/kg.",
        action="ACCEPT"
    )
    db.add(history_entry)

    # 2. Inventory control: Decrement available quantity
    listing.quantity_available -= offer.offered_quantity
    if listing.quantity_available <= 0:
        listing.quantity_available = 0.0
        listing.status = "sold"

    # 3. Calculate environmental impact
    mat_type = listing.material.material_type if listing.material else "General Scrap"
    factors = sustainability_service.get_impact_factors(db)
    impact = sustainability_service.calculate_transaction_impact(mat_type, offer.offered_quantity, factors=factors)


    # 4. Create Official Confirmed Transaction
    total_amount = round(offer.offered_quantity * offer.offered_price, 2)
    transaction = Transaction(
        buyer_id=offer.buyer_id,
        seller_id=offer.seller_id,
        listing_id=listing.id,
        offer_id=offer.id,
        material_type=mat_type,
        quantity_kg=offer.offered_quantity,
        agreed_price=offer.offered_price,
        total_amount=total_amount,
        status="CONFIRMED",
        co2_avoided_kg=impact["co2_avoided_kg"],
        landfill_diverted_kg=impact["landfill_diverted_kg"]
    )
    db.add(transaction)
    db.commit()
    db.refresh(offer)
    db.refresh(transaction)

    return {
        "success": True,
        "message": f"Offer accepted. Transaction created with Agreed Price ₹{offer.offered_price}/kg.",
        "offer": {
            "id": offer.id,
            "status": offer.status,
            "agreed_price": offer.offered_price,
            "quantity_kg": offer.offered_quantity,
        },
        "transaction": {
            "id": transaction.id,
            "agreed_price": transaction.agreed_price,
            "total_amount": transaction.total_amount,
            "quantity_kg": transaction.quantity_kg,
            "status": transaction.status,
            "co2_avoided_kg": transaction.co2_avoided_kg,
            "created_at": transaction.created_at.isoformat()
        }
    }


@router.post("/{offer_id}/reject", response_model=OfferResponse)
def reject_offer(
    offer_id: str,
    reject_in: Optional[OfferReject] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Reject an offer.
    """
    offer = db.query(Offer).filter(Offer.id == offer_id).first()
    if not offer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Offer not found.")

    if current_user.id not in [offer.buyer_id, offer.seller_id] and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to reject this offer.")

    if offer.status in ["ACCEPTED", "REJECTED", "CANCELLED"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Offer is already {offer.status}."
        )

    offer.status = "REJECTED"
    receiver_id = offer.seller_id if current_user.id == offer.buyer_id else offer.buyer_id
    history_entry = OfferHistory(
        offer_id=offer.id,
        sender_id=current_user.id,
        receiver_id=receiver_id,
        price=offer.offered_price,
        quantity=offer.offered_quantity,
        message=reject_in.message if reject_in and reject_in.message else "Offer rejected.",
        action="REJECT"
    )
    db.add(history_entry)
    db.commit()
    db.refresh(offer)

    return offer


@router.post("/{offer_id}/cancel", response_model=OfferResponse)
def cancel_offer(
    offer_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Cancel an offer (can be performed by the user who initiated or countered).
    """
    offer = db.query(Offer).filter(Offer.id == offer_id).first()
    if not offer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Offer not found.")

    if current_user.id not in [offer.buyer_id, offer.seller_id] and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to cancel this offer.")

    if offer.status in ["ACCEPTED", "REJECTED", "CANCELLED"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Offer is already {offer.status}.")

    offer.status = "CANCELLED"
    receiver_id = offer.seller_id if current_user.id == offer.buyer_id else offer.buyer_id
    history_entry = OfferHistory(
        offer_id=offer.id,
        sender_id=current_user.id,
        receiver_id=receiver_id,
        price=offer.offered_price,
        quantity=offer.offered_quantity,
        message="Offer cancelled by participant.",
        action="CANCEL"
    )
    db.add(history_entry)
    db.commit()
    db.refresh(offer)

    return offer
