from fastapi import APIRouter, Depends, Header, Request, HTTPException, status
from app.auth.dependencies import get_current_user
from app.dtos.payment_dto import PaymentRequestDTO, PaymentResponseDTO, WebhookResponseDTO, WebhookPayloadDTO
from app.payments.dependencies import get_payment_service
from app.payments.service import PaymentService
import json


router = APIRouter(prefix="/api/payments", tags=["Payments"])


@router.post("/fund", response_model=PaymentResponseDTO)
def initiate_funding(
        payload: PaymentRequestDTO,
        payment_service: PaymentService = Depends(get_payment_service),
        current_user = Depends(get_current_user)
    ):
    return payment_service.initiate_funding(current_user.id, payload.model_dump())

@router.post("/webhook", response_model=WebhookResponseDTO)
async def process_webhook(
        request: Request,
        payment_service: PaymentService = Depends(get_payment_service),
        x_webhook_signature: str = Header(...)
    ):
    raw_body = await request.body()
    body_str = raw_body.decode("utf-8")

    try:
        print(raw_body, type(raw_body))
        data = WebhookPayloadDTO.model_validate(json.loads(raw_body.decode("utf-8")))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="Invalid payload")

    return payment_service.handle_webhook(body_str, x_webhook_signature, data)

@router.get("/{reference}", response_model=PaymentResponseDTO)
def get_payment_by_reference(
        reference: str,
        payment_service: PaymentService = Depends(get_payment_service),
        current_user = Depends(get_current_user)
    ):
    return payment_service.get_payment_by_reference(reference)
