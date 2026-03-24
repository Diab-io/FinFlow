from app.core.database import Base
from sqlalchemy import ForeignKey, Numeric, JSON
from sqlalchemy.orm import Mapped, mapped_column
from uuid import UUID, uuid4
from app.core.enums import PaymentStatus
from decimal import Decimal
from typing import Optional, Dict, Any
from datetime import datetime, timezone


class Payments(Base):
    __tablename__ = "payments"

    id: Mapped[UUID] = mapped_column(primary_key=True, index=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    amount: Mapped[Decimal] = mapped_column(Numeric(precision=15, scale=2), default=0) 
    status: Mapped[PaymentStatus] = mapped_column(default=PaymentStatus.PENDING)
    reference: Mapped[str] = mapped_column(unique=True)
    gateway_response: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))


