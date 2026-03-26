from app.core.base_repo import BaseRepository
from app.payments.models import Payments
from sqlalchemy import select


class PaymentRepository(BaseRepository[Payments]):
    def __init__(self, db):
        super().__init__(Payments, db)
    
    def get_payment_by_reference(self, reference: str):
        stmt = select(self.model).where(self.model.reference == reference)
        return self.db.execute(statement=stmt).scalar_one_or_none()
