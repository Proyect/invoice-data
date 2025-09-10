#!/usr/bin/env python3
"""
Script para probar el modelo de facturas argentinas
- Hace predicciones con diferentes umbrales de confianza
- Genera reportes de evaluación
- Compara resultados entre modelos
"""

import argparse
import subprocess
import sys
from pathlib import Path


def test_model_predictions(model_path: Path, test_images: list[Path], 
                          confidence_thresholds: list[float] = [0.1, 0.25, 0.5]) -> dict:
    """Prueba el modelo con diferentes umbrales de confianza"""
    results = {}
    
    for conf in confidence_thresholds:
        print(f"🔍 Probando con confianza: {conf}")
        
        for img_path in test_images:
            if not img_path.exists():
                print(f"⚠️  Imagen no encontrada: {img_path}")
                continue
            
            # Crear nombre único para la predicción
            pred_name = f"pred_conf_{conf}_{img_path.stem}"
            
            cmd = [
                "yolo_training_env/Scripts/yolo.exe", "detect", "predict",
                f"model={model_path}",
                f"source={img_path}",
                f"conf={conf}",
                "imgsz=640",
                "save=True",
                "save_txt=True",
                "project=models/yolo_models",
                f"name={pred_name}"
            ]
            
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                results[f"{img_path.stem}_conf_{conf}"] = {
                    "status": "success",
                    "output": result.stdout,
                    "confidence": conf
                }
                print(f"✅ Predicción exitosa: {pred_name}")
            except subprocess.CalledProcessError as e:
                results[f"{img_path.stem}_conf_{conf}"] = {
                    "status": "error",
                    "error": e.stderr,
                    "confidence": conf
                }
                print(f"❌ Error en predicción: {e}")
    
    return results


def compare_models(models: list[Path], test_image: Path) -> dict:
    """Compara diferentes modelos en la misma imagen"""
    comparison = {}
    
    for model_path in models:
        if not model_path.exists():
            print(f"⚠️  Modelo no encontrado: {model_path}")
            continue
        
        model_name = model_path.parent.parent.name
        print(f"🤖 Probando modelo: {model_name}")
        
        pred_name = f"compare_{model_name}_{test_image.stem}"
        
        cmd = [
            "yolo_training_env/Scripts/yolo.exe", "detect", "predict",
            f"model={model_path}",
            f"source={test_image}",
            "conf=0.1",
            "imgsz=640",
            "save=True",
            "project=models/yolo_models",
            f"name={pred_name}"
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            comparison[model_name] = {
                "status": "success",
                "output": result.stdout
            }
            print(f"✅ Modelo {model_name}: Predicción exitosa")
        except subprocess.CalledProcessError as e:
            comparison[model_name] = {
                "status": "error",
                "error": e.stderr
            }
            print(f"❌ Modelo {model_name}: Error")
    
    return comparison


def generate_test_report(results: dict, output_file: Path) -> None:
    """Genera reporte de pruebas"""
    report = f"""# Reporte de Pruebas - Modelo Facturas Argentinas

## Resumen
- Total de pruebas: {len(results)}
- Pruebas exitosas: {sum(1 for r in results.values() if r['status'] == 'success')}
- Pruebas fallidas: {sum(1 for r in results.values() if r['status'] == 'error')}

## Detalles por Prueba

"""
    
    for test_name, result in results.items():
        report += f"### {test_name}\n"
        report += f"- Estado: {result['status']}\n"
        if 'confidence' in result:
            report += f"- Confianza: {result['confidence']}\n"
        if result['status'] == 'success':
            report += f"- Salida: {result['output'][:200]}...\n"
        else:
            report += f"- Error: {result.get('error', 'N/A')}\n"
        report += "\n"
    
    output_file.write_text(report, encoding='utf-8')
    print(f"📄 Reporte generado: {output_file}")


def main():
    parser = argparse.ArgumentParser(description='Prueba modelo de facturas argentinas')
    parser.add_argument('--model', type=str, 
                       default='models/yolo_models/argentina_invoices_v1/weights/best.pt',
                       help='Ruta al modelo a probar')
    parser.add_argument('--test_images', type=str, nargs='+',
                       default=['models/yolo_models/test_invoice.jpg'],
                       help='Imágenes de prueba')
    parser.add_argument('--confidence_thresholds', type=float, nargs='+',
                       default=[0.1, 0.25, 0.5],
                       help='Umbrales de confianza a probar')
    parser.add_argument('--compare_models', action='store_true',
                       help='Comparar con otros modelos disponibles')
    parser.add_argument('--output_report', type=str,
                       default='test_report_argentina.md',
                       help='Archivo de reporte de salida')
    
    args = parser.parse_args()
    
    model_path = Path(args.model)
    test_images = [Path(img) for img in args.test_images]
    output_report = Path(args.output_report)
    
    print("🇦🇷 Probando modelo de facturas argentinas...")
    print(f"   - Modelo: {model_path}")
    print(f"   - Imágenes de prueba: {len(test_images)}")
    print(f"   - Umbrales de confianza: {args.confidence_thresholds}")
    
    # Verificar que el modelo existe
    if not model_path.exists():
        print(f"❌ Modelo no encontrado: {model_path}")
        print("Modelos disponibles:")
        models_dir = Path("models/yolo_models")
        for model_dir in models_dir.glob("*/weights/best.pt"):
            print(f"  - {model_dir}")
        sys.exit(1)
    
    # Probar con diferentes umbrales de confianza
    results = test_model_predictions(model_path, test_images, args.confidence_thresholds)
    
    # Comparar con otros modelos si se solicita
    if args.compare_models:
        print("\n🔄 Comparando con otros modelos...")
        other_models = list(Path("models/yolo_models").glob("*/weights/best.pt"))
        other_models = [m for m in other_models if m != model_path]
        
        if other_models and test_images:
            comparison = compare_models(other_models, test_images[0])
            results.update(comparison)
    
    # Generar reporte
    generate_test_report(results, output_report)
    
    print(f"\n🎉 Pruebas completadas!")
    print(f"   - Reporte: {output_report}")
    print(f"   - Predicciones guardadas en: models/yolo_models/")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n⏹️  Pruebas canceladas por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
