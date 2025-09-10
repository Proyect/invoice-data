#!/usr/bin/env python3
"""
Script para debuggear el problema del usuario
"""

import sys
import os
sys.path.append('.')

from database import SessionLocal, User
from services.auth_service import authenticate_user, create_access_token
from datetime import timedelta

def debug_user():
    """Debug del problema del usuario"""
    print("🔍 Debug del problema del usuario...")
    
    db = SessionLocal()
    try:
        # Buscar el usuario testuser
        user = db.query(User).filter(User.username == "testuser").first()
        if not user:
            print("❌ Usuario testuser no encontrado")
            return
        
        print(f"✅ Usuario encontrado:")
        print(f"ID: {user.id}")
        print(f"Username: {user.username}")
        
        # Probar autenticación
        auth_user = authenticate_user("testuser", "testpassword", db)
        if auth_user:
            print(f"✅ Autenticación exitosa:")
            print(f"Auth User ID: {auth_user.id}")
            print(f"Auth Username: {auth_user.username}")
            
            # Crear token
            access_token = create_access_token(
                data={"sub": auth_user.username, "user_id": str(auth_user.id)}, 
                expires_delta=timedelta(minutes=30)
            )
            print(f"✅ Token creado: {access_token[:50]}...")
            
            # Decodificar token
            from jose import jwt
            from config import SECRET_KEY_JWT, ALGORITHM
            payload = jwt.decode(access_token, SECRET_KEY_JWT, algorithms=[ALGORITHM])
            print(f"✅ Token decodificado:")
            print(f"Username: {payload.get('sub')}")
            print(f"User ID: {payload.get('user_id')}")
            
        else:
            print("❌ Error en autenticación")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    debug_user()
