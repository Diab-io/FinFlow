from app.base_repo import BaseRepository
from app.wallets.models import Wallets
from app.transactions.models import Transactions
from app.enums import TransactionTypeEnum
from uuid import UUID
from sqlalchemy import select, case, func, and_
from sqlalchemy.orm import Session


class WalletRepository(BaseRepository[Wallets]):
    def __init__(self, db: Session):
        super().__init__(Wallets, db)

    def get_wallet_by_acc_number(self, account_number: str) -> Wallets:
        query = select(Wallets).where(Wallets.account_number == account_number)
        wallet = self.db.execute(query).scalar_one_or_none()
        return wallet

    def get_wallet_by_user_id(self, user_id: UUID):
        query = select(Wallets).where(Wallets.user_id == user_id)
        wallet = self.db.execute(query).scalar_one_or_none()
        return wallet

    def get_wallet_balance(self, wallet_id: UUID):
        credits = self.db.execute(
            select(
                func.coalesce(
                    func.sum(Transactions.amount), 0
                )
            ).where(
                and_(
                    Transactions.wallet_id == wallet_id,
                    Transactions.type == TransactionTypeEnum.CREDIT
                )
            )
        ).scalar()

        debits = self.db.execute(
            select(
                func.coalesce(
                    func.sum(Transactions.amount), 0
                )
            ).where(
                and_(
                    Transactions.wallet_id == wallet_id,
                    Transactions.type == TransactionTypeEnum.DEBIT
                )
            )
        ).scalar()

        balance = credits - debits
        return balance
    
    def get_wallet_transactions(self, wallet_id: UUID):
        query = select(Transactions).where(Transactions.wallet_id == wallet_id)
        transactions = self.db.execute(query).all()
        return transactions
