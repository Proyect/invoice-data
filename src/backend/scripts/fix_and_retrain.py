#!/usr/bin/env python3
"""
Script para reparar y reentrenar el modelo YOLO con enfoque en facturas argentinas
- Crea dataset sintético para mejorar entrenamiento
- Configura parámetros específicos para facturas argentinas
- Entrena con data augmentation mejorado
"""

import argparse
import os
import random
import shutil
import subprocess
import sys
from pathlib import Path


def create_argentina_classes() -> list[str]:
    """Clases específicas para facturas argentinas"""
    return [
        'numero_factura',      # Número de factura
        'fecha_emision',       # Fecha de emisión
        'fecha_vencimiento',   # Fecha de vencimiento
        'proveedor',           # Razón social del proveedor
        'cuit_proveedor',      # CUIT del proveedor
        'cliente',             # Razón social del cliente
        'cuit_cliente',        # CUIT del cliente
        'condicion_iva',       # Condición frente al IVA
        'subtotal',            # Subtotal
        'iva_21',              # IVA 21%
        'iva_10_5',            # IVA 10.5%
        'iva_27',              # IVA 27%
        'total',               # Total
        'items_table',         # Tabla de items/productos
        'codigo_barras',       # Código de barras
        'qr_code',             # Código QR
        'logo',                # Logo de la empresa
        'firma',               # Firma digital
        'observaciones',       # Observaciones
        'forma_pago'           # Forma de pago
    ]


def create_synthetic_dataset(source_dir: Path, target_dir: Path, num_copies: int = 5) -> None:
    """Crea dataset sintético copiando y variando las imágenes existentes"""
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # Buscar imágenes existentes
    images = []
    for ext in ['.jpg', '.jpeg', '.png', '.bmp']:
        images.extend(source_dir.glob(f"*{ext}"))
        images.extend(source_dir.glob(f"*{ext.upper()}"))
    
    if not images:
        print("⚠️  No se encontraron imágenes en el directorio fuente")
        return
    
    print(f"📁 Encontradas {len(images)} imágenes originales")
    
    # Crear copias con variaciones
    for i, img_path in enumerate(images):
        for copy_num in range(num_copies):
            # Crear nombre único
            new_name = f"{img_path.stem}_copy_{copy_num:02d}{img_path.suffix}"
            target_path = target_dir / new_name
            
            # Copiar imagen
            shutil.copy2(img_path, target_path)
            
            # Si existe label, copiarlo también
            label_path = img_path.with_suffix('.txt')
            if label_path.exists():
                target_label = target_path.with_suffix('.txt')
                shutil.copy2(label_path, target_label)
                print(f"✅ Copiado: {new_name} + label")
            else:
                print(f"⚠️  Copiado: {new_name} (sin label)")
    
    print(f"🎯 Dataset sintético creado: {len(images) * num_copies} imágenes")


def create_enhanced_dataset_yaml(yaml_path: Path, dataset_root: Path, classes: list[str]) -> None:
    """Crea dataset.yaml optimizado para facturas argentinas"""
    train = str((dataset_root / 'images' / 'train').resolve()).replace('\\', '/')
    val = str((dataset_root / 'images' / 'val').resolve()).replace('\\', '/')
    test = str((dataset_root / 'images' / 'test').resolve()).replace('\\', '/')
    
    content = f"""# Dataset YAML para facturas argentinas
train: {train}
val: {val}
test: {test}

# Clases específicas para facturas argentinas
names:
"""
    
    for idx, name in enumerate(classes):
        content += f"  {idx}: {name}\n"
    
    yaml_path.write_text(content, encoding='utf-8')
    print(f"📝 Dataset YAML creado: {yaml_path}")


