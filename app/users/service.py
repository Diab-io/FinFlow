from fastapi import status, HTTPException
from sqlalchemy.orm import Session
from app.users.repository import UsersRepository
from app.users.models import Users
from app.auth.security import hash_password, create_access_token, verify_password
from app.dtos.user_dto import UserCreateRequest, TokenRequest, UserUpdateRequest
from uuid import UUID

class UsersService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UsersRepository(db)
    
    def register_user(self, payload: UserCreateRequest) -> Users:
        """Service for creating users and perisitence into the database
        """
        user = self.user_repo.get_user_by_email(email=payload.email)
        if user:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")
        
        create_data = payload.model_dump(exclude_unset=True)
        create_data['password'] = hash_password(payload.password)

        return self.user_repo.create(create_data)


    def login_user(self, payload: TokenRequest) -> Users:
        """Generates a jwt access token
        """
        user = self.user_repo.get_user_by_email(email=payload.email)

        if not user or not verify_password(payload.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        access_token = create_access_token(payload={"sub": str(user.id)})
        return {"access_token": access_token, "token_type": "bearer"}

    def update_user(self, user_id: UUID, data: UserUpdateRequest, current_user: Users) -> Users:
        """Updates a user object with the passed payload
        """
        payload = data.model_dump(exclude_unset=True)

        if user_id != current_user.id and not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update your profile"
            )
        
        if 'role' in payload.keys() and not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admins have access to change user roles"
            )
        
        user = self.user_repo.get(user_id)

        if not user or not user.active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return self.user_repo.update(user, payload)

    def get_user(self, user_id: UUID, current_user: Users) -> Users:
        """Get a single user from the id
        """
        if user_id != current_user.id and not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admins can retrieve other user records"
            ) 
        
        return self.user_repo.get(user_id)

    def get_users(self, current_user: Users, **filters) -> list[Users]:
        """Get a list of users
        """
        if not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not Allowed"
            )
        
        return self.user_repo.filter(**filters)
    
    def update_user_role(self, user_id: UUID, role: str) -> Users:
        user = self.user_repo.get(user_id)

        if not user:
            raise HTTPException(404, "User not found")

        return self.user_repo.update(user, {"role": role})


