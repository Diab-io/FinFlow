from fastapi import APIRouter, Depends, Header
from app.dtos.transfer_dto import (
    TransferRequestDTO, TransferResponseDTO, TransferReferenceResponseDTO
)
from app.auth.dependencies import get_current_user
from app.users.models import Users
from app.transfers.dependencies import get_transfer_service
from app.transfers.service import TransferService

router = APIRouter(prefix="/api/transfers", tags=["Transfers"])

@router.post('/', response_model=TransferResponseDTO)
def create_transfer(
        payload: TransferRequestDTO,
        current_user: Users = Depends(get_current_user),
        transfer_service: TransferService = Depends(get_transfer_service),
        x_idempotency_key: str = Header(...)
    ):
    return transfer_service.create_transfer(current_user, payload.model_dump(), x_idempotency_key)

@router.get('/{reference}', response_model=TransferReferenceResponseDTO)
def get_by_reference(
        reference: str,
        current_user: Users = Depends(get_current_user), 
        transfer_service: TransferService = Depends(get_transfer_service)
    ):
    return transfer_service.get_transfer_by_reference(reference)
