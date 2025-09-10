#!/usr/bin/env python3
"""
Script para probar el token
"""

import requests

# Probar autenticación
response = requests.post(
    "http://localhost:8000/api/v1/token",
    data={"username": "testuser", "password": "testpassword"}
)

if response.status_code == 200:
    token_data = response.json()
    token = token_data['access_token']
    print(f"Token obtenido: {token[:50]}...")
    
    # Decodificar token para ver qué contiene
    import jwt
    from jose import jwt as jose_jwt
    
    # Intentar con jose
    try:
        # Necesitamos la clave secreta, vamos a usar una hardcodeada para prueba
        SECRET_KEY = "your_super_secret_jwt_key_here_make_it_long_and_random"
        payload = jose_jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        print(f"Token decodificado:")
        print(f"Username: {payload.get('sub')}")
        print(f"User ID: {payload.get('user_id')}")
    except Exception as e:
        print(f"Error decodificando token: {e}")
else:
    print(f"Error en autenticación: {response.status_code}")
    print(response.text)
