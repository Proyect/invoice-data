#!/usr/bin/env python3
"""
Script para probar la conexion del frontend con el backend y la base de datos
"""

import requests
import json
import sys

def test_frontend_backend_connection():
    """Probar conexion entre frontend y backend"""
    try:
        print("Probando conexion frontend -> backend...")
        
        # Probar endpoint de token (sin autenticacion)
        response = requests.get('http://localhost:8000/api/v1/token', timeout=10)
        print(f"Endpoint token: Status {response.status_code}")
        
        if response.status_code == 200:
            print("Backend respondiendo correctamente")
            return True
        else:
            print(f"Error en backend: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"Error conectando al backend: {e}")
        return False

def test_login_flow():
    """Probar flujo de login completo"""
    try:
        print("\nProbando flujo de login...")
        
        # Datos de login
        login_data = {
            'username': 'testuser',
            'password': 'testpassword'
        }
        
        # Headers para la peticion
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        # Realizar login
        response = requests.post(
            'http://localhost:8000/api/v1/token',
            data=login_data,
            headers=headers,
            timeout=10
        )
        
        print(f"Login response status: {response.status_code}")
        
        if response.status_code == 200:
            token_data = response.json()
            token = token_data.get('access_token')
            print(f"Token obtenido: {token[:50]}...")
            
            # Probar endpoint protegido con el token
            auth_headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            # Probar endpoint de documentos
            docs_response = requests.get(
                'http://localhost:8000/api/v1/documents/',
                headers=auth_headers,
                timeout=10
            )
            
            print(f"Documentos endpoint: Status {docs_response.status_code}")
            
            if docs_response.status_code == 200:
                docs_data = docs_response.json()
                print(f"Documentos obtenidos: {docs_data}")
                return True
            else:
                print(f"Error obteniendo documentos: {docs_response.text}")
                return False
                
        else:
            print(f"Error en login: {response.text}")
            return False
            
    except Exception as e:
        print(f"Error en flujo de login: {e}")
        return False

def test_database_through_api():
    """Probar acceso a base de datos a traves de la API"""
    try:
        print("\nProbando acceso a base de datos via API...")
        
        # Login primero
        login_data = {
            'username': 'testuser',
            'password': 'testpassword'
        }
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        response = requests.post(
            'http://localhost:8000/api/v1/token',
            data=login_data,
            headers=headers,
            timeout=10
        )
        
        if response.status_code != 200:
            print("No se pudo hacer login")
            return False
            
        token = response.json().get('access_token')
        
        # Probar endpoints que acceden a la base de datos
        auth_headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        # Probar endpoint de documentos (lee de la BD)
        docs_response = requests.get(
            'http://localhost:8000/api/v1/documents/',
            headers=auth_headers,
            timeout=10
        )
        
        print(f"Documentos desde BD: Status {docs_response.status_code}")
        
        if docs_response.status_code == 200:
            docs_data = docs_response.json()
            print(f"Total documentos en BD: {docs_data.get('total', 0)}")
            print("Conexion a base de datos via API: EXITOSA")
            return True
        else:
            print(f"Error accediendo a BD via API: {docs_response.text}")
            return False
            
    except Exception as e:
        print(f"Error probando BD via API: {e}")
        return False

def test_frontend_availability():
    """Probar que el frontend este disponible"""
    try:
        print("Probando disponibilidad del frontend...")
        
        response = requests.get('http://localhost:3000', timeout=10)
        print(f"Frontend status: {response.status_code}")
        
        if response.status_code == 200:
            print("Frontend disponible")
            return True
        else:
            print("Frontend no disponible")
            return False
            
    except Exception as e:
        print(f"Error accediendo al frontend: {e}")
        return False

def main():
    """Funcion principal"""
    print("PRUEBA DE CONEXION FRONTEND -> BACKEND -> BASE DE DATOS")
    print("=" * 60)
    
    results = []
    
    # Probar frontend
    results.append(("Frontend", test_frontend_availability()))
    
    # Probar backend
    results.append(("Backend", test_frontend_backend_connection()))
    
    # Probar login
    results.append(("Login", test_login_flow()))
    
    # Probar BD via API
    results.append(("Base de Datos via API", test_database_through_api()))
    
    # Resumen
    print("\n" + "=" * 60)
    print("RESUMEN DE PRUEBAS")
    print("=" * 60)
    
    for service, success in results:
        status = "EXITOSO" if success else "FALLO"
        print(f"{service:25} {status}")
    
    all_success = all(result[1] for result in results)
    
    if all_success:
        print("\nTodas las conexiones funcionan correctamente!")
        print("El frontend se conecta correctamente al backend y la base de datos")
        print("\nPuedes usar el frontend en: http://localhost:3000")
        print("Credenciales de login:")
        print("  Usuario: testuser")
        print("  Contraseña: testpassword")
    else:
        print("\nAlgunas conexiones fallaron")
        print("Revisa la configuracion de los servicios")
    
    return 0 if all_success else 1

if __name__ == "__main__":
    sys.exit(main())

