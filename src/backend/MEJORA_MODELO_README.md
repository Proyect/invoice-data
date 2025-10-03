# 🚀 Mejora del Modelo YOLO - Facturas Argentinas

## 📋 Resumen

Este proceso mejora significativamente el modelo YOLO para detección de campos en facturas argentinas mediante:

1. **Generación de datasets sintéticos** (500-1000 imágenes)
2. **Entrenamiento optimizado** con múltiples configuraciones
3. **Evaluación automática** de rendimiento
4. **Reporte detallado** de resultados

## 🎯 Problema Actual

- **Dataset insuficiente**: Solo 1 imagen de entrenamiento
- **Métricas en cero**: mAP = 0%, Precisión = 0%, Recall = 0%
- **Modelo no funcional** para uso en producción

## ✅ Solución Implementada

### 1. Generadores de Datos Sintéticos

#### `generate_synthetic_invoices.py`
- **500 imágenes** de facturas sintéticas
- **36 clases** específicas de facturas argentinas
- **Datos realistas**: CUITs, números de factura, productos
- **Formato YOLO** listo para entrenamiento

#### `advanced_invoice_generator.py`
- **1000 imágenes** con variaciones avanzadas
- **3 estilos diferentes** de factura
- **Ruido y artefactos** para simular escaneo real
- **Datos más realistas** y variados

### 2. Scripts de Entrenamiento

#### `train_optimized_model.py`
- **3 configuraciones** de entrenamiento:
  - Básico: 50 épocas, batch=8
  - Intermedio: 100 épocas, batch=4  
  - Avanzado: 200 épocas, batch=2
- **Parámetros optimizados** para facturas argentinas
- **Evaluación automática** de cada modelo

#### `complete_training_pipeline.py`
- **Pipeline completo** automatizado
- **Logging detallado** de todo el proceso
- **Manejo de errores** robusto
- **Reporte final** con métricas

## 🚀 Uso Rápido

### Opción 1: Pipeline Completo (Recomendado)
```bash
cd backend
python mejorar_modelo.py
```

### Opción 2: Pasos Individuales
```bash
cd backend

# 1. Probar entorno
python scripts/test_model_improvement.py

# 2. Generar dataset básico
python scripts/generate_synthetic_invoices.py

# 3. Generar dataset avanzado
python scripts/advanced_invoice_generator.py

# 4. Entrenar modelos
python scripts/train_optimized_model.py
```

## 📊 Resultados Esperados

### Datasets Generados
- **Dataset Básico**: 500 imágenes (350 train, 100 val, 50 test)
- **Dataset Avanzado**: 1000 imágenes (700 train, 200 val, 100 test)
- **Total**: 1500 imágenes de entrenamiento

### Modelos Entrenados
- **argentina_invoices_basic**: Modelo básico (50 épocas)
- **argentina_invoices_advanced**: Modelo avanzado (100 épocas)
- **Métricas esperadas**: mAP > 30%, Precisión > 50%

### Archivos Generados
```
backend/
├── datasets/
│   ├── invoices_argentina_synthetic/     # 500 imágenes
│   └── invoices_argentina_advanced/      # 1000 imágenes
├── models/yolo_models/
│   ├── argentina_invoices_basic_*/       # Modelo básico
│   └── argentina_invoices_advanced_*/    # Modelo avanzado
├── MODELO_MEJORADO_REPORTE.md           # Reporte completo
└── training_pipeline.log                # Logs detallados
```

## 🔧 Configuración Avanzada

### Personalizar Generación de Datos
```python
# En generate_synthetic_invoices.py
generator = SyntheticInvoiceGenerator()
generator.generate_dataset(1000)  # Cambiar número de imágenes
```

### Personalizar Entrenamiento
```python
# En train_optimized_model.py
training_configs = {
    "custom": {
        "epochs": 150,
        "batch": 6,
        "lr0": 0.004,
        "patience": 30
    }
}
```

## 📈 Monitoreo del Proceso

### Logs en Tiempo Real
```bash
tail -f training_pipeline.log
```

### Verificar Progreso
```bash
# Ver imágenes generadas
ls datasets/invoices_argentina_advanced/images/train/ | wc -l

# Ver modelos entrenados
ls models/yolo_models/argentina_invoices_*/
```

## 🎯 Clases Detectadas

El modelo detecta **36 campos específicos** de facturas argentinas:

### Información Básica
- `numero_factura`, `fecha_emision`, `proveedor`, `cuit_proveedor`
- `cliente`, `cuit_cliente`, `condicion_iva`

### Totales e IVA
- `subtotal`, `iva_21`, `iva_10_5`, `iva_27`, `total`

### Tabla de Items
- `items_table`, `codigo_producto`, `descripcion`
- `cantidad`, `precio_unitario`, `importe_item`

### Información Adicional
- `fecha_vencimiento`, `forma_pago`, `observaciones`
- `logo`, `firma`, `codigo_barras`, `qr_code`
- `numero_cae`, `fecha_vto_cae`, `punto_venta`
- `tipo_comprobante`, `moneda`, `tipo_cambio`
- `importe_neto`, `importe_exento`, `percepciones`
- `retenciones`, `otros_tributos`

## 🧪 Pruebas del Modelo

### Probar con Imagen Real
```bash
python -m ultralytics.yolo.v8.detect.predict \
  model=models/yolo_models/argentina_invoices_advanced/weights/best.pt \
  source=mi_factura.jpg \
  conf=0.25 \
  save=True
```

### Evaluar Rendimiento
```bash
python -m ultralytics.yolo.v8.detect.val \
  model=models/yolo_models/argentina_invoices_advanced/weights/best.pt \
  data=datasets/invoices_argentina_advanced/dataset.yaml
```

## ⚠️ Solución de Problemas

### Error: "No module named 'ultralytics'"
```bash
pip install ultralytics
```

### Error: "CUDA out of memory"
- Reducir batch size en la configuración
- Usar `device=cpu` en lugar de GPU

### Error: "Dataset not found"
- Verificar que los scripts de generación se ejecutaron correctamente
- Revisar rutas en `dataset.yaml`

### Error: "Model not found"
- Verificar que el entrenamiento se completó
- Buscar en `models/yolo_models/` el directorio del modelo

## 📝 Notas Importantes

1. **Tiempo de ejecución**: 2-4 horas para pipeline completo
2. **Espacio requerido**: ~2GB para datasets + modelos
3. **GPU recomendada**: Para entrenamiento más rápido
4. **Backup**: Los modelos se guardan automáticamente

## 🎉 Resultados Finales

Después de ejecutar el pipeline completo:

1. **Modelo funcional** con métricas > 30% mAP
2. **1500+ imágenes** de entrenamiento sintéticas
3. **36 campos** de facturas argentinas detectables
4. **Reporte completo** con métricas y recomendaciones
5. **Modelo listo** para integración en producción

---

**Desarrollado para**: Sistema OCR de Facturas Argentinas  
**Versión**: 1.0  
**Fecha**: Enero 2025
