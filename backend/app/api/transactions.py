"""
Transactions API Router
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.models.transaction import Transaction
from backend.app.models.listing import Listing
from backend.app.models.material import Material
from backend.app.schemas.transaction import (
    TransactionCreate,
    TransactionStatusUpdate,
    TransactionResponse
)
from backend.app.dependencies import get_current_user
from backend.app.services.sustainability_service import sustainability_service

router = APIRouter(prefix="/api/transactions", tags=["Transactions"])


@router.post("", response_model=TransactionResponse)
def create_transaction(
    tx_in: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    seller = db.query(User).filter(User.id == tx_in.seller_id).first()
    if not seller:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Seller not found")

    factors = sustainability_service.get_impact_factors(db)
    impact = sustainability_service.calculate_transaction_impact(
        material_type=tx_in.material_type,
        quantity_kg=tx_in.quantity_kg,
        factors=factors
    )

    total_amount = round(tx_in.quantity_kg * tx_in.agreed_price, 2)

    tx = Transaction(
        buyer_id=current_user.id,
        seller_id=tx_in.seller_id,
        listing_id=tx_in.listing_id,
        material_type=tx_in.material_type,
        quantity_kg=tx_in.quantity_kg,
        agreed_price=tx_in.agreed_price,
        total_amount=total_amount,
        status="completed",
        co2_avoided_kg=impact["co2_avoided_kg"],
        landfill_diverted_kg=impact["landfill_diverted_kg"]
    )
    db.add(tx)

    # If linked to a listing, decrement listing quantity
    if tx_in.listing_id:
        listing = db.query(Listing).filter(Listing.id == tx_in.listing_id).first()
        if listing:
            listing.quantity_available = max(0.0, listing.quantity_available - tx_in.quantity_kg)
            if listing.quantity_available == 0:
                listing.status = "closed"
                if listing.material:
                    listing.material.status = "sold"

    db.commit()
    db.refresh(tx)
    return tx


@router.get("", response_model=List[TransactionResponse])
def get_transactions(
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Transaction)
    if current_user.role == "seller":
        query = query.filter(Transaction.seller_id == current_user.id)
    elif current_user.role == "buyer":
        query = query.filter(Transaction.buyer_id == current_user.id)

    if status:
        query = query.filter(Transaction.status == status)

    return query.order_by(Transaction.created_at.desc()).all()


@router.get("/{tx_id}", response_model=TransactionResponse)
def get_transaction_by_id(
    tx_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    tx = db.query(Transaction).filter(Transaction.id == tx_id).first()
    if not tx:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")

    if current_user.role not in ["admin"] and tx.buyer_id != current_user.id and tx.seller_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access forbidden to this transaction")

    return tx


@router.put("/{tx_id}/status", response_model=TransactionResponse)
def update_transaction_status(
    tx_id: str,
    status_in: TransactionStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    tx = db.query(Transaction).filter(Transaction.id == tx_id).first()
    if not tx:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")

    if current_user.role != "admin" and tx.seller_id != current_user.id and tx.buyer_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this transaction")

    tx.status = status_in.status
    db.commit()
    db.refresh(tx)
    return tx
