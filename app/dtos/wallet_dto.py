from pydantic import BaseModel
from uuid import UUID
from app.core.enums import CurrencyEnum
from decimal import Decimal
from app.dtos.transaction_dto import TransactionResponseDTO

class WalletBaseDTO(BaseModel):
    id: UUID
    currency: CurrencyEnum

class WalletResponseDTO(WalletBaseDTO):
    user_id: UUID
    account_number: str

class WalletBalanceDTO(WalletBaseDTO):
    balance: Decimal

class WalletTransactionsDTO(BaseModel):
    transactions: list[TransactionResponseDTO]
