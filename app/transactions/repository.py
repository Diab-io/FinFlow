from app.core.base_repo import BaseRepository
from app.transactions.models import Transactions
from sqlalchemy.orm import Session
from sqlalchemy import select


class TransactionRepository(BaseRepository[Transactions]):
    def __init__(self, db: Session):
        super().__init__(Transactions, db)

    def get_transaction_by_reference(self, reference: str):
        query = select(self.model).where(self.model.reference == reference)
        return self.db.execute(query).scalars().all()
