from pydantic import BaseModel
from uuid import UUID
from app.core.enums import TransactionTypeEnum
from decimal import Decimal
from typing import Optional
from datetime import datetime

class TransactionResponseDTO(BaseModel):
    id: UUID
    wallet_id: UUID
    type: TransactionTypeEnum
    amount: Decimal
    reference: str
    description: Optional[str] = None
    created_at: datetime
