#!/usr/bin/env python3
"""
Script de prueba para verificar la funcionalidad de eliminación de documentos.
Prueba los endpoints DELETE y GET de documentos.
"""

import requests
import json
import sys
import os
from pathlib import Path

# Configuración del servidor
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

def test_delete_functionality():
    """Prueba completa de la funcionalidad de eliminación de documentos."""
    
    print("🧪 Iniciando pruebas de eliminación de documentos...")
    
    # 1. Crear usuario de prueba y obtener token
    print("\n1. Creando usuario de prueba...")
    
    # Datos del usuario de prueba
    test_user = {
        "username": "test_delete_user",
        "email": "test_delete@example.com",
        "password": "testpassword123"
    }
    
    # Registrar usuario
    try:
        response = requests.post(f"{API_BASE}/auth/register", json=test_user)
        if response.status_code == 201:
            print("✅ Usuario creado exitosamente")
        elif response.status_code == 400 and "already registered" in response.text:
            print("ℹ️ Usuario ya existe, continuando...")
        else:
            print(f"❌ Error creando usuario: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error de conexión al crear usuario: {e}")
        return False
    
    # Obtener token
    try:
        login_data = {
            "username": test_user["username"],
            "password": test_user["password"]
        }
        response = requests.post(f"{API_BASE}/auth/token", data=login_data)
        if response.status_code == 200:
            token = response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            print("✅ Token obtenido exitosamente")
        else:
            print(f"❌ Error obteniendo token: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error de conexión al obtener token: {e}")
        return False
    
    # 2. Subir un documento de prueba
    print("\n2. Subiendo documento de prueba...")
    
    # Crear una imagen de prueba simple
    test_image_content = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\nIDATx\x9cc\xf8\x00\x00\x00\x01\x00\x01\x00\x00\x00\x00IEND\xaeB`\x82'
    
    try:
        files = {
            'file': ('test_document.png', test_image_content, 'image/png')
        }
        data = {
            'document_type': 'invoice'
        }
        
        response = requests.post(f"{API_BASE}/documents/upload", 
                               files=files, 
                               data=data, 
                               headers=headers)
        
        if response.status_code == 202:
            document_data = response.json()
            document_id = document_data["document_id"]
            print(f"✅ Documento subido exitosamente. ID: {document_id}")
        else:
            print(f"❌ Error subiendo documento: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error de conexión al subir documento: {e}")
        return False
    
    # 3. Verificar que el documento existe
    print("\n3. Verificando que el documento existe...")
    
    try:
        response = requests.get(f"{API_BASE}/documents/{document_id}", headers=headers)
        if response.status_code == 200:
            print("✅ Documento encontrado correctamente")
        else:
            print(f"❌ Error obteniendo documento: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error de conexión al obtener documento: {e}")
        return False
    
    # 4. Listar documentos del usuario
    print("\n4. Listando documentos del usuario...")
    
    try:
        response = requests.get(f"{API_BASE}/documents/", headers=headers)
        if response.status_code == 200:
            documents_list = response.json()
            print(f"✅ Documentos listados: {documents_list['total']} documentos encontrados")
            
            # Verificar que nuestro documento está en la lista
            found = False
            for doc in documents_list['documents']:
                if doc['id'] == document_id:
                    found = True
                    break
            
            if found:
                print("✅ Documento encontrado en la lista")
            else:
                print("❌ Documento no encontrado en la lista")
                return False
        else:
            print(f"❌ Error listando documentos: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error de conexión al listar documentos: {e}")
        return False
    
    # 5. Eliminar el documento
    print("\n5. Eliminando el documento...")
    
    try:
        response = requests.delete(f"{API_BASE}/documents/{document_id}", headers=headers)
        if response.status_code == 204:
            print("✅ Documento eliminado exitosamente")
        else:
            print(f"❌ Error eliminando documento: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error de conexión al eliminar documento: {e}")
        return False
    
    # 6. Verificar que el documento ya no existe
    print("\n6. Verificando que el documento fue eliminado...")
    
    try:
        response = requests.get(f"{API_BASE}/documents/{document_id}", headers=headers)
        if response.status_code == 404:
            print("✅ Documento eliminado correctamente (404 Not Found)")
        else:
            print(f"❌ El documento aún existe: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error de conexión al verificar eliminación: {e}")
        return False
    
    # 7. Verificar que la lista de documentos ya no lo incluye
    print("\n7. Verificando que el documento no aparece en la lista...")
    
    try:
        response = requests.get(f"{API_BASE}/documents/", headers=headers)
        if response.status_code == 200:
            documents_list = response.json()
            
            # Verificar que nuestro documento NO está en la lista
            found = False
            for doc in documents_list['documents']:
                if doc['id'] == document_id:
                    found = True
                    break
            
            if not found:
                print("✅ Documento no aparece en la lista (eliminado correctamente)")
            else:
                print("❌ Documento aún aparece en la lista")
                return False
        else:
            print(f"❌ Error listando documentos: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error de conexión al listar documentos: {e}")
        return False
    
    # 8. Probar eliminación de documento inexistente
    print("\n8. Probando eliminación de documento inexistente...")
    
    try:
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = requests.delete(f"{API_BASE}/documents/{fake_id}", headers=headers)
        if response.status_code == 404:
            print("✅ Error 404 correcto para documento inexistente")
        else:
            print(f"⚠️ Respuesta inesperada para documento inexistente: {response.status_code}")
    except Exception as e:
        print(f"❌ Error de conexión al probar documento inexistente: {e}")
        return False
    
    print("\n🎉 ¡Todas las pruebas de eliminación pasaron exitosamente!")
    return True

def check_server_status():
    """Verifica si el servidor está ejecutándose."""
    try:
        response = requests.get(f"{BASE_URL}/docs", timeout=5)
        return response.status_code == 200
    except:
        return False

if __name__ == "__main__":
    print("🚀 Script de prueba para funcionalidad de eliminación de documentos")
    print("=" * 60)
    
    # Verificar que el servidor esté ejecutándose
    if not check_server_status():
        print("❌ El servidor no está ejecutándose en http://localhost:8000")
        print("   Por favor, ejecuta el servidor con: python run_local.py")
        sys.exit(1)
    
    # Ejecutar pruebas
    success = test_delete_functionality()
    
    if success:
        print("\n✅ Todas las pruebas completadas exitosamente")
        sys.exit(0)
    else:
        print("\n❌ Algunas pruebas fallaron")
        sys.exit(1)
