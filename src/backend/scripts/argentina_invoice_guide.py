#!/usr/bin/env python3
"""
Guía y configuración para entrenar YOLO con facturas argentinas
Incluye las variantes más comunes del sistema fiscal argentino
"""

def get_argentina_invoice_classes():
    """
    Clases específicas para facturas argentinas según AFIP
    Basado en los campos obligatorios y opcionales del sistema fiscal
    """
    return [
        # Campos obligatorios principales
        'numero_factura',      # Número de comprobante
        'fecha_emision',       # Fecha de emisión
        'proveedor',           # Razón social del emisor
        'cuit_proveedor',      # CUIT del emisor
        'cliente',             # Razón social del cliente
        'cuit_cliente',        # CUIT del cliente
        'condicion_iva',       # Condición frente al IVA
        'subtotal',            # Subtotal
        'iva_21',              # IVA 21%
        'iva_10_5',            # IVA 10.5%
        'iva_27',              # IVA 27%
        'total',               # Total
        
        # Campos de productos/servicios
        'items_table',         # Tabla de items
        'codigo_producto',     # Código de producto
        'descripcion',         # Descripción del producto/servicio
        'cantidad',            # Cantidad
        'precio_unitario',     # Precio unitario
        'importe_item',        # Importe del item
        
        # Campos adicionales comunes
        'fecha_vencimiento',   # Fecha de vencimiento
        'forma_pago',          # Forma de pago
        'observaciones',       # Observaciones
        'logo',                # Logo de la empresa
        'firma',               # Firma digital
        'codigo_barras',       # Código de barras
        'qr_code',             # Código QR AFIP
        'numero_cae',          # Número CAE
        'fecha_vto_cae',       # Fecha vencimiento CAE
        'punto_venta',         # Punto de venta
        'tipo_comprobante',    # Tipo de comprobante (A, B, C, etc.)
        'moneda',              # Moneda
        'tipo_cambio',         # Tipo de cambio
        'importe_neto',        # Importe neto gravado
        'importe_exento',      # Importe exento
        'percepciones',        # Percepciones
        'retenciones',         # Retenciones
        'otros_tributos'       # Otros tributos
    ]


def get_invoice_variants():
    """
    Variantes de facturas argentinas más comunes
    """
    return {
        'factura_a': {
            'description': 'Factura A - Responsable Inscripto',
            'fields': ['numero_factura', 'fecha_emision', 'proveedor', 'cuit_proveedor', 
                      'cliente', 'cuit_cliente', 'condicion_iva', 'items_table', 
                      'subtotal', 'iva_21', 'total', 'qr_code', 'numero_cae']
        },
        'factura_b': {
            'description': 'Factura B - Consumidor Final',
            'fields': ['numero_factura', 'fecha_emision', 'proveedor', 'cuit_proveedor',
                      'cliente', 'items_table', 'subtotal', 'iva_21', 'total', 'qr_code']
        },
        'factura_c': {
            'description': 'Factura C - Exento',
            'fields': ['numero_factura', 'fecha_emision', 'proveedor', 'cuit_proveedor',
                      'cliente', 'cuit_cliente', 'items_table', 'subtotal', 'total']
        },
        'nota_credito': {
            'description': 'Nota de Crédito',
            'fields': ['numero_factura', 'fecha_emision', 'proveedor', 'cuit_proveedor',
                      'cliente', 'cuit_cliente', 'items_table', 'subtotal', 'iva_21', 'total']
        },
        'nota_debito': {
            'description': 'Nota de Débito',
            'fields': ['numero_factura', 'fecha_emision', 'proveedor', 'cuit_proveedor',
                      'cliente', 'cuit_cliente', 'items_table', 'subtotal', 'iva_21', 'total']
        },
        'remito': {
            'description': 'Remito',
            'fields': ['numero_factura', 'fecha_emision', 'proveedor', 'cuit_proveedor',
                      'cliente', 'cuit_cliente', 'items_table', 'observaciones']
        },
        'presupuesto': {
            'description': 'Presupuesto',
            'fields': ['numero_factura', 'fecha_emision', 'proveedor', 'cuit_proveedor',
                      'cliente', 'items_table', 'subtotal', 'iva_21', 'total', 'fecha_vencimiento']
        }
    }


