#!/usr/bin/env python3
"""
Script para preparar múltiples facturas para entrenamiento YOLO
- Organiza imágenes en carpetas
- Abre labelImg para anotación
- Prepara dataset con splits
- Entrena modelo
"""

import argparse
import os
import random
import shutil
import subprocess
import sys
from pathlib import Path


def create_classes_file(classes: list[str], output_path: Path) -> None:
    """Crea archivo de clases para labelImg"""
    content = "\n".join(classes)
    output_path.write_text(content, encoding='utf-8')
    print(f"Archivo de clases creado: {output_path}")


def organize_images(source_dir: Path, target_dir: Path, extensions: set = {'.jpg', '.jpeg', '.png', '.bmp'}) -> None:
    """Organiza imágenes de source_dir a target_dir"""
    target_dir.mkdir(parents=True, exist_ok=True)
    
    images = []
    for ext in extensions:
        images.extend(source_dir.glob(f"*{ext}"))
        images.extend(source_dir.glob(f"*{ext.upper()}"))
    
    print(f"Encontradas {len(images)} imágenes en {source_dir}")
    
    for img in images:
        dest = target_dir / img.name
        shutil.copy2(img, dest)
        print(f"Copiado: {img.name}")
    
    return len(images)


def open_labelimg(images_dir: Path, classes_file: Path, labels_dir: Path) -> None:
    """Abre labelImg con configuración correcta"""
    labels_dir.mkdir(parents=True, exist_ok=True)
    
    # Buscar labelImg en el entorno virtual
    venv_scripts = Path("yolo_training_env/Scripts")
    labelimg_exe = venv_scripts / "labelImg.exe"
    
    if not labelimg_exe.exists():
        print(f"❌ No se encontró labelImg en: {labelimg_exe}")
        print("Instala labelImg: pip install labelImg")
        return
    
    print(f"🖼️  Abriendo labelImg...")
    print(f"   - Imágenes: {images_dir}")
    print(f"   - Clases: {classes_file}")
    print(f"   - Labels: {labels_dir}")
    print("\n📝 Instrucciones:")
    print("1. En labelImg, ve a View > Auto Save Mode (activar)")
    print("2. Cambia formato a YOLO si te lo pide")
    print("3. Change Save Dir: selecciona la carpeta de labels")
    print("4. Anota cada imagen (tecla W para dibujar cajas)")
    print("5. Selecciona la clase correcta para cada caja")
    print("6. Guarda (Ctrl+S) y pasa a la siguiente imagen")
    print("\n⏳ Presiona Enter cuando termines de anotar...")
    input()
    
    # Comando para abrir labelImg
    cmd = [str(labelimg_exe), str(images_dir), str(classes_file), str(labels_dir)]
    try:
        subprocess.Popen(cmd)
    except Exception as e:
        print(f"Error abriendo labelImg: {e}")


def create_dataset_splits(images_dir: Path, labels_dir: Path, output_dir: Path, 
                         train_ratio: float = 0.8, val_ratio: float = 0.2) -> None:
    """Crea splits train/val/test del dataset"""
    
    # Obtener imágenes con sus labels correspondientes
    images = []
    for img_path in images_dir.glob("*"):
        if img_path.suffix.lower() in {'.jpg', '.jpeg', '.png', '.bmp'}:
            label_path = labels_dir / f"{img_path.stem}.txt"
            if label_path.exists():
                images.append((img_path, label_path))
            else:
                print(f"⚠️  Sin label: {img_path.name}")
    
    if not images:
        raise SystemExit("❌ No se encontraron imágenes con labels")
    
    print(f"📊 Dataset: {len(images)} imágenes con labels")
    
    # Mezclar y dividir
    random.shuffle(images)
    total = len(images)
    train_count = max(1, int(total * train_ratio))
    val_count = max(1, int(total * val_ratio))
    
    splits = {
        'train': images[:train_count],
        'val': images[train_count:train_count + val_count],
        'test': images[train_count + val_count:] if total > train_count + val_count else []
    }
    
    # Crear estructura y copiar archivos
    for split_name, split_images in splits.items():
        if not split_images:
            continue
            
        split_img_dir = output_dir / 'images' / split_name
        split_lbl_dir = output_dir / 'labels' / split_name
        
        split_img_dir.mkdir(parents=True, exist_ok=True)
        split_lbl_dir.mkdir(parents=True, exist_ok=True)
        
        for img_path, lbl_path in split_images:
            shutil.copy2(img_path, split_img_dir / img_path.name)
            shutil.copy2(lbl_path, split_lbl_dir / lbl_path.name)
        
        print(f"✅ {split_name}: {len(split_images)} imágenes")


