#!/usr/bin/env bash
set -e
DATASET_YAML="yolo/dataset.yaml"
WEIGHTS="yolov8n.pt" # o yolov11n.pt si lo tienes
IMG=640
EPOCHS=150
BATCH=16
PROJECT="runs-invoice"
NAME="yolo-detect"


# Ejemplo con Ultralytics CLI
yolo detect train \
data=$DATASET_YAML \
model=$WEIGHTS \
imgsz=$IMG \
epochs=$EPOCHS \
batch=$BATCH \
optimizer=SGD \
amp=True \
lr0=0.01 \
lrf=0.01 \
weight_decay=0.0005 \
patience=50 \
project=$PROJECT \
name=$NAME