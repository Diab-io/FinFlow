from app.database import Base
from sqlalchemy.orm import mapped_column, Mapped
from uuid import UUID, uuid4
from datetime import datetime, timezone
from typing import Optional
from app.enums import UserRole


class Users(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    username: Mapped[str] = mapped_column(unique=True, index=True)
    email: Mapped[str] = mapped_column(unique=True, index=True)
    password: Mapped[str]
    phone: Mapped[Optional[str]]
    role: Mapped[UserRole] = mapped_column(default="customer")
    active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[Optional[datetime]] = mapped_column(onupdate=datetime.now(timezone.utc), nullable=True)

    @property
    def is_admin(self) -> bool:
        return self.role == UserRole.ADMIN
    
    @property
    def is_customer(self) -> bool:
        return self.role == UserRole.CUSTOMER
    
    @property
    def is_merchant(self) -> bool:
        return self.role == UserRole.MERCHANT