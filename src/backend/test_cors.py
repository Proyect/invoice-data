#!/usr/bin/env python3
"""
Script para probar CORS del backend
"""

import requests
import json

def test_cors():
    """Probar CORS del backend"""
    url = "http://localhost:8000/api/v1/token"
    
    # Headers para simular una petición desde el frontend
    headers = {
        'Origin': 'http://localhost:3000',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Access-Control-Request-Method': 'POST',
        'Access-Control-Request-Headers': 'Content-Type'
    }
    
    # Datos de prueba
    data = {
        'username': 'testuser',
        'password': 'testpassword'
    }
    
    print("🔍 Probando CORS del backend...")
    print(f"URL: {url}")
    print(f"Headers: {headers}")
    
    try:
        # Probar OPTIONS (preflight)
        print("\n1. Probando OPTIONS (preflight)...")
        response = requests.options(url, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        # Probar POST
        print("\n2. Probando POST...")
        response = requests.post(url, data=data, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Response: {response.text}")
        
        # Verificar cabeceras CORS
        print("\n3. Verificando cabeceras CORS...")
        cors_headers = {
            'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
            'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
            'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers'),
            'Access-Control-Allow-Credentials': response.headers.get('Access-Control-Allow-Credentials')
        }
        print(f"CORS Headers: {cors_headers}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_cors()
