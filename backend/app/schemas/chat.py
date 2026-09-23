"""
Chat Schemas for In-Platform Transaction Messaging
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
from backend.app.schemas.user import UserResponse


class ChatMessageCreate(BaseModel):
    message: str = Field(..., min_length=1, max_length=5000, description="Chat text message content")


class ChatMessageResponse(BaseModel):
    id: str
    transaction_id: str
    sender_id: str
    receiver_id: str
    message: str
    created_at: datetime
    read_at: Optional[datetime] = None
    sender: Optional[UserResponse] = None
    receiver: Optional[UserResponse] = None

    class Config:
        from_attributes = True


class ChatConversationResponse(BaseModel):
    transaction_id: str
    material_type: str
    quantity_kg: float
    agreed_price: float
    total_amount: float
    status: str
    other_party: UserResponse
    last_message: Optional[ChatMessageResponse] = None
    unread_count: int = 0
    created_at: datetime

    class Config:
        from_attributes = True
