from fastapi import APIRouter, Depends, Query, Request
from app.dtos.wallet_dto import WalletResponseDTO, WalletBalanceDTO, WalletTransactionsDTO
from app.users.models import Users
from app.auth.dependencies import get_current_user
from app.wallets.dependencies import get_wallet_service
from app.wallets.service import WalletService

router = APIRouter(prefix="/api/wallets", tags=["wallets"])

@router.get('/me', response_model=WalletResponseDTO, summary="Get wallet details")
def get_wallet(current_user: Users = Depends(get_current_user), service: WalletService = Depends(get_wallet_service)):
    return service.get_user_wallet(current_user)

@router.get('/me/balance', response_model=WalletBalanceDTO, summary="Get wallet balance")
def get_wallet_balance(
    current_user: Users = Depends(get_current_user),
    service: WalletService = Depends(get_wallet_service)):
    return service.get_wallet_balance(current_user)

@router.get('/me/transactions', response_model=WalletTransactionsDTO, summary="Get wallet transactions")
def get_wallet_transactions(
    request: Request,
    current_user: Users = Depends(get_current_user),
    service: WalletService = Depends(get_wallet_service),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100)
    ):
    return service.get_wallet_transactions(current_user, page=page, limit=limit, request=request)