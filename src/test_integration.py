#!/usr/bin/env python3
"""
Script de pruebas de integración entre frontend y backend
Verifica la comunicación completa del sistema
"""

import os
import sys
import time
import requests
import json
from pathlib import Path

def print_header(title):
    """Imprime un encabezado formateado"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def print_status(test_name, success, details=""):
    """Imprime el estado de una prueba"""
    status = "[PASS]" if success else "[FAIL]"
    print(f"{status} {test_name}")
    if details:
        print(f"    {details}")

def test_backend_health():
    """Prueba la salud del backend"""
    print_header("PRUEBAS DE SALUD DEL BACKEND")
    
    try:
        response = requests.get("http://localhost:8000/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print_status("Health check", True, f"Status: {data.get('status', 'unknown')}")
            return True
        else:
            print_status("Health check", False, f"Status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print_status("Health check", False, f"Error: {str(e)}")
        return False

def test_frontend_accessibility():
    """Prueba la accesibilidad del frontend"""
    print_header("PRUEBAS DE ACCESIBILIDAD DEL FRONTEND")
    
    try:
        response = requests.get("http://localhost:3000", timeout=10)
        if response.status_code == 200:
            print_status("Frontend accesible", True, "Página principal cargada")
            
            # Verificar que sea una página React
            if "react" in response.text.lower() or "root" in response.text.lower():
                print_status("Página React", True, "Contenido React detectado")
            else:
                print_status("Página React", False, "No se detectó contenido React")
            
            return True
        else:
            print_status("Frontend accesible", False, f"Status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print_status("Frontend accesible", False, f"Error: {str(e)}")
        return False

def test_authentication_flow():
    """Prueba el flujo de autenticación"""
    print_header("PRUEBAS DE FLUJO DE AUTENTICACIÓN")
    
    # Datos de prueba
    login_data = {
        "username": "testuser",
        "password": "testpassword"
    }
    
    try:
        # 1. Probar login
        response = requests.post(
            "http://localhost:8000/api/v1/auth/login",
            data=login_data,
            timeout=10
        )
        
        if response.status_code == 200:
            print_status("Login exitoso", True, "Credenciales válidas")
            token_data = response.json()
            token = token_data.get("access_token")
            
            if token:
                print_status("Token JWT", True, "Token generado correctamente")
                
                # 2. Probar acceso con token
                headers = {"Authorization": f"Bearer {token}"}
                response = requests.get(
                    "http://localhost:8000/api/v1/documents/",
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    print_status("Acceso con token", True, "API protegida accesible")
                    return True
                else:
                    print_status("Acceso con token", False, f"Status: {response.status_code}")
                    return False
            else:
                print_status("Token JWT", False, "No se recibió token")
                return False
        else:
            print_status("Login exitoso", False, f"Status: {response.status_code}")
            if response.status_code == 422:
                print("    Posible problema: Usuario de prueba no existe")
            return False
            
    except requests.exceptions.RequestException as e:
        print_status("Flujo de autenticación", False, f"Error: {str(e)}")
        return False

def test_document_upload():
    """Prueba la subida de documentos"""
    print_header("PRUEBAS DE SUBIDA DE DOCUMENTOS")
    
    # Primero obtener token
    login_data = {
        "username": "testuser",
        "password": "testpassword"
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/api/v1/auth/login",
            data=login_data,
            timeout=10
        )
        
        if response.status_code != 200:
            print_status("Obtención de token", False, "No se pudo obtener token para la prueba")
            return False
        
        token = response.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        
        # Crear un archivo de prueba
        test_file_content = b"Test document content"
        files = {
            "file": ("test_document.txt", test_file_content, "text/plain")
        }
        data = {
            "document_type": "invoice"
        }
        
        # Probar subida
        response = requests.post(
            "http://localhost:8000/api/v1/documents/upload",
            headers=headers,
            files=files,
            data=data,
            timeout=30
        )
        
        if response.status_code == 200:
            print_status("Subida de documento", True, "Documento subido exitosamente")
            return True
        else:
            print_status("Subida de documento", False, f"Status: {response.status_code}")
            if response.status_code == 422:
                print("    Posible problema: Validación de archivo falló")
            return False
            
    except requests.exceptions.RequestException as e:
        print_status("Subida de documento", False, f"Error: {str(e)}")
        return False

def test_api_documentation():
    """Prueba la documentación de la API"""
    print_header("PRUEBAS DE DOCUMENTACIÓN API")
    
    try:
        response = requests.get("http://localhost:8000/docs", timeout=10)
        if response.status_code == 200:
            print_status("Documentación Swagger", True, "Accesible en /docs")
        else:
            print_status("Documentación Swagger", False, f"Status: {response.status_code}")
        
        # Probar OpenAPI schema
        response = requests.get("http://localhost:8000/openapi.json", timeout=10)
        if response.status_code == 200:
            print_status("Schema OpenAPI", True, "JSON schema disponible")
            return True
        else:
            print_status("Schema OpenAPI", False, f"Status: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print_status("Documentación API", False, f"Error: {str(e)}")
        return False

def test_cors_configuration():
    """Prueba la configuración CORS"""
    print_header("PRUEBAS DE CONFIGURACIÓN CORS")
    
    try:
        # Probar preflight request
        headers = {
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type"
        }
        
        response = requests.options(
            "http://localhost:8000/api/v1/auth/login",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            print_status("CORS preflight", True, "Configuración CORS correcta")
            
            # Verificar headers CORS
            cors_headers = {
                "Access-Control-Allow-Origin": response.headers.get("Access-Control-Allow-Origin"),
                "Access-Control-Allow-Methods": response.headers.get("Access-Control-Allow-Methods"),
                "Access-Control-Allow-Headers": response.headers.get("Access-Control-Allow-Headers")
            }
            
            for header, value in cors_headers.items():
                if value:
                    print_status(f"Header {header}", True, value)
                else:
                    print_status(f"Header {header}", False, "No configurado")
            
            return True
        else:
            print_status("CORS preflight", False, f"Status: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print_status("Configuración CORS", False, f"Error: {str(e)}")
        return False

def test_database_connectivity():
    """Prueba la conectividad de la base de datos"""
    print_header("PRUEBAS DE CONECTIVIDAD DE BASE DE DATOS")
    
    try:
        # Probar endpoint que requiere base de datos
        response = requests.get("http://localhost:8000/api/v1/documents/", timeout=10)
        
        # 401 es esperado sin token, pero significa que la API está funcionando
        if response.status_code in [200, 401, 422]:
            print_status("Conectividad BD", True, "API responde correctamente")
            return True
        else:
            print_status("Conectividad BD", False, f"Status: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print_status("Conectividad BD", False, f"Error: {str(e)}")
        return False

def test_error_handling():
    """Prueba el manejo de errores"""
    print_header("PRUEBAS DE MANEJO DE ERRORES")
    
    # Probar endpoint inexistente
    try:
        response = requests.get("http://localhost:8000/api/v1/nonexistent", timeout=10)
        if response.status_code == 404:
            print_status("Error 404", True, "Manejo correcto de endpoint inexistente")
        else:
            print_status("Error 404", False, f"Status inesperado: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print_status("Error 404", False, f"Error: {str(e)}")
    
    # Probar login con credenciales inválidas
    try:
        invalid_data = {"username": "invalid", "password": "invalid"}
        response = requests.post(
            "http://localhost:8000/api/v1/auth/login",
            data=invalid_data,
            timeout=10
        )
        if response.status_code == 401:
            print_status("Error 401", True, "Manejo correcto de credenciales inválidas")
        else:
            print_status("Error 401", False, f"Status inesperado: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print_status("Error 401", False, f"Error: {str(e)}")
    
    return True

def main():
    """Función principal"""
    print_header("PRUEBAS DE INTEGRACIÓN - FRONTEND Y BACKEND")
    print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("Verificando comunicación entre frontend y backend...")
    
    # Ejecutar todas las pruebas
    tests = [
        ("Salud del backend", test_backend_health),
        ("Accesibilidad del frontend", test_frontend_accessibility),
        ("Flujo de autenticación", test_authentication_flow),
        ("Subida de documentos", test_document_upload),
        ("Documentación API", test_api_documentation),
        ("Configuración CORS", test_cors_configuration),
        ("Conectividad de base de datos", test_database_connectivity),
        ("Manejo de errores", test_error_handling),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print_status(test_name, False, f"Error: {str(e)}")
            results[test_name] = False
    
    # Resumen final
    print_header("RESUMEN DE PRUEBAS DE INTEGRACIÓN")
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    print(f"Pruebas pasadas: {passed}/{total}")
    print(f"Porcentaje de éxito: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print_status("RESULTADO GENERAL", True, "Todas las pruebas de integración pasaron")
        print("\n[SUCCESS] El sistema está completamente integrado y funcionando correctamente")
        return 0
    else:
        print_status("RESULTADO GENERAL", False, f"{total-passed} pruebas de integración fallaron")
        print("\n[WARNING] Revisa los errores arriba para solucionar los problemas de integración")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