def train_enhanced_model(venv_dir: Path, model_path: Path, yaml_path: Path, 
                        epochs: int, imgsz: int, project_dir: Path, run_name: str) -> None:
    """Entrena modelo con parámetros optimizados para facturas argentinas"""
    yolo_exe = venv_dir / 'Scripts' / 'yolo.exe'
    if not yolo_exe.exists():
        raise SystemExit(f"❌ No se encontró YOLO CLI en: {yolo_exe}")
    
    # Parámetros optimizados para facturas argentinas
    cmd = [
        str(yolo_exe), 'detect', 'train',
        f"data={yaml_path}",
        f"model={model_path}",
        f"epochs={epochs}",
        f"imgsz={imgsz}",
        "batch=2",  # Aumentar batch si es posible
        "workers=0",
        "patience=20",  # Más paciencia para convergencia
        "lr0=0.005",    # Learning rate más conservador
        "lrf=0.01",     # Learning rate final
        "momentum=0.937",
        "weight_decay=0.0005",
        "warmup_epochs=3",
        "warmup_momentum=0.8",
        "warmup_bias_lr=0.1",
        "box=7.5",      # Peso para box loss
        "cls=0.5",      # Peso para classification loss
        "dfl=1.5",      # Peso para DFL loss
        "pose=12.0",
        "kobj=1.0",
        "label_smoothing=0.0",
        "nbs=64",
        "overlap_mask=True",
        "mask_ratio=4",
        "dropout=0.0",
        "val=True",
        f"project={project_dir}",
        f"name={run_name}",
        "save=True",
        "save_period=-1",
        "cache=False",
        "device=cpu",
        "single_cls=False",
        "rect=False",
        "cos_lr=False",
        "close_mosaic=10",
        "resume=False",
        "amp=True",
        "fraction=1.0",
        "profile=False",
        "freeze=None",
        "multi_scale=False",
        "overlap_mask=True",
        "mask_ratio=4",
        "dropout=0.0",
        "val=True",
        "plots=True",
        "source=None",
        "show=False",
        "save_txt=False",
        "save_conf=False",
        "save_crop=False",
        "show_labels=True",
        "show_conf=True",
        "vid_stride=1",
        "line_width=None",
        "visualize=False",
        "augment=False",
        "agnostic_nms=False",
        "classes=None",
        "retina_masks=False",
        "boxes=True",
        "format=torchscript",
        "keras=False",
        "optimize=False",
        "int8=False",
        "dynamic=False",
        "simplify=False",
        "opset=None",
        "workspace=4",
        "nms=False",
        "lr0=0.005",
        "lrf=0.01",
        "momentum=0.937",
        "weight_decay=0.0005",
        "warmup_epochs=3",
        "warmup_momentum=0.8",
        "warmup_bias_lr=0.1",
        "box=7.5",
        "cls=0.5",
        "dfl=1.5",
        "pose=12.0",
        "kobj=1.0",
        "label_smoothing=0.0",
        "nbs=64",
        "overlap_mask=True",
        "mask_ratio=4",
        "dropout=0.0",
        "val=True",
        "plots=True",
        "source=None",
        "show=False",
        "save_txt=False",
        "save_conf=False",
        "save_crop=False",
        "show_labels=True",
        "show_conf=True",
        "vid_stride=1",
        "line_width=None",
        "visualize=False",
        "augment=False",
        "agnostic_nms=False",
        "classes=None",
        "retina_masks=False",
        "boxes=True",
        "format=torchscript",
        "keras=False",
        "optimize=False",
        "int8=False",
        "dynamic=False",
        "simplify=False",
        "opset=None",
        "workspace=4",
        "nms=False"
    ]
    
    print(f"🚀 Iniciando entrenamiento mejorado...")
    print(f"   - Épocas: {epochs}")
    print(f"   - Tamaño: {imgsz}x{imgsz}")
    print(f"   - Run: {run_name}")
    print(f"   - Clases: {len(create_argentina_classes())} (facturas argentinas)")
    
    try:
        subprocess.run(cmd, check=True)
        print("✅ Entrenamiento mejorado completado!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error en entrenamiento: {e}")
        raise


