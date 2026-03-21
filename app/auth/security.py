import bcrypt
import jwt
from datetime import datetime, timezone, timedelta
from app.core.config import jwt_settings

SECRET_KEY = jwt_settings.SECRET_KEY
ACCESS_TOKEN_EXPIRE_MINUTES = jwt_settings.ACCESS_TOKEN_EXPIRE_MINUTES
ALGORITHM = jwt_settings.ALGORITHM

def hash_password(password: str) -> str:
    hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hash.decode('utf-8')

def verify_password(password: str, hash_password: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hash_password.encode('utf-8'))

def create_access_token(payload: dict) -> str:
    to_encode = payload.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt

def verify_token(token: str) -> str | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            return None
        return user_id
    except jwt.PyJWTError:
        return None
