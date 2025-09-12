from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import Response
from datetime import timedelta
from typing import Annotated
from sqlalchemy.orm import Session

from models.auth import Token
from services.auth_service import authenticate_user, create_access_token
from config import ACCESS_TOKEN_EXPIRE_MINUTES # Definir en config.py
from database import get_db

router = APIRouter()

@router.options("/token")
async def options_token():
    """
    Maneja las peticiones OPTIONS (preflight) para CORS
    """
    return Response(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
            "Access-Control-Allow-Credentials": "true",
        }
    )

@router.get("/token")
async def get_token():
    """
    Endpoint GET para verificar que el token está disponible
    """
    return {"message": "Token endpoint is available"}

@router.post("/token", response_model=Token, summary="Obtener token de acceso")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(get_db)]
):
    """
    Permite a un usuario autenticarse y obtener un token JWT.
    """
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "user_id": str(user.id)}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}