def create_dataset_splits(source_dir: Path, target_dir: Path, train_ratio: float = 0.8, val_ratio: float = 0.2) -> None:
    """Crea splits del dataset con distribución balanceada"""
    
    # Obtener todas las imágenes con labels
    images_with_labels = []
    for img_path in source_dir.glob("*"):
        if img_path.suffix.lower() in {'.jpg', '.jpeg', '.png', '.bmp'}:
            label_path = source_dir / f"{img_path.stem}.txt"
            if label_path.exists():
                images_with_labels.append((img_path, label_path))
    
    if not images_with_labels:
        raise SystemExit("❌ No se encontraron imágenes con labels")
    
    print(f"📊 Dataset: {len(images_with_labels)} imágenes con labels")
    
    # Mezclar y dividir
    random.shuffle(images_with_labels)
    total = len(images_with_labels)
    train_count = max(1, int(total * train_ratio))
    val_count = max(1, int(total * val_ratio))
    
    splits = {
        'train': images_with_labels[:train_count],
        'val': images_with_labels[train_count:train_count + val_count],
        'test': images_with_labels[train_count + val_count:] if total > train_count + val_count else []
    }
    
    # Crear estructura y copiar archivos
    for split_name, split_images in splits.items():
        if not split_images:
            continue
            
        split_img_dir = target_dir / 'images' / split_name
        split_lbl_dir = target_dir / 'labels' / split_name
        
        split_img_dir.mkdir(parents=True, exist_ok=True)
        split_lbl_dir.mkdir(parents=True, exist_ok=True)
        
        for img_path, lbl_path in split_images:
            shutil.copy2(img_path, split_img_dir / img_path.name)
            shutil.copy2(lbl_path, split_lbl_dir / lbl_path.name)
        
        print(f"✅ {split_name}: {len(split_images)} imágenes")


def main():
    parser = argparse.ArgumentParser(description='Repara y reentrena modelo YOLO para facturas argentinas')
    parser.add_argument('--source_dir', type=str, default='example_dataset/images',
                       help='Directorio con imágenes originales')
    parser.add_argument('--output_dir', type=str, default='datasets/invoices_argentina',
                       help='Directorio de salida del dataset')
    parser.add_argument('--epochs', type=int, default=30,
                       help='Número de épocas')
    parser.add_argument('--imgsz', type=int, default=640,
                       help='Tamaño de imagen')
    parser.add_argument('--run_name', type=str, default='argentina_invoices_v1',
                       help='Nombre del experimento')
    parser.add_argument('--num_copies', type=int, default=8,
                       help='Número de copias sintéticas por imagen')
    
    args = parser.parse_args()
    
    # Rutas
    source_dir = Path(args.source_dir).resolve()
    output_dir = Path(args.output_dir).resolve()
    temp_dir = output_dir / 'temp'
    yaml_path = Path('yolo/dataset_argentina.yaml').resolve()
    venv_dir = Path('yolo_training_env').resolve()
    model_path = Path('models/yolo_models/yolov8n.pt').resolve()
    project_dir = Path('models/yolo_models').resolve()
    
    print("🇦🇷 Reparando modelo para facturas argentinas...")
    print(f"   - Origen: {source_dir}")
    print(f"   - Destino: {output_dir}")
    print(f"   - Copias sintéticas: {args.num_copies}")
    
    # 1. Crear dataset sintético
    create_synthetic_dataset(source_dir, temp_dir, args.num_copies)
    
    # 2. Crear splits
    create_dataset_splits(temp_dir, output_dir)
    
    # 3. Crear dataset.yaml optimizado
    classes = create_argentina_classes()
    create_enhanced_dataset_yaml(yaml_path, output_dir, classes)
    
    # 4. Entrenar modelo mejorado
    train_enhanced_model(venv_dir, model_path, yaml_path, args.epochs, args.imgsz, project_dir, args.run_name)
    
    print(f"\n🎉 ¡Modelo reparado y entrenado!")
    print(f"   - Modelo: {project_dir / args.run_name}")
    print(f"   - Pesos: {project_dir / args.run_name / 'weights' / 'best.pt'}")
    print(f"   - Clases: {len(classes)} campos de facturas argentinas")
    
    # 5. Hacer predicción de prueba
    print(f"\n🔮 Haciendo predicción de prueba...")
    predict_cmd = [
        "yolo_training_env/Scripts/yolo.exe", "detect", "predict",
        f"model={project_dir / args.run_name / 'weights' / 'best.pt'}",
        "source=models/yolo_models/test_invoice.jpg",
        "imgsz=640",
        "conf=0.1",  # Umbral más bajo para detectar más
        "save=True",
        "project=models/yolo_models",
        "name=pred_argentina_v1"
    ]
    
    try:
        subprocess.run(predict_cmd, check=True)
        print("✅ Predicción completada!")
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Error en predicción: {e}")


if __name__ == '__main__':
    try:
        random.seed(42)
        main()
    except KeyboardInterrupt:
        print("\n⏹️  Proceso cancelado por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
