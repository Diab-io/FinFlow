from app.core.database import Base
from app.core.enums import CurrencyEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, String
from uuid import uuid4, UUID
from datetime import datetime, timezone


class Wallets(Base):
    __tablename__ = 'wallets'

    id: Mapped[UUID] = mapped_column(primary_key=True, index=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey('users.id'), unique=True)
    account_number: Mapped[str] = mapped_column(String(10), index=True, unique=True)
    currency: Mapped[CurrencyEnum] = mapped_column(default="NGN")
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))

    transactions: Mapped[list["Transactions"]] = relationship(back_populates="wallet")