from fastapi import Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.transfers.service import TransferService

def get_transfer_service(db: Session = Depends(get_db)) -> TransferService:
    return TransferService(db)