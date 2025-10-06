#!/usr/bin/env python3
"""
Script para procesar todos los documentos pendientes con las mejoras implementadas
- Procesa documentos pendientes automáticamente
- Aplica todas las mejoras implementadas
- Genera reportes de procesamiento
- Monitorea el rendimiento del sistema
"""

import sys
import os
import uuid
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
import logging

# Agregar el directorio del backend al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configurar logging mejorado
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/document_processing.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def process_all_pending_documents():
    """Procesa todos los documentos pendientes con las mejoras implementadas"""
    
    print("🚀 PROCESADOR DE DOCUMENTOS PENDIENTES MEJORADO")
    print("=" * 80)
    print(f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    try:
        # Importar servicios
        from database import SessionLocal
        from models.documents import Document
        from services.sync_ocr_service import process_document_sync
        
        db = SessionLocal()
        
        # Obtener todos los documentos pendientes
        pending_documents = db.query(Document).filter(Document.status == 'PENDING').all()
        
        if not pending_documents:
            print("✅ No hay documentos pendientes para procesar")
            return
        
        print(f"📋 Documentos pendientes encontrados: {len(pending_documents)}")
        
        # Estadísticas
        stats = {
            "total": len(pending_documents),
            "success": 0,
            "failed": 0,
            "processing_times": [],
            "fields_extracted": 0,
            "errors": []
        }
        
        # Procesar cada documento
        for i, doc in enumerate(pending_documents, 1):
            print(f"\n📄 Procesando documento {i}/{len(pending_documents)}: {doc.id}")
            print(f"   Archivo: {doc.original_filename}")
            print(f"   Tipo: {doc.document_type}")
            print(f"   Subido: {doc.uploaded_at}")
            
            start_time = time.time()
            
            try:
                # Procesar documento con mejoras
                result = process_document_sync(doc.id)
                processing_time = time.time() - start_time
                
                if result["status"] == "success":
                    fields_count = result.get('fields_count', 0)
                    stats["success"] += 1
                    stats["fields_extracted"] += fields_count
                    stats["processing_times"].append(processing_time)
                    
                    print(f"   ✅ Procesado exitosamente en {processing_time:.2f}s")
                    print(f"   📊 Campos extraídos: {fields_count}")
                    
                    # Mostrar campos extraídos
                    extracted_data = result.get('extracted_data', {})
                    if extracted_data:
                        print(f"   📝 Campos encontrados:")
                        for field, data in extracted_data.items():
                            if isinstance(data, dict) and 'value' in data:
                                value = data['value'][:50] + "..." if len(data['value']) > 50 else data['value']
                                confidence = data.get('confidence', 0)
                                print(f"      - {field}: '{value}' (conf: {confidence:.2f})")
                
                else:
                    stats["failed"] += 1
                    error_msg = result.get('error', 'Unknown error')
                    stats["errors"].append(f"Documento {doc.id}: {error_msg}")
                    
                    print(f"   ❌ Error: {error_msg}")
                    
            except Exception as e:
                processing_time = time.time() - start_time
                stats["failed"] += 1
                stats["errors"].append(f"Documento {doc.id}: {str(e)}")
                
                print(f"   ❌ Excepción: {str(e)}")
                logger.error(f"Error procesando documento {doc.id}: {str(e)}", exc_info=True)
        
        db.close()
        
        # Generar reporte final
        generate_processing_report(stats)
        
    except Exception as e:
        print(f"❌ Error general: {str(e)}")
        logger.error(f"Error general en procesamiento: {str(e)}", exc_info=True)

def generate_processing_report(stats):
    """Genera un reporte detallado del procesamiento"""
    
    print("\n" + "=" * 80)
    print("📊 REPORTE DE PROCESAMIENTO")
    print("=" * 80)
    
    # Estadísticas básicas
    total = stats["total"]
    success = stats["success"]
    failed = stats["failed"]
    success_rate = (success / total * 100) if total > 0 else 0
    
    print(f"📄 Total de documentos: {total}")
    print(f"✅ Procesados exitosamente: {success}")
    print(f"❌ Fallidos: {failed}")
    print(f"📈 Tasa de éxito: {success_rate:.1f}%")
    print(f"📊 Total de campos extraídos: {stats['fields_extracted']}")
    
    # Tiempos de procesamiento
    if stats["processing_times"]:
        avg_time = sum(stats["processing_times"]) / len(stats["processing_times"])
        min_time = min(stats["processing_times"])
        max_time = max(stats["processing_times"])
        
        print(f"\n⏱️  Tiempos de procesamiento:")
        print(f"   Promedio: {avg_time:.2f}s")
        print(f"   Mínimo: {min_time:.2f}s")
        print(f"   Máximo: {max_time:.2f}s")
    
    # Errores
    if stats["errors"]:
        print(f"\n❌ Errores encontrados ({len(stats['errors'])}):")
        for error in stats["errors"][:5]:  # Mostrar solo los primeros 5
            print(f"   - {error}")
        if len(stats["errors"]) > 5:
            print(f"   ... y {len(stats['errors']) - 5} errores más")
    
    # Guardar reporte en archivo
    report_data = {
        "timestamp": datetime.now().isoformat(),
        "statistics": stats,
        "summary": {
            "total_documents": total,
            "successful": success,
            "failed": failed,
            "success_rate": success_rate,
            "total_fields_extracted": stats["fields_extracted"]
        }
    }
    
    report_file = Path("logs/processing_report.json")
    report_file.parent.mkdir(exist_ok=True)
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 Reporte guardado en: {report_file}")
    
    # Recomendaciones
    print(f"\n💡 Recomendaciones:")
    if success_rate < 70:
        print("   - Tasa de éxito baja, revisar calidad de imágenes")
        print("   - Considerar mejoras adicionales en preprocesamiento")
    elif success_rate < 90:
        print("   - Tasa de éxito aceptable, monitorear errores")
    else:
        print("   - Excelente tasa de éxito, sistema funcionando bien")
    
    if stats["fields_extracted"] == 0:
        print("   - No se extrajeron campos, revisar modelos YOLO")
    elif stats["fields_extracted"] < total * 2:
        print("   - Pocos campos extraídos por documento, optimizar detección")
    else:
        print("   - Buena extracción de campos, sistema funcionando bien")

def monitor_system_health():
    """Monitorea la salud del sistema"""
    
    print("\n🔍 MONITOREO DE SALUD DEL SISTEMA")
    print("-" * 50)
    
    try:
        # Verificar componentes
        from services.ocr_service import is_tesseract_available
        from services.sync_ocr_service import is_redis_available
        from database import SessionLocal
        from models.documents import Document
        
        # Tesseract
        if is_tesseract_available():
            print("✅ Tesseract: Disponible")
        else:
            print("❌ Tesseract: No disponible")
        
        # Redis
        if is_redis_available():
            print("✅ Redis: Disponible")
        else:
            print("⚠️  Redis: No disponible (usando procesamiento síncrono)")
        
        # Base de datos
        db = SessionLocal()
        total_docs = db.query(Document).count()
        pending_docs = db.query(Document).filter(Document.status == 'PENDING').count()
        completed_docs = db.query(Document).filter(Document.status == 'COMPLETED').count()
        failed_docs = db.query(Document).filter(Document.status == 'FAILED').count()
        
        print(f"✅ Base de datos: Conectada")
        print(f"   📄 Total documentos: {total_docs}")
        print(f"   ⏳ Pendientes: {pending_docs}")
        print(f"   ✅ Completados: {completed_docs}")
        print(f"   ❌ Fallidos: {failed_docs}")
        
        db.close()
        
        # Modelos YOLO
        models_path = Path("models/yolo_models")
        available_models = []
        if models_path.exists():
            for model_dir in models_path.iterdir():
                if model_dir.is_dir():
                    weights_path = model_dir / "weights" / "best.pt"
                    if weights_path.exists():
                        available_models.append(model_dir.name)
        
        print(f"✅ Modelos YOLO: {len(available_models)} disponibles")
        for model in available_models[:3]:  # Mostrar solo los primeros 3
            print(f"   - {model}")
        if len(available_models) > 3:
            print(f"   ... y {len(available_models) - 3} más")
        
    except Exception as e:
        print(f"❌ Error en monitoreo: {str(e)}")

if __name__ == "__main__":
    # Crear directorio de logs si no existe
    Path("logs").mkdir(exist_ok=True)
    
    # Monitorear salud del sistema
    monitor_system_health()
    
    # Procesar documentos pendientes
    process_all_pending_documents()
    
    print("\n🎯 PROCESAMIENTO COMPLETADO")
    print("=" * 80)



























