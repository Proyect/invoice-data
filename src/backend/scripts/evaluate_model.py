#!/usr/bin/env python3
"""
Script para evaluar modelo YOLO entrenado
- Hace predicciones en lote
- Calcula métricas
- Genera reportes
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List


def find_best_model(project_dir: Path, run_name: str) -> Path:
    """Encuentra el mejor modelo entrenado"""
    run_dir = project_dir / run_name
    if not run_dir.exists():
        raise SystemExit(f"❌ No existe el run: {run_dir}")
    
    # Buscar best.pt primero, luego last.pt
    for weight_name in ['best.pt', 'last.pt']:
        weight_path = run_dir / 'weights' / weight_name
        if weight_path.exists():
            return weight_path
    
    raise SystemExit(f"❌ No se encontraron pesos en: {run_dir / 'weights'}")


def run_validation(model_path: Path, yaml_path: Path, output_dir: Path) -> Dict:
    """Ejecuta validación del modelo"""
    venv_dir = Path('yolo_training_env')
    yolo_exe = venv_dir / 'Scripts' / 'yolo.exe'
    
    if not yolo_exe.exists():
        raise SystemExit(f"❌ No se encontró YOLO CLI en: {yolo_exe}")
    
    cmd = [
        str(yolo_exe), 'detect', 'val',
        f"model={model_path}",
        f"data={yaml_path}",
        "batch=1",
        "imgsz=640",
        "workers=0",
        f"project={output_dir}",
        "name=validation"
    ]
    
    print(f"🔍 Ejecutando validación...")
    print(f"   - Modelo: {model_path}")
    print(f"   - Dataset: {yaml_path}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("✅ Validación completada")
        return {"status": "success", "output": result.stdout}
    except subprocess.CalledProcessError as e:
        print(f"❌ Error en validación: {e}")
        return {"status": "error", "output": e.stdout, "error": e.stderr}


def run_batch_prediction(model_path: Path, source_dir: Path, output_dir: Path, 
                        conf_threshold: float = 0.25) -> Dict:
    """Ejecuta predicciones en lote"""
    venv_dir = Path('yolo_training_env')
    yolo_exe = venv_dir / 'Scripts' / 'yolo.exe'
    
    if not source_dir.exists():
        raise SystemExit(f"❌ No existe el directorio fuente: {source_dir}")
    
    cmd = [
        str(yolo_exe), 'detect', 'predict',
        f"model={model_path}",
        f"source={source_dir}",
        f"conf={conf_threshold}",
        "imgsz=640",
        "save=True",
        "save_txt=True",
        f"project={output_dir}",
        "name=batch_predictions"
    ]
    
    print(f"🔮 Ejecutando predicciones en lote...")
    print(f"   - Modelo: {model_path}")
    print(f"   - Fuente: {source_dir}")
    print(f"   - Confianza: {conf_threshold}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("✅ Predicciones completadas")
        return {"status": "success", "output": result.stdout}
    except subprocess.CalledProcessError as e:
        print(f"❌ Error en predicciones: {e}")
        return {"status": "error", "output": e.stdout, "error": e.stderr}


def analyze_results(results_dir: Path) -> Dict:
    """Analiza los resultados de entrenamiento"""
    results = {}
    
    # Buscar archivos de resultados
    results_csv = results_dir / 'results.csv'
    if results_csv.exists():
        print(f"📊 Analizando: {results_csv}")
        # Aquí podrías parsear el CSV para extraer métricas finales
        results['csv_exists'] = True
    
    # Buscar imágenes de resultados
    results_png = results_dir / 'results.png'
    if results_png.exists():
        results['results_plot'] = str(results_png)
    
    confusion_matrix = results_dir / 'confusion_matrix.png'
    if confusion_matrix.exists():
        results['confusion_matrix'] = str(confusion_matrix)
    
    return results


def generate_report(model_path: Path, validation_results: Dict, 
                   prediction_results: Dict, analysis_results: Dict, 
                   output_file: Path) -> None:
    """Genera reporte de evaluación"""
    report = {
        "model": {
            "path": str(model_path),
            "name": model_path.parent.parent.name,
            "weight_type": model_path.name
        },
        "validation": validation_results,
        "predictions": prediction_results,
        "analysis": analysis_results,
        "timestamp": str(Path().cwd())
    }
    
    output_file.write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(f"📄 Reporte generado: {output_file}")


def main():
    parser = argparse.ArgumentParser(description='Evalúa modelo YOLO entrenado')
    parser.add_argument('--run_name', type=str, required=True,
                       help='Nombre del experimento a evaluar')
    parser.add_argument('--test_images', type=str,
                       help='Carpeta con imágenes de prueba (opcional)')
    parser.add_argument('--yaml_path', type=str, default='yolo/dataset.yaml',
                       help='Ruta al dataset.yaml')
    parser.add_argument('--output_dir', type=str, default='evaluation_results',
                       help='Carpeta de salida para resultados')
    parser.add_argument('--conf_threshold', type=float, default=0.25,
                       help='Umbral de confianza para predicciones')
    parser.add_argument('--skip_validation', action='store_true',
                       help='Saltar validación del dataset')
    
    args = parser.parse_args()
    
    # Rutas
    project_dir = Path('models/yolo_models')
    yaml_path = Path(args.yaml_path).resolve()
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("🎯 Evaluando modelo YOLO...")
    print(f"   - Run: {args.run_name}")
    print(f"   - Salida: {output_dir}")
    
    # 1. Encontrar modelo
    model_path = find_best_model(project_dir, args.run_name)
    print(f"✅ Modelo encontrado: {model_path}")
    
    # 2. Validación (opcional)
    validation_results = {"skipped": True}
    if not args.skip_validation and yaml_path.exists():
        validation_results = run_validation(model_path, yaml_path, output_dir)
    
    # 3. Predicciones en lote (opcional)
    prediction_results = {"skipped": True}
    if args.test_images:
        test_dir = Path(args.test_images).resolve()
        prediction_results = run_batch_prediction(
            model_path, test_dir, output_dir, args.conf_threshold
        )
    
    # 4. Análisis de resultados
    run_dir = project_dir / args.run_name
    analysis_results = analyze_results(run_dir)
    
    # 5. Generar reporte
    report_file = output_dir / f"evaluation_report_{args.run_name}.json"
    generate_report(model_path, validation_results, prediction_results, 
                   analysis_results, report_file)
    
    print(f"\n🎉 Evaluación completada!")
    print(f"   - Reporte: {report_file}")
    if analysis_results.get('results_plot'):
        print(f"   - Gráficos: {analysis_results['results_plot']}")
    if analysis_results.get('confusion_matrix'):
        print(f"   - Matriz confusión: {analysis_results['confusion_matrix']}")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n⏹️  Proceso cancelado por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
