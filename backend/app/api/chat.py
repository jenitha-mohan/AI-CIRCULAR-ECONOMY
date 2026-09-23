"""
In-Platform Transaction Chat API Router
Enables direct buyer-seller messaging strictly tied to confirmed transactions.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.models.transaction import Transaction
from backend.app.models.chat import ChatMessage
from backend.app.schemas.chat import ChatMessageCreate, ChatMessageResponse, ChatConversationResponse
from backend.app.dependencies import get_current_user

router = APIRouter(tags=["Transaction Chat"])


@router.get("/api/transactions/{transaction_id}/messages", response_model=List[ChatMessageResponse])
def get_transaction_messages(
    transaction_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve chronological messages for a confirmed transaction.
    Only authorized buyer and seller participants can view messages.
    """
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found.")

    if current_user.id not in [transaction.buyer_id, transaction.seller_id] and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access chat for this transaction.")

    # Mark incoming messages as read
    db.query(ChatMessage).filter(
        ChatMessage.transaction_id == transaction_id,
        ChatMessage.receiver_id == current_user.id,
        ChatMessage.read_at.is_(None)
    ).update({"read_at": None})
    db.commit()

    return db.query(ChatMessage).filter(
        ChatMessage.transaction_id == transaction_id
    ).order_by(ChatMessage.created_at.asc()).all()


@router.post("/api/transactions/{transaction_id}/messages", response_model=ChatMessageResponse, status_code=status.HTTP_201_CREATED)
def send_transaction_message(
    transaction_id: str,
    message_in: ChatMessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Send a message within a transaction conversation.
    """
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found.")

    if current_user.id not in [transaction.buyer_id, transaction.seller_id] and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to send messages in this transaction.")

    receiver_id = transaction.seller_id if current_user.id == transaction.buyer_id else transaction.buyer_id

    chat_msg = ChatMessage(
        transaction_id=transaction.id,
        sender_id=current_user.id,
        receiver_id=receiver_id,
        message=message_in.message.strip()
    )
    db.add(chat_msg)
    db.commit()
    db.refresh(chat_msg)

    return chat_msg


@router.get("/api/chat/conversations", response_model=List[ChatConversationResponse])
def get_user_conversations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all active transaction chat conversations for the current user.
    """
    txs = db.query(Transaction).filter(
        or_(Transaction.buyer_id == current_user.id, Transaction.seller_id == current_user.id)
    ).order_by(Transaction.created_at.desc()).all()

    conversations = []
    for tx in txs:
        other = tx.seller if current_user.id == tx.buyer_id else tx.buyer
        last_msg = db.query(ChatMessage).filter(
            ChatMessage.transaction_id == tx.id
        ).order_by(ChatMessage.created_at.desc()).first()

        unread = db.query(ChatMessage).filter(
            ChatMessage.transaction_id == tx.id,
            ChatMessage.receiver_id == current_user.id,
            ChatMessage.read_at.is_(None)
        ).count()

        conversations.append({
            "transaction_id": tx.id,
            "material_type": tx.material_type,
            "quantity_kg": tx.quantity_kg,
            "agreed_price": tx.agreed_price,
            "total_amount": tx.total_amount,
            "status": tx.status,
            "other_party": other,
            "last_message": last_msg,
            "unread_count": unread,
            "created_at": tx.created_at
        })

    return conversations
