from app.auth.oauth2 import oauth2_scheme
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.auth.security import verify_token
from app.database import get_db
from app.users.models import Users
from app.users.repository import UsersRepository

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)) -> Users:

    user_repo = UsersRepository(db)
    user_id = verify_token(token)

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    user = user_repo.get(user_id)

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    return user

def requires_admin(user: Users = Depends(get_current_user)) -> Users:
    if user.role != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Admins can perform this action"
        )
    return user
    
