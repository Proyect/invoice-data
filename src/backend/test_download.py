#!/usr/bin/env python3
"""
Script para probar el endpoint de descarga
"""

import requests
import json

def test_download():
    """Probar el endpoint de descarga"""
    base_url = "http://localhost:8000"
    
    # 1. Primero hacer login para obtener el token
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
        print(f"✅ Login exitoso, token obtenido")
        
    except Exception as e:
        print(f"❌ Error en login: {e}")
        return
    
    # 2. Obtener lista de documentos
    print("\n📄 Obteniendo lista de documentos...")
    try:
        headers = {'Authorization': f'Bearer {token}'}
        docs_response = requests.get(f"{base_url}/api/v1/documents/", headers=headers)
        
        if docs_response.status_code != 200:
            print(f"❌ Error obteniendo documentos: {docs_response.status_code}")
            print(f"Response: {docs_response.text}")
            return
            
        docs_data = docs_response.json()
        documents = docs_data.get('documents', [])
        
        if not documents:
            print("❌ No hay documentos disponibles para descargar")
            return
            
        print(f"✅ Encontrados {len(documents)} documentos")
        
        # Mostrar documentos disponibles
        for i, doc in enumerate(documents[:3]):  # Mostrar solo los primeros 3
            print(f"  {i+1}. {doc['original_filename']} (ID: {doc['id']})")
            
    except Exception as e:
        print(f"❌ Error obteniendo documentos: {e}")
        return
    
    # 3. Probar descarga del primer documento
    if documents:
        first_doc = documents[0]
        doc_id = first_doc['id']
        filename = first_doc['original_filename']
        
        print(f"\n⬇️ Probando descarga de: {filename}")
        print(f"ID: {doc_id}")
        
        try:
            download_response = requests.get(
                f"{base_url}/api/v1/documents/{doc_id}/download",
                headers=headers,
                stream=True
            )
            
            print(f"Status: {download_response.status_code}")
            print(f"Headers: {dict(download_response.headers)}")
            
            if download_response.status_code == 200:
                # Guardar el archivo descargado
                with open(f"downloaded_{filename}", "wb") as f:
                    for chunk in download_response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                print(f"✅ Descarga exitosa! Archivo guardado como: downloaded_{filename}")
            else:
                print(f"❌ Error en descarga: {download_response.text}")
                
        except Exception as e:
            print(f"❌ Error en descarga: {e}")

if __name__ == "__main__":
    test_download()

