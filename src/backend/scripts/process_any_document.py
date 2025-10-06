#!/usr/bin/env python3
"""
Script para procesar cualquier tipo de documento con el sistema OCR universal
"""

import sys
import os
from pathlib import Path
import json
import argparse
from datetime import datetime

# Agregar el directorio backend al path
sys.path.append(str(Path(__file__).parent.parent))

from services.universal_ocr_service import UniversalOCRService
from services.universal_image_preprocessor import UniversalImagePreprocessor

def process_document(image_path: str, document_type: str = "UNKNOWN", output_file: str = None):
    """
    Procesa un documento y extrae datos estructurados
    
    Args:
        image_path: Ruta a la imagen del documento
        document_type: Tipo de documento (opcional)
        output_file: Archivo de salida para los resultados (opcional)
    """
    print("🚀 PROCESADOR UNIVERSAL DE DOCUMENTOS")
    print("=" * 50)
    print(f"📄 Imagen: {image_path}")
    print(f"📋 Tipo: {document_type}")
    print()
    
    # Verificar que la imagen existe
    if not Path(image_path).exists():
        print(f"❌ Error: La imagen {image_path} no existe")
        return False
    
    try:
        # Crear servicio OCR
        ocr_service = UniversalOCRService()
        
        # Procesar documento
        print("🔄 Procesando documento...")
        result = ocr_service.process_document(image_path, document_type)
        
        # Mostrar resultados
        print("\n📊 RESULTADOS DEL PROCESAMIENTO")
        print("=" * 50)
        
        if result['success']:
            print(f"✅ Procesamiento exitoso")
            print(f"📋 Tipo detectado: {result['document_type']}")
            print(f"⭐ Calidad de imagen: {result['quality_score']:.1f}/100")
            print(f"🎯 Confianza: {result['confidence_score']:.1f}/100")
            
            print(f"\n📝 TEXTO EXTRAÍDO ({len(result['raw_text'])} caracteres):")
            print("-" * 30)
            print(result['raw_text'][:500] + "..." if len(result['raw_text']) > 500 else result['raw_text'])
            
            print(f"\n📊 DATOS ESTRUCTURADOS ({len(result['structured_data'])} campos):")
            print("-" * 30)
            for key, value in result['structured_data'].items():
                print(f"  {key}: {value}")
            
            print(f"\n💡 RECOMENDACIONES:")
            print("-" * 30)
            for rec in result['recommendations']:
                print(f"  • {rec}")
            
            # Guardar resultados si se especifica archivo de salida
            if output_file:
                save_results(result, output_file)
                print(f"\n💾 Resultados guardados en: {output_file}")
            
            return True
            
        else:
            print(f"❌ Error en el procesamiento: {result['error']}")
            return False
            
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def save_results(result: dict, output_file: str):
    """Guarda los resultados en un archivo JSON"""
    try:
        # Preparar datos para guardar
        save_data = {
            'timestamp': datetime.now().isoformat(),
            'success': result['success'],
            'document_type': result['document_type'],
            'quality_score': result['quality_score'],
            'confidence_score': result['confidence_score'],
            'raw_text': result['raw_text'],
            'structured_data': result['structured_data'],
            'recommendations': result['recommendations']
        }
        
        # Guardar en JSON
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, indent=2, ensure_ascii=False)
            
    except Exception as e:
        print(f"⚠️  Error guardando resultados: {e}")

def test_with_sample_images():
    """Prueba el sistema con imágenes de muestra"""
    print("🧪 PRUEBA CON IMÁGENES DE MUESTRA")
    print("=" * 50)
    
    # Buscar imágenes de prueba
    test_images = []
    
    # Buscar en directorios comunes
    search_dirs = [
        "datasets/invoices_argentina_synthetic/images/train",
        "datasets/invoices_argentina_advanced/images/train",
        "datasets/universal_documents/images/train",
        "uploaded_documents_local",
        "tests"
    ]
    
    for search_dir in search_dirs:
        if Path(search_dir).exists():
            for img_file in Path(search_dir).glob("*.jpg"):
                test_images.append(str(img_file))
                if len(test_images) >= 3:  # Limitar a 3 imágenes para prueba
                    break
            if test_images:
                break
    
    if not test_images:
        print("❌ No se encontraron imágenes de prueba")
        return False
    
    print(f"📁 Encontradas {len(test_images)} imágenes de prueba")
    
    # Procesar cada imagen
    success_count = 0
    for i, img_path in enumerate(test_images, 1):
        print(f"\n🔄 Procesando imagen {i}/{len(test_images)}: {Path(img_path).name}")
        
        if process_document(img_path, "UNKNOWN"):
            success_count += 1
    
    print(f"\n📊 RESUMEN DE PRUEBAS")
    print("=" * 30)
    print(f"✅ Exitosas: {success_count}/{len(test_images)}")
    print(f"❌ Fallidas: {len(test_images) - success_count}/{len(test_images)}")
    
    return success_count == len(test_images)

def main():
    """Función principal"""
    parser = argparse.ArgumentParser(description='Procesador Universal de Documentos OCR')
    parser.add_argument('image_path', nargs='?', help='Ruta a la imagen del documento')
    parser.add_argument('--type', '-t', default='UNKNOWN', help='Tipo de documento (FACTURA, DNI, RECIBO, TARJETA, CONTRATO)')
    parser.add_argument('--output', '-o', help='Archivo de salida para los resultados (JSON)')
    parser.add_argument('--test', action='store_true', help='Ejecutar pruebas con imágenes de muestra')
    
    args = parser.parse_args()
    
    if args.test:
        # Modo de prueba
        success = test_with_sample_images()
        sys.exit(0 if success else 1)
    
    elif args.image_path:
        # Modo de procesamiento
        success = process_document(args.image_path, args.type, args.output)
        sys.exit(0 if success else 1)
    
    else:
        # Mostrar ayuda
        print("🚀 PROCESADOR UNIVERSAL DE DOCUMENTOS OCR")
        print("=" * 50)
        print()
        print("Uso:")
        print("  python process_any_document.py <imagen> [opciones]")
        print("  python process_any_document.py --test")
        print()
        print("Opciones:")
        print("  --type, -t     Tipo de documento (FACTURA, DNI, RECIBO, TARJETA, CONTRATO)")
        print("  --output, -o   Archivo de salida para resultados (JSON)")
        print("  --test         Ejecutar pruebas con imágenes de muestra")
        print()
        print("Ejemplos:")
        print("  python process_any_document.py mi_factura.jpg")
        print("  python process_any_document.py mi_dni.jpg --type DNI --output resultado.json")
        print("  python process_any_document.py --test")
        print()
        sys.exit(1)

if __name__ == "__main__":
    main()

