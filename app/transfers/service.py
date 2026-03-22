from sqlalchemy.orm import Session
from app.transactions.repository import TransactionRepository
from app.wallets.repository import WalletRepository
from app.users.models import Users
from app.core.enums import TransactionTypeEnum
from fastapi import HTTPException, status
from uuid import uuid4

class TransferService:
    def __init__(self, db: Session):
        self.db = db
        self.transaction_repo = TransactionRepository(self.db)
        self.wallet_repo = WalletRepository(self.db)
    
    def get_transfer_by_reference(self, reference: str):
        transfer = self.transaction_repo.get_transaction_by_reference(reference)
        if not transfer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="A transfer with this reference does not exist"
            )
        
        return {"transactions": transfer}
    
    def create_transfer(self, current_user: Users, payload: dict):
        account_number = payload.get('account_number')
        amount = payload.get("amount")
        description = payload.get("description")

        sender_wallet = self.wallet_repo.get_wallet_by_user_id(current_user.id)

        if not sender_wallet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User does not have a wallet attached to him"
            )
        
        receipient_wallet = self.wallet_repo.get_wallet_by_acc_number(account_number)

        if not receipient_wallet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="There is no wallet with the specified account number"
            )
        
        if sender_wallet.id == receipient_wallet.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You can't send funds to yourself"
            )
        
        sender_balance = self.wallet_repo.get_wallet_balance(sender_wallet.id)

        if sender_balance < amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient funds"
            )
        
        if sender_wallet.currency != receipient_wallet.currency:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Transfer to an account with a different currency is currently unavailable"
            )
        
        transaction_reference = f'tnx_{uuid4().hex[:12]}'

        base_trxn_data = {
            "amount": amount,
            "reference": transaction_reference,
        }
        if description:
            base_trxn_data["description"] = description

        debit_data = {
            "wallet_id": sender_wallet.id,
            "type": TransactionTypeEnum.DEBIT
        }

        credit_data = {
            "wallet_id": receipient_wallet.id,
            "type": TransactionTypeEnum.CREDIT
        }

        print(base_trxn_data)
        debit_trxn_data = {**base_trxn_data, **debit_data}
        credit_trxn_data = {**base_trxn_data, **credit_data}

        print(debit_trxn_data)

        self.transaction_repo.create(debit_trxn_data, commit=False)
        self.transaction_repo.create(credit_trxn_data, commit=False)

        self.transaction_repo.db.commit()

        data = {
            "reference": transaction_reference,
            "account_number": account_number,
            "amount": amount,
            "status": "completed",
            "currency": sender_wallet.currency
        }

        if description:
            data["description"] = description


        return data

