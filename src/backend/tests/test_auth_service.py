import sys
import os
from dotenv import load_dotenv

load_dotenv()
project_root = os.getenv("PROJECT_ROOT")
#print(f"Project root from .env: {project_root} ")
if project_root and project_root not in sys.path:
    sys.path.append(project_root)

import uuid

from datetime import timedelta
from src.backend.services.auth_service import (
    verify_password,
    get_password_hash,
    authenticate_user,
    create_access_token,
    TEST_USER_USERNAME,
    TEST_USER_PASSWORD_HASH
)
from src.backend.database import User

def test_password_hash_and_verify():
    password = "testpassword"
    hashed = get_password_hash(password)
    assert verify_password(password, hashed), "La verificación de contraseña falló"
    assert not verify_password("wrongpassword", hashed), "La verificación debería fallar con contraseña incorrecta"

def test_authenticate_user_success():
    user = authenticate_user(TEST_USER_USERNAME, "testpassword")
    assert user is not None, "No se autenticó el usuario válido"
    assert user.username == TEST_USER_USERNAME

def test_authenticate_user_fail():
    user = authenticate_user("wronguser", "testpassword")
    assert user is None, "Se autenticó un usuario inválido"
    user = authenticate_user(TEST_USER_USERNAME, "wrongpassword")
    assert user is None, "Se autenticó con contraseña incorrecta"

def test_create_access_token_and_decode():
    user_id = str(uuid.uuid4())
    data = {"sub": TEST_USER_USERNAME, "user_id": user_id}
    token = create_access_token(data, expires_delta=timedelta(minutes=5))
    assert isinstance(token, str), "El token JWT no es un string"
    # Decodifica el token para verificar el contenido
    from src.backend.config import SECRET_KEY_JWT, ALGORITHM
    from jose import jwt
    payload = jwt.decode(token, SECRET_KEY_JWT, algorithms=[ALGORITHM])
    assert payload["sub"] == TEST_USER_USERNAME
    assert payload["user_id"] == user_id

if __name__ == "__main__":
    print("Running auth_service tests...")
    test_password_hash_and_verify()
    test_authenticate_user_success()
    test_authenticate_user_fail()
    test_create_access_token_and_decode()
    print("Everything Ok!!.")