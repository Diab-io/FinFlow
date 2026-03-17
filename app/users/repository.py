from app.base_repo import BaseRepository
from app.users.models import Users
from sqlalchemy.orm import Session
from sqlalchemy import select


class UsersRepository(BaseRepository[Users]):
    ALLOWED_SEARCH_FIELDS = {"active", "email", "username", "phone"}

    def __init__(self, db: Session):
        super().__init__(Users, db)
    
    def get_user_by_email(self, email):
        stmt = select(Users).where(Users.email == email)
        return self.db.execute(stmt).scalar_one_or_none()
    
