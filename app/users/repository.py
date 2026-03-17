from app.base_repo import BaseRepository
from app.users.models import Users
from sqlalchemy.orm import Session
from sqlalchemy import select, and_


class UsersRepository(BaseRepository[Users]):
    def __init__(self, db: Session):
        super().__init__(Users, db)
    
