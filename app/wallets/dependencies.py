from fastapi import Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.wallets.service import WalletService

def get_wallet_service(db: Session = Depends(get_db)) -> WalletService:
    return WalletService(db)