def write_dataset_yaml(yaml_path: Path, dataset_root: Path, classes: list[str]) -> None:
    """Escribe dataset.yaml con rutas absolutas"""
    train = str((dataset_root / 'images' / 'train').resolve()).replace('\\', '/')
    val = str((dataset_root / 'images' / 'val').resolve()).replace('\\', '/')
    test = str((dataset_root / 'images' / 'test').resolve()).replace('\\', '/')
    
    lines = [
        f"train: {train}",
        f"val: {val}",
        f"test: {test}",
        "names:",
    ]
    for idx, name in enumerate(classes):
        lines.append(f"  {idx}: {name}")
    
    yaml_path.write_text("\n".join(lines), encoding='utf-8')
    print(f"📝 Dataset YAML escrito: {yaml_path}")


def train_model(venv_dir: Path, model_path: Path, yaml_path: Path, 
                epochs: int, imgsz: int, project_dir: Path, run_name: str) -> None:
    """Entrena el modelo YOLO"""
    yolo_exe = venv_dir / 'Scripts' / 'yolo.exe'
    if not yolo_exe.exists():
        raise SystemExit(f"❌ No se encontró YOLO CLI en: {yolo_exe}")
    
    cmd = [
        str(yolo_exe), 'detect', 'train',
        f"data={yaml_path}",
        f"model={model_path}",
        f"epochs={epochs}",
        f"imgsz={imgsz}",
        "batch=1",
        "workers=0",
        f"project={project_dir}",
        f"name={run_name}",
    ]
    
    print(f"🚀 Iniciando entrenamiento...")
    print(f"   - Épocas: {epochs}")
    print(f"   - Tamaño: {imgsz}x{imgsz}")
    print(f"   - Run: {run_name}")
    
    try:
        subprocess.run(cmd, check=True)
        print("✅ Entrenamiento completado!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error en entrenamiento: {e}")
        raise


def main():
    parser = argparse.ArgumentParser(description='Prepara y entrena modelo YOLO con múltiples facturas')
    parser.add_argument('--source_dir', type=str, required=True, 
                       help='Carpeta con imágenes de facturas (sin anotar)')
    parser.add_argument('--output_dir', type=str, default='datasets/invoices_multi',
                       help='Carpeta de salida del dataset')
    parser.add_argument('--epochs', type=int, default=20,
                       help='Número de épocas de entrenamiento')
    parser.add_argument('--imgsz', type=int, default=640,
                       help='Tamaño de imagen')
    parser.add_argument('--run_name', type=str, default='invoices_multi',
                       help='Nombre del experimento')
    parser.add_argument('--classes', type=str, nargs='*', 
                       default=['invoice_number', 'date', 'vendor', 'cuit', 'subtotal', 'tax', 'total', 'items_table'],
                       help='Lista de clases')
    parser.add_argument('--skip_annotation', action='store_true',
                       help='Saltar anotación (asume que ya están anotadas)')
    
    args = parser.parse_args()
    
    # Rutas
    source_dir = Path(args.source_dir).resolve()
    output_dir = Path(args.output_dir).resolve()
    temp_dir = output_dir / 'temp'
    images_dir = temp_dir / 'images'
    labels_dir = temp_dir / 'labels'
    classes_file = temp_dir / 'classes.txt'
    yaml_path = Path('yolo/dataset.yaml').resolve()
    venv_dir = Path('yolo_training_env').resolve()
    model_path = Path('models/yolo_models/yolov8n.pt').resolve()
    project_dir = Path('models/yolo_models').resolve()
    
    print("🎯 Preparando dataset de múltiples facturas...")
    print(f"   - Origen: {source_dir}")
    print(f"   - Destino: {output_dir}")
    
    # 1. Crear archivo de clases
    create_classes_file(args.classes, classes_file)
    
    # 2. Organizar imágenes
    if not source_dir.exists():
        raise SystemExit(f"❌ No existe el directorio: {source_dir}")
    
    num_images = organize_images(source_dir, images_dir)
    if num_images == 0:
        raise SystemExit("❌ No se encontraron imágenes en el directorio fuente")
    
    # 3. Anotación (opcional)
    if not args.skip_annotation:
        open_labelimg(images_dir, classes_file, labels_dir)
    
    # 4. Crear splits
    create_dataset_splits(images_dir, labels_dir, output_dir)
    
    # 5. Escribir dataset.yaml
    write_dataset_yaml(yaml_path, output_dir, args.classes)
    
    # 6. Entrenar
    train_model(venv_dir, model_path, yaml_path, args.epochs, args.imgsz, project_dir, args.run_name)
    
    print(f"\n🎉 ¡Proceso completado!")
    print(f"   - Modelo entrenado: {project_dir / args.run_name}")
    print(f"   - Pesos: {project_dir / args.run_name / 'weights' / 'best.pt'}")
    print(f"   - Resultados: {project_dir / args.run_name / 'results.png'}")


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
