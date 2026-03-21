from app.core.database import Base
from app.core.enums import TransactionTypeEnum
from sqlalchemy import ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid import uuid4, UUID
from decimal import Decimal
from typing import Optional
from datetime import datetime, timezone 


class Transactions(Base):
    __tablename__ = "transactions"

    id: Mapped[UUID] = mapped_column(primary_key=True, index=True, default=uuid4)
    wallet_id: Mapped[UUID] = mapped_column(ForeignKey('wallets.id'))
    type: Mapped[TransactionTypeEnum] = mapped_column()
    amount: Mapped[Decimal] = mapped_column(Numeric(precision=15, scale=2), default=0)
    reference: Mapped[str] = mapped_column()
    description: Mapped[Optional[str]]
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))

    wallet: Mapped["Wallets"] = relationship(back_populates="transactions")
    

