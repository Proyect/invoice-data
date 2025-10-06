#!/usr/bin/env python3
"""
Script para Procesar Documentos Pendientes con Procesador Rápido
===============================================================

Este script procesa todos los documentos en estado PENDING usando el
procesador rápido optimizado que garantiza procesamiento en máximo 30 segundos.

Características:
- Procesamiento en lotes
- Timeouts estrictos
- Estadísticas detalladas
- Reintentos automáticos
- Logging completo
"""

import sys
import os
import time
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Agregar el directorio backend al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from services.document_service import get_documents_by_status
from services.fast_ocr_service import process_document_fast_sync, fast_processor

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pending_processing.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PendingDocumentProcessor:
    """Procesador de documentos pendientes optimizado"""
    
    def __init__(self, batch_size: int = 5, max_retries: int = 2):
        self.batch_size = batch_size
        self.max_retries = max_retries
        self.stats = {
            'total_found': 0,
            'processed': 0,
            'failed': 0,
            'timeout': 0,
            'retried': 0,
            'start_time': None,
            'end_time': None,
            'processing_times': []
        }
    
    def get_pending_documents(self, limit: int = None) -> List[Dict[str, Any]]:
        """Obtiene documentos pendientes de la base de datos"""
        db = SessionLocal()
        try:
            # Obtener documentos pendientes
            pending_docs = get_documents_by_status(db, 'PENDING', limit=limit)
            
            documents = []
            for doc in pending_docs:
                documents.append({
                    'id': str(doc.id),
                    'filename': doc.original_filename,
                    'document_type': doc.document_type,
                    'uploaded_at': doc.uploaded_at,
                    'user_id': str(doc.user_id) if doc.user_id else None
                })
            
            logger.info(f"📋 Encontrados {len(documents)} documentos pendientes")
            return documents
            
        except Exception as e:
            logger.error(f"Error obteniendo documentos pendientes: {e}")
            return []
        finally:
            db.close()
    
    def process_document_with_retry(self, doc_info: Dict[str, Any]) -> Dict[str, Any]:
        """Procesa un documento con reintentos automáticos"""
        doc_id = doc_info['id']
        filename = doc_info['filename']
        
        for attempt in range(self.max_retries + 1):
            try:
                logger.info(f"🔄 Procesando {filename} (intento {attempt + 1}/{self.max_retries + 1})")
                
                start_time = time.time()
                result = process_document_fast_sync(doc_id)
                processing_time = time.time() - start_time
                
                if result['status'] == 'success':
                    logger.info(f"✅ {filename} procesado exitosamente en {processing_time:.2f}s")
                    return {
                        'status': 'success',
                        'document_id': doc_id,
                        'filename': filename,
                        'processing_time': processing_time,
                        'attempts': attempt + 1,
                        'extracted_data': result.get('extracted_data', {})
                    }
                elif result['status'] == 'timeout':
                    logger.warning(f"⏰ {filename} excedió timeout en {processing_time:.2f}s")
                    if attempt < self.max_retries:
                        logger.info(f"🔄 Reintentando {filename}...")
                        time.sleep(2)  # Esperar 2s antes del reintento
                        continue
                    else:
                        return {
                            'status': 'timeout',
                            'document_id': doc_id,
                            'filename': filename,
                            'processing_time': processing_time,
                            'attempts': attempt + 1
                        }
                else:
                    logger.error(f"❌ Error procesando {filename}: {result.get('error', 'Unknown error')}")
                    if attempt < self.max_retries:
                        logger.info(f"🔄 Reintentando {filename}...")
                        time.sleep(2)
                        continue
                    else:
                        return {
                            'status': 'error',
                            'document_id': doc_id,
                            'filename': filename,
                            'processing_time': processing_time,
                            'attempts': attempt + 1,
                            'error': result.get('error', 'Unknown error')
                        }
            
            except Exception as e:
                processing_time = time.time() - start_time if 'start_time' in locals() else 0
                logger.error(f"❌ Excepción procesando {filename}: {e}")
                
                if attempt < self.max_retries:
                    logger.info(f"🔄 Reintentando {filename}...")
                    time.sleep(2)
                    continue
                else:
                    return {
                        'status': 'error',
                        'document_id': doc_id,
                        'filename': filename,
                        'processing_time': processing_time,
                        'attempts': attempt + 1,
                        'error': str(e)
                    }
        
        # No debería llegar aquí
        return {
            'status': 'error',
            'document_id': doc_id,
            'filename': filename,
            'error': 'Máximo de reintentos alcanzado'
        }
    
    def process_batch(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Procesa un lote de documentos"""
        results = []
        
        logger.info(f"📦 Procesando lote de {len(documents)} documentos")
        
        for i, doc_info in enumerate(documents, 1):
            logger.info(f"📄 [{i}/{len(documents)}] {doc_info['filename']}")
            
            result = self.process_document_with_retry(doc_info)
            results.append(result)
            
            # Actualizar estadísticas
            if result['status'] == 'success':
                self.stats['processed'] += 1
                self.stats['processing_times'].append(result['processing_time'])
            elif result['status'] == 'timeout':
                self.stats['timeout'] += 1
            else:
                self.stats['failed'] += 1
            
            if result.get('attempts', 1) > 1:
                self.stats['retried'] += 1
            
            # Pausa pequeña entre documentos para no sobrecargar
            time.sleep(0.5)
        
        return results
    
    def run(self, limit: int = None, max_batches: int = None) -> Dict[str, Any]:
        """Ejecuta el procesamiento de documentos pendientes"""
        self.stats['start_time'] = datetime.now()
        
        logger.info("🚀 INICIANDO PROCESAMIENTO DE DOCUMENTOS PENDIENTES")
        logger.info("=" * 60)
        
        try:
            # Obtener documentos pendientes
            all_documents = self.get_pending_documents(limit)
            self.stats['total_found'] = len(all_documents)
            
            if not all_documents:
                logger.info("✅ No hay documentos pendientes para procesar")
                return self.get_final_stats()
            
            # Procesar en lotes
            batch_count = 0
            all_results = []
            
            for i in range(0, len(all_documents), self.batch_size):
                if max_batches and batch_count >= max_batches:
                    logger.info(f"⏹️ Límite de lotes alcanzado ({max_batches})")
                    break
                
                batch = all_documents[i:i + self.batch_size]
                batch_count += 1
                
                logger.info(f"📦 LOTE {batch_count} - Documentos {i+1}-{min(i+self.batch_size, len(all_documents))}")
                
                batch_results = self.process_batch(batch)
                all_results.extend(batch_results)
                
                # Mostrar progreso
                processed_so_far = self.stats['processed'] + self.stats['failed'] + self.stats['timeout']
                logger.info(f"📊 Progreso: {processed_so_far}/{len(all_documents)} documentos procesados")
                
                # Pausa entre lotes
                if i + self.batch_size < len(all_documents):
                    logger.info("⏸️ Pausa entre lotes...")
                    time.sleep(2)
            
            # Estadísticas finales
            self.stats['end_time'] = datetime.now()
            final_stats = self.get_final_stats()
            
            logger.info("🏁 PROCESAMIENTO COMPLETADO")
            logger.info("=" * 60)
            self.print_final_stats(final_stats)
            
            return final_stats
            
        except Exception as e:
            logger.error(f"❌ Error crítico en procesamiento: {e}")
            self.stats['end_time'] = datetime.now()
            return self.get_final_stats()
    
    def get_final_stats(self) -> Dict[str, Any]:
        """Calcula estadísticas finales"""
        duration = None
        if self.stats['start_time'] and self.stats['end_time']:
            duration = (self.stats['end_time'] - self.stats['start_time']).total_seconds()
        
        avg_time = 0
        if self.stats['processing_times']:
            avg_time = sum(self.stats['processing_times']) / len(self.stats['processing_times'])
        
        return {
            'duration_seconds': duration,
            'duration_minutes': duration / 60 if duration else 0,
            'total_found': self.stats['total_found'],
            'processed': self.stats['processed'],
            'failed': self.stats['failed'],
            'timeout': self.stats['timeout'],
            'retried': self.stats['retried'],
            'success_rate': (self.stats['processed'] / self.stats['total_found'] * 100) if self.stats['total_found'] > 0 else 0,
            'avg_processing_time': avg_time,
            'fastest_time': min(self.stats['processing_times']) if self.stats['processing_times'] else 0,
            'slowest_time': max(self.stats['processing_times']) if self.stats['processing_times'] else 0,
            'processor_stats': fast_processor.get_stats()
        }
    
    def print_final_stats(self, stats: Dict[str, Any]):
        """Imprime estadísticas finales"""
        print(f"\n📊 ESTADÍSTICAS FINALES:")
        print(f"   ⏱️  Duración total: {stats['duration_minutes']:.1f} minutos")
        print(f"   📄 Documentos encontrados: {stats['total_found']}")
        print(f"   ✅ Procesados exitosamente: {stats['processed']}")
        print(f"   ❌ Fallidos: {stats['failed']}")
        print(f"   ⏰ Timeouts: {stats['timeout']}")
        print(f"   🔄 Reintentados: {stats['retried']}")
        print(f"   📈 Tasa de éxito: {stats['success_rate']:.1f}%")
        
        if stats['avg_processing_time'] > 0:
            print(f"\n⏱️  TIEMPOS DE PROCESAMIENTO:")
            print(f"   Promedio: {stats['avg_processing_time']:.2f}s")
            print(f"   Más rápido: {stats['fastest_time']:.2f}s")
            print(f"   Más lento: {stats['slowest_time']:.2f}s")
        
        print(f"\n🤖 ESTADÍSTICAS DEL PROCESADOR:")
        proc_stats = stats['processor_stats']
        print(f"   Total procesados: {proc_stats['total_processed']}")
        print(f"   Exitosos: {proc_stats['successful']}")
        print(f"   Fallidos: {proc_stats['failed']}")
        if proc_stats['avg_processing_time'] > 0:
            print(f"   Tiempo promedio: {proc_stats['avg_processing_time']:.2f}s")


def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Procesar documentos pendientes con procesador rápido')
    parser.add_argument('--limit', type=int, help='Límite de documentos a procesar')
    parser.add_argument('--batch-size', type=int, default=5, help='Tamaño del lote (default: 5)')
    parser.add_argument('--max-batches', type=int, help='Máximo número de lotes a procesar')
    parser.add_argument('--max-retries', type=int, default=2, help='Máximo reintentos por documento (default: 2)')
    
    args = parser.parse_args()
    
    processor = PendingDocumentProcessor(
        batch_size=args.batch_size,
        max_retries=args.max_retries
    )
    
    stats = processor.run(limit=args.limit, max_batches=args.max_batches)
    
    # Guardar estadísticas en archivo
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    stats_file = f'processing_stats_{timestamp}.json'
    
    import json
    with open(stats_file, 'w') as f:
        json.dump(stats, f, indent=2, default=str)
    
    logger.info(f"📁 Estadísticas guardadas en: {stats_file}")


if __name__ == "__main__":
    main()
