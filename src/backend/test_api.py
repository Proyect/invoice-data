#!/usr/bin/env python3
"""
Script de prueba para la API OCR
"""

import requests
import json
import os

# Configuración
API_BASE_URL = "http://localhost:8000"
TEST_USER = "testuser"
TEST_PASSWORD = "testpassword"
TEST_IMAGE = "example_dataset/images/test_invoice.jpg"

def test_authentication():
    """Prueba el endpoint de autenticación"""
    print("🔐 Probando autenticación...")
    
    url = f"{API_BASE_URL}/api/v1/token"
    data = {
        "username": TEST_USER,
        "password": TEST_PASSWORD
    }
    
    try:
        response = requests.post(url, data=data)
        response.raise_for_status()
        
        token_data = response.json()
        print(f"✅ Autenticación exitosa")
        print(f"Token: {token_data['access_token'][:50]}...")
        return token_data['access_token']
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error en autenticación: {e}")
        return None

def test_upload_document(token):
    """Prueba el endpoint de subida de documentos"""
    print("\n📤 Probando subida de documento...")
    
    if not os.path.exists(TEST_IMAGE):
        print(f"❌ Imagen de prueba no encontrada: {TEST_IMAGE}")
        return None
    
    url = f"{API_BASE_URL}/api/v1/documents/upload"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    files = {
        "file": (os.path.basename(TEST_IMAGE), open(TEST_IMAGE, "rb"), "image/jpeg")
    }
    
    params = {
        "document_type": "INVOICE_A"
    }
    
    try:
        response = requests.post(url, headers=headers, files=files, params=params)
        response.raise_for_status()
        
        result = response.json()
        print(f"✅ Documento subido exitosamente")
        print(f"Document ID: {result['document_id']}")
        print(f"Status: {result['status']}")
        print(f"Message: {result['message']}")
        return result['document_id']
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error subiendo documento: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")
        return None
    finally:
        files["file"][1].close()

def test_document_status(token, document_id):
    """Prueba el endpoint de estado del documento"""
    print(f"\n📊 Probando estado del documento {document_id}...")
    
    url = f"{API_BASE_URL}/api/v1/documents/{document_id}/status"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        result = response.json()
        print(f"✅ Estado obtenido exitosamente")
        print(f"Status: {result['status']}")
        print(f"Document Type: {result['document_type']}")
        print(f"Uploaded At: {result['uploaded_at']}")
        return result
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error obteniendo estado: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")
        return None

def test_extracted_data(token, document_id):
    """Prueba el endpoint de datos extraídos"""
    print(f"\n📄 Probando datos extraídos del documento {document_id}...")
    
    url = f"{API_BASE_URL}/api/v1/documents/{document_id}/extracted_data"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        result = response.json()
        print(f"✅ Datos extraídos obtenidos exitosamente")
        print(f"Datos: {json.dumps(result, indent=2)}")
        return result
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error obteniendo datos extraídos: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")
        return None

def main():
    """Función principal de prueba"""
    print("🧪 INICIANDO PRUEBAS DE LA API OCR")
    print("=" * 50)
    
    # 1. Probar autenticación
    token = test_authentication()
    if not token:
        print("❌ No se pudo autenticar. Abortando pruebas.")
        return
    
    # 2. Probar subida de documento
    document_id = test_upload_document(token)
    if not document_id:
        print("❌ No se pudo subir documento. Abortando pruebas.")
        return
    
    # 3. Probar estado del documento
    status = test_document_status(token, document_id)
    if not status:
        print("❌ No se pudo obtener estado del documento.")
        return
    
    # 4. Esperar un poco para que se procese
    print("\n⏳ Esperando procesamiento...")
    import time
    time.sleep(5)
    
    # 5. Probar datos extraídos
    extracted_data = test_extracted_data(token, document_id)
    
    print("\n" + "=" * 50)
    print("🎉 PRUEBAS COMPLETADAS")
    print("=" * 50)

if __name__ == "__main__":
    main()
