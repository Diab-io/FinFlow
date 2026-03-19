from pydantic import BaseModel
from uuid import UUID
from app.enums import CurrencyEnum

class WalletBaseDTO(BaseModel):
    id: UUID
    currency: CurrencyEnum

class WalletResponseDTO(WalletBaseDTO):
    user_id: UUID
    account_number: str

class WalletBalanceDTO(BaseModel):
    balance: float

class WalletTransactionsDTO(BaseModel):
    id: UUID
    # transactions: list[]
