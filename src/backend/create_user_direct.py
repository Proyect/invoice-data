#!/usr/bin/env python3
"""
Script para crear usuario de prueba directamente en la base de datos
"""

import psycopg2
import uuid
import hashlib

def get_password_hash(password: str) -> str:
    """Hash simple de contraseña para pruebas"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_test_user():
    """Crea el usuario de prueba en la base de datos"""
    print("Creando usuario de prueba...")
    
    try:
        # Conectar a la base de datos
        conn = psycopg2.connect(
            host='localhost',
            port=5432,
            user='ocr_user',
            password='dev_password_123',
            database='ocr_database'
        )
        
        cursor = conn.cursor()
        
        # Verificar si el usuario ya existe
        cursor.execute("SELECT id FROM users WHERE username = %s", ("testuser",))
        existing_user = cursor.fetchone()
        
        if existing_user:
            print("Usuario 'testuser' ya existe")
            print(f"ID: {existing_user[0]}")
            return existing_user[0]
        
        # Crear nuevo usuario
        user_id = str(uuid.uuid4())
        hashed_password = get_password_hash("testpassword")
        
        cursor.execute("""
            INSERT INTO users (id, username, hashed_password, disabled)
            VALUES (%s, %s, %s, %s)
        """, (user_id, "testuser", hashed_password, False))
        
        conn.commit()
        
        print("Usuario 'testuser' creado exitosamente")
        print(f"ID: {user_id}")
        print(f"Username: testuser")
        print(f"Password: testpassword")
        print(f"Password hash: {hashed_password}")
        
        # Verificar que se creó correctamente
        cursor.execute("SELECT id, username FROM users WHERE username = %s", ("testuser",))
        created_user = cursor.fetchone()
        print(f"Usuario verificado: {created_user}")
        
        return user_id
        
    except Exception as e:
        print(f"Error creando usuario: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    create_test_user()

