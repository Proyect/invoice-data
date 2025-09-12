#!/usr/bin/env python3
"""
Script para probar específicamente OPTIONS
"""

import requests

def test_options():
    """Probar OPTIONS específicamente"""
    url = "http://localhost:8000/api/v1/token"
    
    headers = {
        'Origin': 'http://localhost:3000',
        'Access-Control-Request-Method': 'POST',
        'Access-Control-Request-Headers': 'Content-Type'
    }
    
    print("🔍 Probando OPTIONS específicamente...")
    print(f"URL: {url}")
    print(f"Headers: {headers}")
    
    try:
        response = requests.options(url, headers=headers)
        print(f"\nStatus: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Response: {response.text}")
        
        # Verificar cabeceras CORS específicas
        cors_headers = {
            'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
            'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
            'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers'),
            'Access-Control-Allow-Credentials': response.headers.get('Access-Control-Allow-Credentials')
        }
        print(f"\nCORS Headers: {cors_headers}")
        
        if cors_headers['Access-Control-Allow-Origin']:
            print("✅ CORS está funcionando!")
        else:
            print("❌ CORS no está funcionando")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_options()
