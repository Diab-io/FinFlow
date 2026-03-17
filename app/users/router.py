from fastapi import APIRouter, Depends
from app.dtos.user_dto import TokenRequest, TokenResponse, UserCreateRequest, UserResponse, UserUpdateRequest
from app.auth.dependencies import get_current_user, requires_admin
from app.users.service import UsersService
from app.users.models import Users
from typing import Optional
from app.users.dependencies import get_user_service

router = APIRouter(prefix="/api/auth", tags=["Users"])

@router.post("/token", response_model=TokenResponse)
def login(
    payload: TokenRequest,
    user_service: UsersService = Depends(get_user_service)
    ):
    return user_service.login_user(payload)

@router.post("/register", response_model=UserResponse, status_code=201)
def register(
    payload: UserCreateRequest,
    user_service: UsersService = Depends(get_user_service)
    ):
    return user_service.register_user(payload)

@router.get("/users", response_model=list[UserResponse])
def get_users(
    active: Optional[bool] = True,
    current_user: Users = Depends(requires_admin),
    user_service: UsersService = Depends(get_user_service)
    ):
    return user_service.get_users(current_user, active=active)

@router.get("/users/{id}", response_model=UserResponse)
def get_user(
    id: str,
    current_user: Users = Depends(get_current_user),
    user_service: UsersService = Depends(get_user_service)
    ):
    return user_service.get_user(id, current_user)

@router.put("/users/{id}", response_model=UserResponse)
def update_user(
    id: str,
    payload: UserUpdateRequest,
    current_user: Users = Depends(requires_admin),
    user_service: UsersService = Depends(get_user_service)):
    
    return user_service.update_user(id, payload, current_user)

#will be implemented with the AccountClosureService
@router.post("/users/{id}/archive")
def archive_user(
    id: str,
    current_user: Users = Depends(get_current_user),
    user_service: UsersService = Depends(get_user_service)):
    pass

