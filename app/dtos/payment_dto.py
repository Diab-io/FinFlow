from pydantic import BaseModel, Field
from decimal import Decimal
from uuid import UUID
from app.core.enums import PaymentStatus
from typing import Dict, Any, Optional
from datetime import datetime


class PaymentRequestDTO(BaseModel):
    amount: Decimal = Field(ge=1)

class PaymentResponseDTO(BaseModel):
    id: UUID
    amount: Decimal
    status: PaymentStatus
    reference: str
    payment_response: Optional[Dict[str, Any]] = None
    created_at: datetime

class WebhookPayloadDTO(BaseModel):
    status: str
    reference: str
    reason: Optional[str] = None

class WebhookResponseDTO(BaseModel):
    status: str
