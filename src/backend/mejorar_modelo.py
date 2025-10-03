#!/usr/bin/env python3
"""
Script principal para mejorar el modelo YOLO de facturas argentinas
Ejecuta el pipeline completo de generación de datos y entrenamiento
"""

import os
import sys
from pathlib import Path

def main():
    """Función principal"""
    print("🚀 MEJORANDO MODELO YOLO - FACTURAS ARGENTINAS")
    print("=" * 50)
    
    # Verificar que estamos en el directorio correcto
    if not Path("scripts/complete_training_pipeline.py").exists():
        print("❌ Error: Ejecutar desde el directorio backend/")
        print("   Comando correcto: python mejorar_modelo.py")
        return 1
    
    # Ejecutar pipeline completo
    print("📋 Iniciando pipeline completo...")
    print("   - Generación de datasets sintéticos")
    print("   - Entrenamiento de modelos optimizados")
    print("   - Evaluación y reporte")
    print()
    
    try:
        # Importar y ejecutar pipeline
        sys.path.append(str(Path.cwd()))
        from scripts.complete_training_pipeline import CompleteTrainingPipeline
        
        pipeline = CompleteTrainingPipeline()
        success = pipeline.run_complete_pipeline()
        
        if success:
            print("\n🎉 ¡Modelo mejorado exitosamente!")
            print("\n📁 Archivos generados:")
            print("   - datasets/invoices_argentina_synthetic/ (500 imágenes)")
            print("   - datasets/invoices_argentina_advanced/ (1000 imágenes)")
            print("   - models/yolo_models/argentina_invoices_*/ (modelos entrenados)")
            print("   - MODELO_MEJORADO_REPORTE.md (reporte completo)")
            print("   - training_pipeline.log (logs detallados)")
            
            print("\n🎯 Próximos pasos:")
            print("1. Revisar el reporte: MODELO_MEJORADO_REPORTE.md")
            print("2. Probar modelos con facturas reales")
            print("3. Integrar el mejor modelo en el sistema OCR")
            
            return 0
        else:
            print("\n⚠️  Pipeline completado con advertencias")
            print("   Revisa training_pipeline.log para detalles")
            return 1
            
    except Exception as e:
        print(f"\n❌ Error ejecutando pipeline: {e}")
        print("   Revisa que todas las dependencias estén instaladas")
        return 1

if __name__ == "__main__":
    sys.exit(main())
