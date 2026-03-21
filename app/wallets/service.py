import random
from fastapi import HTTPException, status
from typing import Dict, Any
from uuid import UUID
from app.core.enums import CurrencyEnum
from app.users.models import Users
from app.wallets.models import Wallets
from app.wallets.repository import WalletRepository


class WalletService:
    def __init__(self, db):
        self.db = db
        self.wallet_repo = WalletRepository(db)
    
    def _generate_account_number(self) -> str:
        while True:
            account_number = ''.join(random.choices('0123456789', k=10))
            existing = self.wallet_repo.get_wallet_by_acc_number(account_number)
            if not existing:
                return account_number
    
    def get_user_wallet(self, current_user: Users) -> Wallets:
        user_wallet = self.wallet_repo.get_wallet_by_user_id(current_user.id)
        if not user_wallet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Wallet not found"
            )
        
        return user_wallet

    def get_wallet_balance(self, current_user: Users) -> Dict[str, Any]:
        user_wallet = self.get_user_wallet(current_user)
        balance = self.wallet_repo.get_wallet_balance(user_wallet.id)
        return {"id": current_user.id, "balance": balance, "currency": user_wallet.currency}

    def create_user_wallet(self, current_user: Users, currency: CurrencyEnum = None, commit: bool = True) -> UUID:
        user_wallet = self.wallet_repo.get_wallet_by_user_id(current_user.id)
        if user_wallet:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A wallet already exists for this user"
            )
        account_number = self._generate_account_number()
        wallet_data = {
            "user_id": current_user.id,
            "account_number": account_number,
        }
        if currency:
            wallet_data['currency'] = currency
        
        wallet = self.wallet_repo.create(wallet_data, commit=commit)
        return wallet.id
    
    def get_wallet_transactions(self, current_user: Users):
        user_wallet = self.get_user_wallet(current_user)
        transactions = self.wallet_repo.get_wallet_transactions(user_wallet.id)
        return {"transactions": transactions}