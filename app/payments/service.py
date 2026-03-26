import requests
import hmac
import hashlib
import json
from sqlalchemy.orm import Session
from app.payments.repository import PaymentRepository
from app.transactions.repository import TransactionRepository
from app.wallets.repository import WalletRepository
from uuid import UUID, uuid4
from app.core.config import settings
from fastapi import HTTPException, status
from app.core.enums import PaymentStatus, TransactionTypeEnum


class PaymentService:
    def __init__(self, db: Session):
        self.db = db
        self.payment_repo = PaymentRepository(self.db)
        self.transaction_repo = TransactionRepository(self.db)
        self.wallet_repo = WalletRepository(self.db)

    
    def verify_webhook_signature(self, data: str, webhook_signature: str):
        expected = hmac.new(
            settings.WEBHOOK_KEY.encode("utf-8"),
            data.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(expected, webhook_signature)
        

    def initiate_funding(self, current_user: UUID, data: dict):
        reference = f"PAY-{uuid4().hex[:12]}"

        payment = self.payment_repo.create({
            "user_id": current_user,
            "amount": float(data.get("amount", 0)),
            "reference": reference, 
        })

        requests.post('http://localhost:9000/charge', json={
            "amount": float(data.get("amount", 0)),
            "reference": reference,
            "callback_url": 'http://localhost:8000/api/payments/webhook'
        })

        return payment
    
    def handle_webhook(self, raw_body: str, webhook_signature: str, data):
        if not self.verify_webhook_signature(raw_body, webhook_signature):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid signature"
            )
                
        payment = self.payment_repo.get_payment_by_reference(data.reference)

        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found"
            )

        if payment.status != PaymentStatus.PENDING:
            return {"status": "Already Processed"}
        
        if data.status == 'success':
            wallet = self.wallet_repo.get_wallet_by_user_id(payment.user_id)

            if not wallet:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="There is no wallet associated with the current user"
                )

            payment.status = PaymentStatus.SUCCESS
            self.transaction_repo.create({
                "wallet_id": wallet.id,
                "type": TransactionTypeEnum.CREDIT,
                "amount": payment.amount,
                "reference": payment.reference,
            }, commit=False)
        else:
            payment.status = PaymentStatus.FAILED
        
        payment.gateway_response = data.model_dump()
    
        
        self.payment_repo.db.commit()
        return {"status": payment.status}

    def get_payment_by_reference(self, reference: str):
        payment = self.payment_repo.get_payment_by_reference(reference)

        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment details not found"
            )
        
        return payment

