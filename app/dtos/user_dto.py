from pydantic import BaseModel, UUID4, EmailStr
from app.core.enums import UserRole, CurrencyEnum
from typing import Optional


class TokenRequest(BaseModel):
    email: EmailStr
    password: str


class UserCreateRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    phone: Optional[str] = None
    role: Optional[str] = None
    currency: Optional[CurrencyEnum] = None


class UserUpdateRequest(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    phone: Optional[str] = None


class UserResponse(BaseModel):
    id: UUID4
    username: str
    email: EmailStr
    role: UserRole
    active: bool


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class UpdateUserRoleRequest(BaseModel):
    role: str
