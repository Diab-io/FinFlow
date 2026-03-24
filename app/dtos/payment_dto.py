from pydantic import BaseModel
from decimal import Decimal
from uuid import UUID
from app.core.enums import PaymentStatus
from typing import Dict, Any
from datetime import datetime


class PaymentRequestDTO(BaseModel):
    amount: Decimal

class PaymentResponseDTO(BaseModel):
    id: UUID
    amount: Decimal
    status: PaymentStatus
    reference: str
    payment_response: Dict[str, Any]
    created_at: datetime

class WebhookPayloadDTO(BaseModel):
    event: str
    status: str
    reference: str
    reason: str
