from pydantic import BaseModel, Field
from uuid import UUID
from decimal import Decimal
from app.core.enums import CurrencyEnum
from app.dtos.transaction_dto import TransactionResponseDTO
from typing import Optional

class TransferRequestDTO(BaseModel):
    account_number: str
    description: Optional[str] = None
    amount: Decimal = Field(ge=1)


class TransferResponseDTO(BaseModel):
    reference: str
    account_number: str
    amount: Decimal
    description: Optional[str] = None
    status: str
    currency: CurrencyEnum

class TransferReferenceResponseDTO(BaseModel):
    transactions: list[TransactionResponseDTO]
