#!/usr/bin/env python3
"""
Script principal para entrenar detectores YOLO para documentos
Uso: python train_detector.py --type invoice --epochs 100
"""

import argparse
import os
import json
from datetime import datetime
import torch
from pathlib import Path
from ultralytics import YOLO
import yaml

def setup_directories():
    """Crea la estructura de directorios necesaria"""
    dirs = [
        'datasets/invoices/images/train',
        'datasets/invoices/images/val', 
        'datasets/invoices/images/test',
        'datasets/invoices/labels/train',
        'datasets/invoices/labels/val',
        'datasets/invoices/labels/test',
        'datasets/dni/images/train',
        'datasets/dni/images/val',
        'datasets/dni/images/test', 
        'datasets/dni/labels/train',
        'datasets/dni/labels/val',
        'datasets/dni/labels/test',
        'models/trained',
        'models/pretrained'
    ]
    
    for dir_path in dirs:
        os.makedirs(dir_path, exist_ok=True)
        print(f"✓ Directorio creado: {dir_path}")

def create_dataset_config(doc_type):
    """Crea archivo de configuración del dataset"""
    
    configs = {
        'invoice': {
            'path': './datasets/invoices',
            'train': 'images/train',
            'val': 'images/val', 
            'test': 'images/test',
            'nc': 8,
            'names': {
                0: 'invoice_number',
                1: 'date',
                2: 'vendor', 
                3: 'cuit',
                4: 'subtotal',
                5: 'tax',
                6: 'total',
                7: 'items_table'
            }
        },
        'dni': {
            'path': './datasets/dni',
            'train': 'images/train',
            'val': 'images/val',
            'test': 'images/test', 
            'nc': 5,
            'names': {
                0: 'document_number',
                1: 'full_name',
                2: 'birth_date',
                3: 'gender',
                4: 'expiry_date'
            }
        }
    }
    
    config = configs[doc_type]
    config_path = f'configs/{doc_type}_dataset.yaml'
    
    os.makedirs('configs', exist_ok=True)
    with open(config_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False)
    
    print(f"✓ Configuración creada: {config_path}")
    return config_path

def validate_dataset_structure(config_path: str) -> dict:
    """Valida estructura del dataset y cuenta imágenes/labels por split.
    Devuelve un dict con conteos y lista de faltantes.
    """
    report = {
        'splits': {},
        'missing_labels': [],
        'missing_images': []
    }

    with open(config_path, 'r') as f:
        cfg = yaml.safe_load(f)

    base = Path(cfg['path'])
    for split in ['train', 'val', 'test']:
        img_dir = base / cfg.get(split, f'images/{split}')
        lbl_dir = base / 'labels' / split

        imgs = list(img_dir.glob('*.jpg')) + list(img_dir.glob('*.jpeg')) + list(img_dir.glob('*.png'))
        lbls = list(lbl_dir.glob('*.txt'))

        report['splits'][split] = {
            'images': len(imgs),
            'labels': len(lbls),
            'image_dir': str(img_dir),
            'label_dir': str(lbl_dir)
        }

        img_stems = {p.stem for p in imgs}
        lbl_stems = {p.stem for p in lbls}

        # Falta label por imagen
        for stem in sorted(img_stems - lbl_stems):
            report['missing_labels'].append(f"{split}:{stem}")

        # Falta imagen por label
        for stem in sorted(lbl_stems - img_stems):
            report['missing_images'].append(f"{split}:{stem}")

    # Mensajes de diagnóstico
    print("\n🧪 Validación del dataset:")
    for split, data in report['splits'].items():
        print(f"  - {split}: {data['images']} imágenes, {data['labels']} labels")
    if report['missing_labels']:
        print(f"⚠️  Labels faltantes: {len(report['missing_labels'])} (ej.: {report['missing_labels'][:5]})")
    if report['missing_images']:
        print(f"⚠️  Imágenes faltantes: {len(report['missing_images'])} (ej.: {report['missing_images'][:5]})")

    return report

