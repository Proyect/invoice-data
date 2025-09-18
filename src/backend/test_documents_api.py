#!/usr/bin/env python3
"""
Script para probar la API de documentos
"""

import requests
import json

def test_documents_api():
    """Probar la API de documentos"""
    base_url = "http://localhost:8000"
    
    # 1. Hacer login
    print("🔐 Haciendo login...")
    login_data = {
        'username': 'testuser',
        'password': 'testpassword'
    }
    
    try:
        login_response = requests.post(
            f"{base_url}/api/v1/token",
            data=login_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        
        if login_response.status_code != 200:
            print(f"❌ Error en login: {login_response.status_code}")
            print(f"Response: {login_response.text}")
            return
            
        token_data = login_response.json()
        token = token_data['access_token']
        print(f"✅ Login exitoso")
        
    except Exception as e:
        print(f"❌ Error en login: {e}")
        return
    
    # 2. Probar endpoint de documentos
    print("\n📄 Probando endpoint de documentos...")
    try:
        headers = {'Authorization': f'Bearer {token}'}
        docs_response = requests.get(f"{base_url}/api/v1/documents/", headers=headers)
        
        print(f"Status: {docs_response.status_code}")
        print(f"Headers: {dict(docs_response.headers)}")
        
        if docs_response.status_code == 200:
            docs_data = docs_response.json()
            print(f"✅ Respuesta exitosa:")
            print(f"Total documentos: {docs_data.get('total', 0)}")
            print(f"Documentos: {json.dumps(docs_data, indent=2)}")
        else:
            print(f"❌ Error: {docs_response.text}")
            
    except Exception as e:
        print(f"❌ Error obteniendo documentos: {e}")

if __name__ == "__main__":
    test_documents_api()