def create_optimized_yaml():
    """
    Crea dataset.yaml optimizado para facturas argentinas
    """
    classes = get_argentina_invoice_classes()
    
    yaml_content = f"""# Dataset YAML optimizado para facturas argentinas
# Basado en normativas Arca y variantes más comunes

train: C:/Users/amdiaz/Desktop/code/Python/v.13.13/invoice-data/src/backend/datasets/invoices_argentina/images/train
val: C:/Users/amdiaz/Desktop/code/Python/v.13.13/invoice-data/src/backend/datasets/invoices_argentina/images/val
test: C:/Users/amdiaz/Desktop/code/Python/v.13.13/invoice-data/src/backend/datasets/invoices_argentina/images/test

# Clases específicas para facturas argentinas (AFIP)
names:
"""
    
    for idx, name in enumerate(classes):
        yaml_content += f"  {idx}: {name}\n"
    
    return yaml_content


def get_training_recommendations():
    """
    Recomendaciones específicas para entrenar con facturas argentinas
    """
    return {
        'dataset_size': {
            'minimum': '50-100 imágenes por variante',
            'recommended': '200-500 imágenes por variante',
            'optimal': '500+ imágenes por variante'
        },
        'image_quality': {
            'resolution': 'Mínimo 800x600, recomendado 1200x800',
            'format': 'JPG o PNG',
            'orientation': 'Incluir rotaciones y perspectivas'
        },
        'annotation_guidelines': {
            'bounding_boxes': 'Incluir todo el texto del campo',
            'class_consistency': 'Usar siempre la misma clase para el mismo tipo de campo',
            'edge_cases': 'Anotar campos parcialmente visibles o cortados'
        },
        'training_parameters': {
            'epochs': '50-100 para dataset pequeño, 100-200 para dataset grande',
            'batch_size': '4-8 (ajustar según GPU)',
            'image_size': '640x640 o 800x800',
            'learning_rate': '0.001-0.005',
            'patience': '20-30 épocas'
        },
        'data_augmentation': {
            'rotation': '±15 grados',
            'brightness': '±20%',
            'contrast': '±20%',
            'noise': 'Ligero ruido gaussiano',
            'blur': 'Desenfoque ligero'
        }
    }


def print_argentina_guide():
    """
    Imprime guía completa para facturas argentinas
    """
    print("🇦🇷 GUÍA PARA ENTRENAR YOLO CON FACTURAS ARGENTINAS")
    print("=" * 60)
    
    print("\n📋 CAMPOS PRINCIPALES (AFIP):")
    classes = get_argentina_invoice_classes()
    for i, cls in enumerate(classes[:15]):  # Mostrar primeros 15
        print(f"  {i:2d}: {cls}")
    print(f"  ... y {len(classes)-15} campos adicionales")
    
    print("\n📄 VARIANTES DE FACTURAS:")
    variants = get_invoice_variants()
    for variant, info in variants.items():
        print(f"  • {variant.upper()}: {info['description']}")
        print(f"    Campos típicos: {', '.join(info['fields'][:5])}...")
    
    print("\n🎯 RECOMENDACIONES DE ENTRENAMIENTO:")
    recommendations = get_training_recommendations()
    for category, items in recommendations.items():
        print(f"\n  {category.upper()}:")
        for key, value in items.items():
            print(f"    • {key}: {value}")
    
    print("\n🚀 PRÓXIMOS PASOS:")
    print("  1. Recolectar 50-100 facturas de cada variante")
    print("  2. Anotar con labelImg usando las clases definidas")
    print("  3. Crear splits train/val/test (80/15/5)")
    print("  4. Entrenar con parámetros optimizados")
    print("  5. Validar con facturas de prueba")
    
    print("\n📝 COMANDO DE ENTRENAMIENTO RECOMENDADO:")
    print("""
yolo detect train \\
  data=yolo/dataset_argentina.yaml \\
  model=yolov8n.pt \\
  epochs=100 \\
  imgsz=640 \\
  batch=4 \\
  lr0=0.003 \\
  patience=25 \\
  project=models/yolo_models \\
  name=argentina_invoices_v1
""")


if __name__ == '__main__':
    print_argentina_guide()
    
    # Crear dataset.yaml optimizado
    yaml_content = create_optimized_yaml()
    with open('yolo/dataset_argentina.yaml', 'w', encoding='utf-8') as f:
        f.write(yaml_content)
    print(f"\n✅ Dataset YAML creado: yolo/dataset_argentina.yaml")
