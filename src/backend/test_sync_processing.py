#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# test_sync_processing.py - Script para probar el procesamiento síncrono

import requests
import json
import time
import sys

# Configurar encoding para Windows
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

# Configuración
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

def create_test_user():
    """Crear un usuario de prueba"""
    user_data = {
        "username": "test_user",
        "email": "test@example.com",
        "password": "test123456"
    }
    
    try:
        response = requests.post(f"{API_BASE}/auth/register", json=user_data)
        if response.status_code == 201:
            print("✅ Usuario de prueba creado exitosamente")
            return True
        elif response.status_code == 400 and "already registered" in response.text:
            print("ℹ️ Usuario de prueba ya existe")
            return True
        else:
            print(f"❌ Error creando usuario: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error de conexión creando usuario: {e}")
        return False

def login_user():
    """Iniciar sesión y obtener token"""
    login_data = {
        "username": "testuser",
        "password": "testpassword"
    }
    
    try:
        response = requests.post(f"{API_BASE}/token", data=login_data)
        if response.status_code == 200:
            token_data = response.json()
            print("✅ Login exitoso")
            return token_data["access_token"]
        else:
            print(f"❌ Error en login: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error de conexión en login: {e}")
        return None

def create_test_image():
    """Crear una imagen de prueba simple"""
    try:
        from PIL import Image, ImageDraw, ImageFont
        import io
        
        # Crear imagen de 400x300 píxeles
        img = Image.new('RGB', (400, 300), color='white')
        draw = ImageDraw.Draw(img)
        
        # Dibujar texto simulando un documento
        try:
            # Intentar usar una fuente del sistema
            font = ImageFont.truetype("arial.ttf", 20)
        except OSError:
            # Usar fuente por defecto si no encuentra arial
            font = ImageFont.load_default()
        
        draw.text((50, 50), "DOCUMENTO DE PRUEBA", fill='black', font=font)
        draw.text((50, 100), "Nombre: Juan Pérez", fill='black', font=font)
        draw.text((50, 150), "DNI: 12345678", fill='black', font=font)
        draw.text((50, 200), "Fecha: 2024-01-01", fill='black', font=font)
        
        # Guardar en memoria como bytes
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        return img_bytes.getvalue()
    except ImportError:
        print("⚠️ PIL no disponible, creando archivo de prueba básico")
        # Crear un archivo PNG mínimo válido
        return b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x01\x90\x00\x00\x01,\x08\x02\x00\x00\x00\xa0\x9c\x18\x19\x00\x00\x00\x19tEXtSoftware\x00Adobe ImageReadyq\xc9e<\x00\x00\x00\x0eIDATx\xdac\xf8\x0f\x00\x00\x01\x00\x01\x00\x18\xdd\x8d\xb4\x00\x00\x00\x00IEND\xaeB`\x82'

def test_document_upload_and_processing(token):
    """Probar subida y procesamiento de documento"""
    print("\n🔄 Probando subida y procesamiento de documento...")
    
    # Crear imagen de prueba
    image_data = create_test_image()
    
    # Preparar archivos y datos
    files = {
        'file': ('test_document.png', image_data, 'image/png')
    }
    
    params = {
        'document_type': 'DNI_FRONT'
    }
    
    headers = {
        'Authorization': f'Bearer {token}'
    }
    
    try:
        # Subir documento
        response = requests.post(
            f"{API_BASE}/documents/upload",
            files=files,
            params=params,
            headers=headers
        )
        
        if response.status_code in [200, 202]:
            result = response.json()
            document_id = result['document_id']
            print(f"✅ Documento subido exitosamente. ID: {document_id}")
            print(f"   Estado: {result['status']}")
            print(f"   Mensaje: {result['message']}")
            
            # Si el procesamiento es síncrono, el documento debería estar COMPLETED
            if result['status'] == 'COMPLETED':
                print("✅ Procesamiento síncrono completado exitosamente")
                return test_extracted_data(token, document_id)
            else:
                print("ℹ️ Documento en cola, esperando procesamiento...")
                return test_document_status_polling(token, document_id)
                
        else:
            print(f"❌ Error subiendo documento: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error de conexión subiendo documento: {e}")
        return False

def test_document_status_polling(token, document_id):
    """Verificar estado del documento con polling"""
    headers = {'Authorization': f'Bearer {token}'}
    
    for attempt in range(10):  # Máximo 10 intentos
        try:
            response = requests.get(
                f"{API_BASE}/documents/{document_id}/status",
                headers=headers
            )
            
            if response.status_code == 200:
                status_data = response.json()
                print(f"   Intento {attempt + 1}: Estado = {status_data['status']}")
                
                if status_data['status'] == 'COMPLETED':
                    print("✅ Documento procesado exitosamente")
                    return test_extracted_data(token, document_id)
                elif status_data['status'] == 'FAILED':
                    print(f"❌ Procesamiento falló: {status_data.get('processing_error', 'Error desconocido')}")
                    return False
                    
            time.sleep(2)  # Esperar 2 segundos antes del siguiente intento
            
        except Exception as e:
            print(f"❌ Error verificando estado: {e}")
            
    print("❌ Timeout esperando procesamiento")
    return False

def test_extracted_data(token, document_id):
    """Probar obtención de datos extraídos"""
    print(f"\n🔍 Probando datos extraídos del documento {document_id}...")
    
    headers = {'Authorization': f'Bearer {token}'}
    
    try:
        response = requests.get(
            f"{API_BASE}/documents/{document_id}/extracted_data",
            headers=headers
        )
        
        if response.status_code == 200:
            extracted_data = response.json()
            print("✅ Datos extraídos obtenidos exitosamente:")
            print(json.dumps(extracted_data, indent=2, ensure_ascii=False))
            return True
        elif response.status_code == 409:
            print("❌ Error 409: Documento no procesado aún (este era el error original)")
            return False
        else:
            print(f"❌ Error obteniendo datos extraídos: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error de conexión obteniendo datos: {e}")
        return False

def main():
    """Función principal de prueba"""
    print("Iniciando pruebas del procesamiento sincrono de documentos")
    print("=" * 60)
    
    # Verificar que el servidor esté ejecutándose
    try:
        response = requests.get(f"{BASE_URL}/docs")
        if response.status_code != 200:
            print("❌ El servidor no está ejecutándose en http://localhost:8000")
            return
    except requests.RequestException:
        print("No se puede conectar al servidor en http://localhost:8000")
        return
    
    print("✅ Servidor detectado en http://localhost:8000")
    
    # Saltar creación de usuario (no hay endpoint de registro)
    print("ℹ️ Usando usuario existente para pruebas")
    
    # Iniciar sesión
    token = login_user()
    if not token:
        return
    
    # Probar subida y procesamiento
    success = test_document_upload_and_processing(token)
    
    print("\n" + "=" * 60)
    if success:
        print("TODAS LAS PRUEBAS PASARON! El error 409 ha sido resuelto.")
    else:
        print("Algunas pruebas fallaron. Revisar logs para mas detalles.")

if __name__ == "__main__":
    main()
