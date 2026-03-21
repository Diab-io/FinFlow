from fastapi import Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.users.service import UsersService

def get_user_service(db: Session = Depends(get_db)) -> UsersService:
    return UsersService(db)