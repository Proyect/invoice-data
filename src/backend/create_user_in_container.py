#!/usr/bin/env python3
"""
Script para crear usuario de prueba dentro del contenedor Docker
"""

import sys
import os
sys.path.append('.')

from database import SessionLocal, User
from services.auth_service import get_password_hash
import uuid

def create_test_user():
    """Crea el usuario de prueba en la base de datos"""
    print("👤 Creando usuario de prueba...")
    
    db = SessionLocal()
    try:
        # Verificar si el usuario ya existe
        existing_user = db.query(User).filter(User.username == "testuser").first()
        if existing_user:
            print("✅ Usuario 'testuser' ya existe")
            print(f"ID: {existing_user.id}")
            return existing_user.id
        
        # Crear nuevo usuario
        user_id = uuid.uuid4()
        hashed_password = get_password_hash("testpassword")
        
        new_user = User(
            id=user_id,
            username="testuser",
            hashed_password=hashed_password,
            disabled=False
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        print("✅ Usuario 'testuser' creado exitosamente")
        print(f"ID: {new_user.id}")
        print(f"Username: {new_user.username}")
        print(f"Password: testpassword")
        
        return new_user.id
        
    except Exception as e:
        print(f"❌ Error creando usuario: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return None
    finally:
        db.close()

if __name__ == "__main__":
    create_test_user()
