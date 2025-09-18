#!/usr/bin/env python3
"""
Analizador simple del sistema OCR - Compatible con Windows
"""

import os
import json
from pathlib import Path

def analyze_system():
    """Analiza el estado actual del sistema"""
    
    print("ANALISIS DEL SISTEMA OCR")
    print("=" * 50)
    
    results = {
        "models": check_models(),
        "datasets": check_datasets(),
        "services": check_services(),
        "config": check_configuration(),
        "docker": check_docker()
    }
    
    # Generar reporte
    generate_report(results)
    
    return results

def check_models():
    """Verifica los modelos disponibles"""
    
    print("\n1. VERIFICANDO MODELOS")
    print("-" * 30)
    
    models_path = Path("models/yolo_models")
    models_found = []
    
    if models_path.exists():
        for model_file in models_path.rglob("*.pt"):
            size_mb = model_file.stat().st_size / (1024 * 1024)
            models_found.append({
                "name": model_file.name,
                "path": str(model_file),
                "size_mb": round(size_mb, 2)
            })
            print(f"  [OK] {model_file.name} ({size_mb:.1f} MB)")
    
    if not models_found:
        print("  [WARNING] No se encontraron modelos YOLO")
    
    return models_found

def check_datasets():
    """Verifica los datasets disponibles"""
    
    print("\n2. VERIFICANDO DATASETS")
    print("-" * 30)
    
    datasets_path = Path("datasets")
    datasets_found = []
    
    if datasets_path.exists():
        for dataset_dir in datasets_path.iterdir():
            if dataset_dir.is_dir():
                # Contar imágenes
                images_count = len(list(dataset_dir.rglob("*.jpg"))) + len(list(dataset_dir.rglob("*.png")))
                labels_count = len(list(dataset_dir.rglob("*.txt")))
                
                datasets_found.append({
                    "name": dataset_dir.name,
                    "images": images_count,
                    "labels": labels_count
                })
                print(f"  [OK] {dataset_dir.name}: {images_count} imágenes, {labels_count} etiquetas")
    
    if not datasets_found:
        print("  [WARNING] No se encontraron datasets")
    
    return datasets_found

def check_services():
    """Verifica los servicios principales"""
    
    print("\n3. VERIFICANDO SERVICIOS")
    print("-" * 30)
    
    services = {
        "auth_service.py": "Servicio de autenticación",
        "document_service.py": "Servicio de documentos", 
        "ocr_service.py": "Servicio de OCR",
        "task_queue_service.py": "Servicio de colas"
    }
    
    services_status = []
    
    for service_file, description in services.items():
        service_path = Path("services") / service_file
        if service_path.exists():
            size_kb = service_path.stat().st_size / 1024
            services_status.append({
                "name": service_file,
                "description": description,
                "status": "OK",
                "size_kb": round(size_kb, 1)
            })
            print(f"  [OK] {description}")
        else:
            services_status.append({
                "name": service_file,
                "description": description,
                "status": "MISSING",
                "size_kb": 0
            })
            print(f"  [ERROR] {description} - NO ENCONTRADO")
    
    return services_status

def check_configuration():
    """Verifica la configuración"""
    
    print("\n4. VERIFICANDO CONFIGURACION")
    print("-" * 30)
    
    config_files = {
        ".env.local": "Configuración local",
        ".env.docker": "Configuración Docker",
        "config.py": "Configuración principal"
    }
    
    config_status = []
    
    for config_file, description in config_files.items():
        config_path = Path(config_file)
        if config_path.exists():
            config_status.append({
                "name": config_file,
                "description": description,
                "status": "OK"
            })
            print(f"  [OK] {description}")
        else:
            config_status.append({
                "name": config_file,
                "description": description,
                "status": "MISSING"
            })
            print(f"  [WARNING] {description} - NO ENCONTRADO")
    
    return config_status

def check_docker():
    """Verifica la configuración de Docker"""
    
    print("\n5. VERIFICANDO DOCKER")
    print("-" * 30)
    
    docker_files = {
        "docker-compose.yml": "Orquestación de servicios",
        "Dockerfile": "Imagen de la aplicación",
        ".dockerignore": "Exclusiones de Docker"
    }
    
    docker_status = []
    
    for docker_file, description in docker_files.items():
        docker_path = Path(docker_file)
        if docker_path.exists():
            docker_status.append({
                "name": docker_file,
                "description": description,
                "status": "OK"
            })
            print(f"  [OK] {description}")
        else:
            docker_status.append({
                "name": docker_file,
                "description": description,
                "status": "MISSING"
            })
            print(f"  [WARNING] {description} - NO ENCONTRADO")
    
    return docker_status

def generate_report(results):
    """Genera reporte del análisis"""
    
    print("\n" + "=" * 50)
    print("RESUMEN DEL ANALISIS")
    print("=" * 50)
    
    # Contar elementos
    total_models = len(results["models"])
    total_datasets = len(results["datasets"])
    
    services_ok = sum(1 for s in results["services"] if s["status"] == "OK")
    total_services = len(results["services"])
    
    config_ok = sum(1 for c in results["config"] if c["status"] == "OK")
    total_config = len(results["config"])
    
    docker_ok = sum(1 for d in results["docker"] if d["status"] == "OK")
    total_docker = len(results["docker"])
    
    print(f"Modelos YOLO encontrados: {total_models}")
    print(f"Datasets disponibles: {total_datasets}")
    print(f"Servicios funcionando: {services_ok}/{total_services}")
    print(f"Archivos de configuración: {config_ok}/{total_config}")
    print(f"Archivos Docker: {docker_ok}/{total_docker}")
    
    # Calcular progreso general
    total_items = total_services + total_config + total_docker
    ok_items = services_ok + config_ok + docker_ok
    progress = (ok_items / total_items * 100) if total_items > 0 else 0
    
    print(f"\nPROGRESO GENERAL: {progress:.1f}%")
    
    # Guardar reporte
    report_data = {
        "timestamp": str(Path.cwd()),
        "progress_percentage": round(progress, 1),
        "summary": {
            "models": total_models,
            "datasets": total_datasets,
            "services_ok": f"{services_ok}/{total_services}",
            "config_ok": f"{config_ok}/{total_config}",
            "docker_ok": f"{docker_ok}/{total_docker}"
        },
        "details": results
    }
    
    with open("system_analysis_report.json", "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)
    
    print(f"\nReporte guardado: system_analysis_report.json")
    
    # Recomendaciones
    print(f"\nRECOMENDACIONES:")
    if total_models == 0:
        print("- Entrenar o descargar modelos YOLO específicos")
    if total_datasets == 0:
        print("- Crear datasets de entrenamiento")
    if services_ok < total_services:
        print("- Revisar servicios faltantes")
    if config_ok < total_config:
        print("- Completar archivos de configuración")

if __name__ == "__main__":
    analyze_system()
