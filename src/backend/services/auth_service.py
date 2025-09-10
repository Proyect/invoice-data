# ocr_api/services/auth_service.py (fragmento)

from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import uuid

from database import get_db
from sqlalchemy.orm import Session
from models.auth import TokenData, User as UserModel
from config import SECRET_KEY_JWT, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/token")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

# --- hardcoded user for testing ---
# En un proyecto real, buscarías en la DB
TEST_USER_USERNAME = "testuser"
TEST_USER_PASSWORD_HASH = get_password_hash("testpassword") # Genera un hash para "testpassword"

def authenticate_user(username: str, password: str, db: Session):
    # Buscar el usuario en la base de datos
    from database import User as DBUser
    user = db.query(DBUser).filter(DBUser.username == username).first()
    if user and verify_password(password, user.hashed_password):
        return UserModel(
            id=user.id,
            username=user.username,
            hashed_password=user.hashed_password,
            disabled=user.disabled
        )
    return None

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY_JWT, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: Annotated[Session, Depends(get_db)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY_JWT, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: str = payload.get("user_id")
        if username is None or user_id is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    # Buscar el usuario en la base de datos usando el ID del token
    from database import User as DBUser
    import uuid
    try:
        user_uuid = uuid.UUID(user_id)
        user = db.query(DBUser).filter(DBUser.id == user_uuid).first()
    except ValueError:
        raise credentials_exception
    
    if user is None:
        raise credentials_exception
    
    return UserModel(
        id=user.id,
        username=user.username,
        hashed_password=user.hashed_password,
        disabled=user.disabled
    )


async def get_current_active_user(
    current_user: Annotated[UserModel, Depends(get_current_user)]
):
    if current_user.disabled:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user