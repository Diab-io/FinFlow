from app.base_repo import BaseRepository
from app.users.models import Users
from sqlalchemy.orm import Session
from sqlalchemy import select, and_


class UsersRepository(BaseRepository[Users]):
    def __init__(self, db: Session):
        super().__init__(Users, db)
    
    def get_user(self, **filters):
        ALLOWED_FIELDS = {"email", "username", "phone"}

        conditions = []

        for field, value in filters.items():
            if field in ALLOWED_FIELDS and value is not None:
                column = getattr(Users, field, None)
                if column is not None:
                    conditions.append(column == value)
        
        if not conditions:
            return None
        
        query = select(Users).where(and_(**conditions))
        return self.db.execute(query).scalar_one_or_none()