def download_pretrained_model(model_size='n'):
    """Descarga modelo preentrenado de YOLOv8"""
    model_name = f'yolov8{model_size}.pt'
    model_path = f'models/pretrained/{model_name}'
    
    if not os.path.exists(model_path):
        print(f"Descargando modelo preentrenado: {model_name}")
        _ = YOLO(model_name)  # Esto descarga automáticamente
        os.makedirs('models/pretrained', exist_ok=True)
        # El modelo se guarda automáticamente en el directorio actual
        if os.path.exists(model_name):
            os.rename(model_name, model_path)
    
    return model_path

def train_model(doc_type, epochs=100, batch_size=16, img_size=640, model_size='n', device: str = None, workers: int = 4, resume_weights: str = None):
    """Entrena el modelo YOLO"""
    
    print(f"\n🚀 Iniciando entrenamiento para {doc_type}")
    print("Configuración:")
    print(f"  - Epochs: {epochs}")
    print(f"  - Batch size: {batch_size}")
    print(f"  - Image size: {img_size}")
    print(f"  - Model size: {model_size}")
    
    # Verificar dispositivo
    auto_device = 'cuda' if torch.cuda.is_available() else 'cpu'
    device = device or auto_device
    print(f"  - Device: {device} (auto: {auto_device})")
    
    # Crear configuración del dataset
    config_path = create_dataset_config(doc_type)
    
    # Seleccionar pesos (resume o preentrenado)
    pretrained_path = None
    if resume_weights and os.path.exists(resume_weights):
        print(f"🔁 Reanudando desde pesos: {resume_weights}")
        pretrained_path = resume_weights
    else:
        pretrained_path = download_pretrained_model(model_size)
    
    # Verificar que existen imágenes de entrenamiento
    train_dir = f'datasets/{doc_type}/images/train'
    if not os.path.exists(train_dir) or len(os.listdir(train_dir)) == 0:
        print(f"❌ Error: No se encontraron imágenes en {train_dir}")
        print("Por favor, añade imágenes de entrenamiento antes de continuar.")
        return None
    
    # Cargar modelo
    model = YOLO(pretrained_path)
    
    # Configurar entrenamiento
    training_args = {
        'data': config_path,
        'epochs': epochs,
        'imgsz': img_size,
        'batch': batch_size,
        'device': device,
        'workers': workers,
        'project': 'models/trained',
        'name': f'{doc_type}_detector',
        'save_period': max(10, epochs // 10),
        'patience': max(20, epochs // 5),
        'verbose': True,
        'plots': True,
        
        # Optimizaciones específicas para documentos
        'optimizer': 'AdamW',
        'lr0': 0.01,
        'weight_decay': 0.0005,
        
        # Augmentaciones conservadoras para documentos
        'hsv_h': 0.015,
        'hsv_s': 0.7, 
        'hsv_v': 0.4,
        'degrees': 5,
        'translate': 0.1,
        'scale': 0.2,
        'shear': 2,
        'perspective': 0.0,
        'flipud': 0.0,
        'fliplr': 0.0,
        'mosaic': 1.0,
        'mixup': 0.1
    }
    
    print("\n📊 Iniciando entrenamiento...")
    
    try:
        # Validar dataset antes de entrenar
        ds_report = validate_dataset_structure(config_path)
        if ds_report['splits']['train']['images'] == 0:
            print("❌ No hay imágenes de entrenamiento. Agrega datos en images/train")
            return None

        results = model.train(**training_args)
        
        print("\n✅ Entrenamiento completado!")
        print(f"Modelo guardado en: models/trained/{doc_type}_detector/weights/best.pt")
        
        # Copiar modelo entrenado a la ubicación final
        best_model_path = f'models/trained/{doc_type}_detector/weights/best.pt'
        final_model_path = f'models/yolo_models/{doc_type}_yolov8.pt'
        
        os.makedirs('models/yolo_models', exist_ok=True)
        if os.path.exists(best_model_path):
            import shutil
            shutil.copy(best_model_path, final_model_path)
            print(f"✅ Modelo copiado a: {final_model_path}")
        
        # Guardar resumen de resultados
        summary = {
            'doc_type': doc_type,
            'epochs': epochs,
            'batch_size': batch_size,
            'img_size': img_size,
            'device': device,
            'workers': workers,
            'pretrained_or_resume': pretrained_path,
            'trained_best_path': best_model_path,
            'final_model_path': final_model_path,
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }
        try:
            if hasattr(results, 'results_dict') and isinstance(results.results_dict, dict):
                summary['metrics'] = results.results_dict
        except Exception:
            pass

        os.makedirs('models/trained', exist_ok=True)
        with open(f'models/trained/{doc_type}_detector/results_summary.json', 'w') as f:
            json.dump(summary, f, indent=2)

        return results
        
    except Exception as e:
        print(f"❌ Error durante el entrenamiento: {e}")
        return None

def validate_model(model_path, config_path):
    """Valida el modelo entrenado"""
    print(f"\n🔍 Validando modelo: {model_path}")
    
    if not os.path.exists(model_path):
        print(f"❌ Modelo no encontrado: {model_path}")
        return None
    
    model = YOLO(model_path)
    results = model.val(
        data=config_path,
        split='test',
        imgsz=640,
        conf=0.25,
        iou=0.5
    )
    
    print(f"📈 Resultados de validación:")
    print(f"  - mAP@0.5: {results.box.map50:.3f}")
    print(f"  - mAP@0.5:0.95: {results.box.map:.3f}")
    print(f"  - Precision: {results.box.mp:.3f}")
    print(f"  - Recall: {results.box.mr:.3f}")
    
    return results

def main():
    parser = argparse.ArgumentParser(description='Entrenar detector YOLO para documentos')
    parser.add_argument('--type', choices=['invoice', 'dni'], required=True,
                       help='Tipo de documento a entrenar')
    parser.add_argument('--epochs', type=int, default=100,
                       help='Número de epochs (default: 100)')
    parser.add_argument('--batch', type=int, default=16,
                       help='Tamaño del batch (default: 16)')
    parser.add_argument('--imgsz', type=int, default=640,
                       help='Tamaño de imagen (default: 640)')
    parser.add_argument('--model', choices=['n', 's', 'm', 'l', 'x'], default='n',
                       help='Tamaño del modelo YOLOv8 (default: n)')
    parser.add_argument('--device', choices=['cpu', 'cuda'], default=None,
                       help='Dispositivo de entrenamiento (default: auto)')
    parser.add_argument('--workers', type=int, default=4,
                       help='Número de workers para dataloader (default: 4)')
    parser.add_argument('--resume', type=str, default=None,
                       help='Ruta a pesos .pt para reanudar entrenamiento')
    parser.add_argument('--setup', action='store_true',
                       help='Solo crear estructura de directorios')
    parser.add_argument('--validate', type=str,
                       help='Validar modelo existente (ruta al modelo)')
    
    args = parser.parse_args()
    
    if args.setup:
        print("🔧 Configurando estructura de directorios...")
        setup_directories()
        create_dataset_config(args.type)
        print("✅ Configuración completada!")
        return
    
    if args.validate:
        config_path = create_dataset_config(args.type)
        validate_model(args.validate, config_path)
        return
    
    # Configurar directorios si no existen
    setup_directories()
    
    # Entrenar modelo
    results = train_model(
        doc_type=args.type,
        epochs=args.epochs,
        batch_size=args.batch,
        img_size=args.imgsz,
        model_size=args.model,
        device=args.device,
        workers=args.workers,
        resume_weights=args.resume
    )
    
    if results:
        # Validar modelo entrenado
        model_path = f'models/trained/{args.type}_detector/weights/best.pt'
        config_path = f'configs/{args.type}_dataset.yaml'
        validate_model(model_path, config_path)

if __name__ == "__main__":
    main()
