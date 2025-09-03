# ocr_api/services/auth_service.py (fragmento)

from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import uuid

from database import User, get_db
from sqlalchemy.orm import Session
from models.auth import TokenData
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

def authenticate_user(username: str, password: str):
    # Aquí iría la lógica para buscar el usuario en la DB
    # Por ahora, usamos un usuario hardcodeado:
    if username == TEST_USER_USERNAME and verify_password(password, TEST_USER_PASSWORD_HASH):
        # Crear un objeto User dummy si no hay DB de usuarios, o cargar de la DB
        return User(id=uuid.uuid4(), username=TEST_USER_USERNAME, hashed_password=TEST_USER_PASSWORD_HASH)
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
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    # Aquí se buscaría el usuario en la DB real
    # Por ahora, un User dummy para el test
    if token_data.username == TEST_USER_USERNAME:
        return User(id=uuid.uuid4(), username=TEST_USER_USERNAME, hashed_password=TEST_USER_PASSWORD_HASH)
    raise credentials_exception


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
):
    if current_user.disabled:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user