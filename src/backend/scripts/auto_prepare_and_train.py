import argparse
import os
import random
import shutil
import subprocess
import sys
from pathlib import Path


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def copy_with_matching_label(image_path: Path, dest_images: Path, dest_labels: Path) -> None:
    ensure_dir(dest_images)
    ensure_dir(dest_labels)
    shutil.copy2(image_path, dest_images / image_path.name)
    label_src = image_path.with_suffix('.txt')
    if label_src.exists():
        shutil.copy2(label_src, dest_labels / label_src.name)


def build_splits(source_images: Path, dataset_root: Path, train_ratio: float, val_ratio: float) -> None:
    images = sorted([p for p in source_images.glob('*') if p.suffix.lower() in {'.jpg', '.jpeg', '.png'}])
    if not images:
        raise SystemExit(f"No se encontraron imágenes en: {source_images}")

    random.shuffle(images)
    total = len(images)
    train_count = max(1, int(total * train_ratio))
    val_count = max(0, int(total * val_ratio))
    train_images = images[:train_count]
    val_images = images[train_count:train_count + val_count] or images[train_count:train_count + 1]

    splits = {
        'train': train_images,
        'val': val_images,
        'test': []
    }

    for split, items in splits.items():
        for img in items:
            copy_with_matching_label(
                img,
                dataset_root / 'images' / split,
                dataset_root / 'labels' / split,
            )


def write_dataset_yaml(yaml_path: Path, dataset_root: Path, class_names: list[str]) -> None:
    # Usar rutas absolutas para evitar resoluciones inesperadas
    train = str((dataset_root / 'images' / 'train').resolve()).replace('\\', '/')
    val = str((dataset_root / 'images' / 'val').resolve()).replace('\\', '/')
    test = str((dataset_root / 'images' / 'test').resolve()).replace('\\', '/')
    lines = [
        f"train: {train}",
        f"val: {val}",
        f"test: {test}",
        "names:",
    ]
    for idx, name in enumerate(class_names):
        lines.append(f"  {idx}: {name}")
    yaml_path.write_text("\n".join(lines), encoding='utf-8')


def run_yolo_train(venv_dir: Path, model_path: Path, yaml_path: Path, epochs: int, imgsz: int, project_dir: Path, run_name: str) -> None:
    yolo_exe = venv_dir / 'Scripts' / 'yolo.exe'
    if not yolo_exe.exists():
        raise SystemExit(f"No se encontró YOLO CLI en: {yolo_exe}")
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
    print('Ejecutando:', ' '.join(cmd))
    subprocess.run(cmd, check=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Prepara dataset y entrena YOLO automáticamente')
    parser.add_argument('--source_images', type=str, required=True, help='Carpeta con imágenes ya anotadas (labels .txt junto a cada imagen)')
    parser.add_argument('--dataset_root', type=str, default=str(Path('datasets/invoices').resolve()), help='Destino del dataset con splits')
    parser.add_argument('--yolo_yaml', type=str, default=str(Path('yolo/dataset.yaml').resolve()), help='Ruta al dataset.yaml a escribir/actualizar')
    parser.add_argument('--venv_dir', type=str, default=str(Path('yolo_training_env').resolve()), help='Directorio del entorno con YOLO CLI')
    parser.add_argument('--model', type=str, default=str(Path('models/yolo_models/yolov8n.pt').resolve()), help='Modelo base para fine-tuning')
    parser.add_argument('--epochs', type=int, default=10)
    parser.add_argument('--imgsz', type=int, default=640)
    parser.add_argument('--run_name', type=str, default='auto_invoices_run')
    parser.add_argument('--classes', type=str, nargs='*', default=[
        'invoice_number', 'date', 'vendor', 'cuit', 'subtotal', 'tax', 'total', 'items_table'
    ], help='Lista de clases en orden')
    parser.add_argument('--train_ratio', type=float, default=0.8)
    parser.add_argument('--val_ratio', type=float, default=0.2)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    source_images = Path(args.source_images).resolve()
    dataset_root = Path(args.dataset_root).resolve()
    yaml_path = Path(args.yolo_yaml).resolve()
    venv_dir = Path(args.venv_dir).resolve()
    model_path = Path(args.model).resolve()
    project_dir = Path('models/yolo_models').resolve()

    print(f"Origen de imágenes: {source_images}")
    print(f"Destino dataset: {dataset_root}")

    # 1) Construir splits (train/val). Asume que los .txt están junto a cada imagen
    build_splits(source_images, dataset_root, args.train_ratio, args.val_ratio)

    # 2) Escribir dataset.yaml con rutas absolutas y clases
    write_dataset_yaml(yaml_path, dataset_root, args.classes)
    print(f"Escrito dataset.yaml en: {yaml_path}")

    # 3) Entrenar
    run_yolo_train(venv_dir, model_path, yaml_path, args.epochs, args.imgsz, project_dir, args.run_name)
    print("Entrenamiento completado.")


if __name__ == '__main__':
    try:
        random.seed(0)
        main()
    except subprocess.CalledProcessError as e:
        print(f"Error ejecutando YOLO CLI (código {e.returncode}). Revisa la salida anterior.", file=sys.stderr)
        sys.exit(e.returncode)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


