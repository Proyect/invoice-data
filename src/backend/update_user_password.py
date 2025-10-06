#!/usr/bin/env python3
"""
Script para actualizar la contraseña del usuario con el hash correcto (bcrypt)
"""

import psycopg2
import bcrypt

def hash_password_bcrypt(password: str) -> str:
    """Hash de contraseña usando bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def update_user_password():
    """Actualiza la contraseña del usuario testuser con bcrypt"""
    print("Actualizando contraseña del usuario testuser...")
    
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
        
        # Generar hash bcrypt para "testpassword"
        hashed_password = hash_password_bcrypt("testpassword")
        
        # Actualizar la contraseña del usuario
        cursor.execute("""
            UPDATE users 
            SET hashed_password = %s 
            WHERE username = %s
        """, (hashed_password, "testuser"))
        
        conn.commit()
        
        print("Contraseña actualizada exitosamente")
        print(f"Username: testuser")
        print(f"Password: testpassword")
        print(f"Password hash (bcrypt): {hashed_password}")
        
        # Verificar que se actualizó correctamente
        cursor.execute("SELECT id, username, hashed_password FROM users WHERE username = %s", ("testuser",))
        updated_user = cursor.fetchone()
        print(f"Usuario actualizado: {updated_user[0]}, {updated_user[1]}")
        
        return True
        
    except Exception as e:
        print(f"Error actualizando contraseña: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    update_user_password()

