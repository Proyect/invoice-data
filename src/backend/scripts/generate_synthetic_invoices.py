#!/usr/bin/env python3
"""
Generador de facturas sintéticas argentinas para entrenamiento YOLO
Basado en normativas AFIP y formatos estándar
"""

import os
import random
import json
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from pathlib import Path
import yaml
from datetime import datetime, timedelta
import math

class SyntheticInvoiceGenerator:
    def __init__(self, output_dir="datasets/invoices_argentina_synthetic"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Crear subdirectorios
        (self.output_dir / "images" / "train").mkdir(parents=True, exist_ok=True)
        (self.output_dir / "images" / "val").mkdir(parents=True, exist_ok=True)
        (self.output_dir / "images" / "test").mkdir(parents=True, exist_ok=True)
        (self.output_dir / "labels" / "train").mkdir(parents=True, exist_ok=True)
        (self.output_dir / "labels" / "val").mkdir(parents=True, exist_ok=True)
        (self.output_dir / "labels" / "test").mkdir(parents=True, exist_ok=True)
        
        # Datos de prueba para facturas argentinas
        self.empresas = [
            "TECHNOLOGY S.A.",
            "INDUSTRIAS ARGENTINAS S.R.L.",
            "COMERCIAL DEL SUR S.A.",
            "SERVICIOS INTEGRALES S.A.",
            "CONSULTORA PROFESIONAL S.R.L.",
            "DISTRIBUIDORA MAYORISTA S.A.",
            "CONSTRUCCIONES MODERNAS S.A.",
            "ALIMENTOS NATURALES S.R.L.",
            "TEXTILES ARGENTINOS S.A.",
            "AUTOMOTORES DEL NORTE S.A."
        ]
        
        self.clientes = [
            "JUAN PEREZ",
            "MARIA GONZALEZ",
            "CARLOS RODRIGUEZ",
            "ANA MARTINEZ",
            "LUIS FERNANDEZ",
            "SOFIA LOPEZ",
            "DIEGO GARCIA",
            "VALENTINA HERRERA",
            "MARTIN SANCHEZ",
            "CAMILA TORRES"
        ]
        
        self.productos = [
            ("PRODUCTO A", "PZA", 1500.00),
            ("SERVICIO B", "UNI", 2500.00),
            ("MATERIAL C", "KG", 800.00),
            ("HERRAMIENTA D", "UNI", 3500.00),
            ("INSUMO E", "LTS", 1200.00),
            ("EQUIPO F", "UNI", 15000.00),
            ("REPUESTO G", "UNI", 4500.00),
            ("ACCESORIO H", "UNI", 750.00),
            ("CONSUMIBLE I", "CAJ", 3000.00),
            ("ESPECIAL J", "UNI", 8500.00)
        ]
        
        # Configuración de clases YOLO (36 clases)
        self.classes = [
            "numero_factura", "fecha_emision", "proveedor", "cuit_proveedor",
            "cliente", "cuit_cliente", "condicion_iva", "subtotal", "iva_21",
            "iva_10_5", "iva_27", "total", "items_table", "codigo_producto",
            "descripcion", "cantidad", "precio_unitario", "importe_item",
            "fecha_vencimiento", "forma_pago", "observaciones", "logo",
            "firma", "codigo_barras", "qr_code", "numero_cae", "fecha_vto_cae",
            "punto_venta", "tipo_comprobante", "moneda", "tipo_cambio",
            "importe_neto", "importe_exento", "percepciones", "retenciones", "otros_tributos"
        ]
        
        # Configuración de colores y estilos
        self.colors = {
            'background': (255, 255, 255),
            'text': (0, 0, 0),
            'header': (50, 50, 150),
            'border': (200, 200, 200),
            'table_header': (240, 240, 240),
            'table_row': (250, 250, 250)
        }
    
    def generate_cuit(self):
        """Genera un CUIT válido argentino"""
        base = random.randint(20000000000, 30999999999)
        return f"{base:011d}"
    
    def generate_invoice_number(self):
        """Genera número de factura"""
        punto_venta = random.randint(1, 9999)
        numero = random.randint(1, 99999999)
        return f"{punto_venta:04d}-{numero:08d}"
    
    def generate_date(self):
        """Genera fecha aleatoria del último año"""
        start_date = datetime.now() - timedelta(days=365)
        random_days = random.randint(0, 365)
        return start_date + timedelta(days=random_days)
    
    def draw_text_with_bbox(self, draw, text, position, font, color, class_name, bboxes):
        """Dibuja texto y guarda bounding box para YOLO"""
        x, y = position
        bbox = draw.textbbox((x, y), text, font=font)
        draw.text((x, y), text, font=font, fill=color)
        
        # Convertir a formato YOLO (normalizado)
        img_width, img_height = 800, 1000  # Tamaño fijo de imagen
        x_center = (bbox[0] + bbox[2]) / 2 / img_width
        y_center = (bbox[1] + bbox[3]) / 2 / img_height
        width = (bbox[2] - bbox[0]) / img_width
        height = (bbox[3] - bbox[1]) / img_height
        
        class_id = self.classes.index(class_name) if class_name in self.classes else 0
        bboxes.append(f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}")
    
    def generate_invoice(self, invoice_id):
        """Genera una factura sintética completa"""
        # Crear imagen base
        img = Image.new('RGB', (800, 1000), self.colors['background'])
        draw = ImageDraw.Draw(img)
        
        # Fuentes (usar fuentes del sistema)
        try:
            title_font = ImageFont.truetype("arial.ttf", 24)
            header_font = ImageFont.truetype("arial.ttf", 16)
            normal_font = ImageFont.truetype("arial.ttf", 12)
            small_font = ImageFont.truetype("arial.ttf", 10)
        except:
            title_font = ImageFont.load_default()
            header_font = ImageFont.load_default()
            normal_font = ImageFont.load_default()
            small_font = ImageFont.load_default()
        
        bboxes = []
        
        # Datos aleatorios
        empresa = random.choice(self.empresas)
        cliente = random.choice(self.clientes)
        cuit_empresa = self.generate_cuit()
        cuit_cliente = self.generate_cuit()
        numero_factura = self.generate_invoice_number()
        fecha = self.generate_date()
        punto_venta = numero_factura.split('-')[0]
        
        # Calcular totales
        num_items = random.randint(1, 5)
        items = random.sample(self.productos, num_items)
        subtotal = sum(cantidad * precio for _, _, precio in items for cantidad in [random.randint(1, 10)])
        iva_21 = subtotal * 0.21
        total = subtotal + iva_21
        
        # HEADER - Logo y datos de empresa
        y_pos = 20
        
        # Logo (simulado)
        logo_bbox = (20, y_pos, 120, y_pos + 60)
        draw.rectangle(logo_bbox, fill=self.colors['table_header'], outline=self.colors['border'])
        self.draw_text_with_bbox(draw, "LOGO", (30, y_pos + 20), header_font, self.colors['text'], "logo", bboxes)
        
        # Datos de empresa
        self.draw_text_with_bbox(draw, empresa, (150, y_pos), header_font, self.colors['header'], "proveedor", bboxes)
        self.draw_text_with_bbox(draw, f"CUIT: {cuit_empresa}", (150, y_pos + 25), normal_font, self.colors['text'], "cuit_proveedor", bboxes)
        
        y_pos += 80
        
        # INFORMACIÓN DE FACTURA
        self.draw_text_with_bbox(draw, "FACTURA", (20, y_pos), title_font, self.colors['header'], "tipo_comprobante", bboxes)
        self.draw_text_with_bbox(draw, f"N°: {numero_factura}", (400, y_pos), header_font, self.colors['text'], "numero_factura", bboxes)
        self.draw_text_with_bbox(draw, f"P.V.: {punto_venta}", (400, y_pos + 25), normal_font, self.colors['text'], "punto_venta", bboxes)
        self.draw_text_with_bbox(draw, f"Fecha: {fecha.strftime('%d/%m/%Y')}", (400, y_pos + 45), normal_font, self.colors['text'], "fecha_emision", bboxes)
        
        y_pos += 80
        
        # DATOS DEL CLIENTE
        self.draw_text_with_bbox(draw, "CLIENTE:", (20, y_pos), header_font, self.colors['header'], "cliente", bboxes)
        self.draw_text_with_bbox(draw, cliente, (100, y_pos), normal_font, self.colors['text'], "cliente", bboxes)
        self.draw_text_with_bbox(draw, f"CUIT: {cuit_cliente}", (100, y_pos + 20), normal_font, self.colors['text'], "cuit_cliente", bboxes)
        self.draw_text_with_bbox(draw, "Cond. IVA: Responsable Inscripto", (100, y_pos + 40), normal_font, self.colors['text'], "condicion_iva", bboxes)
        
        y_pos += 100
        
        # TABLA DE ITEMS
        table_start_y = y_pos
        self.draw_text_with_bbox(draw, "DETALLE DE PRODUCTOS/SERVICIOS", (20, y_pos), header_font, self.colors['header'], "items_table", bboxes)
        y_pos += 30
        
        # Headers de tabla
        headers = ["Código", "Descripción", "Cant.", "Precio Unit.", "Importe"]
        x_positions = [20, 150, 350, 450, 600]
        
        for i, header in enumerate(headers):
            self.draw_text_with_bbox(draw, header, (x_positions[i], y_pos), normal_font, self.colors['text'], "items_table", bboxes)
        
        y_pos += 25
        
        # Items de la tabla
        for i, (desc, unidad, precio_base) in enumerate(items):
            cantidad = random.randint(1, 10)
            precio = precio_base * (0.8 + random.random() * 0.4)  # Variación de precio
            importe = cantidad * precio
            
            codigo = f"P{i+1:03d}"
            self.draw_text_with_bbox(draw, codigo, (x_positions[0], y_pos), small_font, self.colors['text'], "codigo_producto", bboxes)
            self.draw_text_with_bbox(draw, desc, (x_positions[1], y_pos), small_font, self.colors['text'], "descripcion", bboxes)
            self.draw_text_with_bbox(draw, str(cantidad), (x_positions[2], y_pos), small_font, self.colors['text'], "cantidad", bboxes)
            self.draw_text_with_bbox(draw, f"${precio:.2f}", (x_positions[3], y_pos), small_font, self.colors['text'], "precio_unitario", bboxes)
            self.draw_text_with_bbox(draw, f"${importe:.2f}", (x_positions[4], y_pos), small_font, self.colors['text'], "importe_item", bboxes)
            
            y_pos += 20
        
        # TOTALES
        y_pos += 20
        self.draw_text_with_bbox(draw, f"Subtotal: ${subtotal:.2f}", (500, y_pos), normal_font, self.colors['text'], "subtotal", bboxes)
        y_pos += 20
        self.draw_text_with_bbox(draw, f"I.V.A. 21%: ${iva_21:.2f}", (500, y_pos), normal_font, self.colors['text'], "iva_21", bboxes)
        y_pos += 20
        self.draw_text_with_bbox(draw, f"TOTAL: ${total:.2f}", (500, y_pos), header_font, self.colors['header'], "total", bboxes)
        
        # INFORMACIÓN ADICIONAL
        y_pos += 60
        self.draw_text_with_bbox(draw, f"Forma de Pago: Efectivo", (20, y_pos), normal_font, self.colors['text'], "forma_pago", bboxes)
        self.draw_text_with_bbox(draw, f"Vencimiento: {(fecha + timedelta(days=30)).strftime('%d/%m/%Y')}", (20, y_pos + 20), normal_font, self.colors['text'], "fecha_vencimiento", bboxes)
        
        # CÓDIGOS DE BARRAS Y QR (simulados)
        y_pos += 60
        self.draw_text_with_bbox(draw, "CÓDIGO DE BARRAS", (20, y_pos), small_font, self.colors['text'], "codigo_barras", bboxes)
        self.draw_text_with_bbox(draw, "QR CODE", (400, y_pos), small_font, self.colors['text'], "qr_code", bboxes)
        
        # FIRMA
        y_pos += 40
        self.draw_text_with_bbox(draw, "FIRMA", (20, y_pos), normal_font, self.colors['text'], "firma", bboxes)
        
        return img, bboxes
    
    def generate_dataset(self, num_images=500):
        """Genera el dataset completo"""
        print(f"Generando {num_images} facturas sintéticas...")
        
        # Distribución: 70% train, 20% val, 10% test
        train_count = int(num_images * 0.7)
        val_count = int(num_images * 0.2)
        test_count = num_images - train_count - val_count
        
        splits = [
            ("train", train_count),
            ("val", val_count),
            ("test", test_count)
        ]
        
        for split_name, count in splits:
            print(f"Generando {count} imágenes para {split_name}...")
            
            for i in range(count):
                img, bboxes = self.generate_invoice(f"{split_name}_{i:04d}")
                
                # Guardar imagen
                img_path = self.output_dir / "images" / split_name / f"synthetic_invoice_{i:04d}.jpg"
                img.save(img_path, "JPEG", quality=95)
                
                # Guardar labels YOLO
                label_path = self.output_dir / "labels" / split_name / f"synthetic_invoice_{i:04d}.txt"
                with open(label_path, 'w') as f:
                    f.write('\n'.join(bboxes))
                
                if (i + 1) % 50 == 0:
                    print(f"  Generadas {i + 1}/{count} imágenes...")
        
        # Crear dataset.yaml
        self.create_dataset_yaml()
        print(f"Dataset generado en: {self.output_dir}")
    
    def create_dataset_yaml(self):
        """Crea el archivo dataset.yaml para YOLO"""
        dataset_yaml = {
            'train': str(self.output_dir / "images" / "train"),
            'val': str(self.output_dir / "images" / "val"),
            'test': str(self.output_dir / "images" / "test"),
            'nc': len(self.classes),
            'names': {i: name for i, name in enumerate(self.classes)}
        }
        
        yaml_path = self.output_dir / "dataset.yaml"
        with open(yaml_path, 'w') as f:
            yaml.dump(dataset_yaml, f, default_flow_style=False)
        
        print(f"Dataset YAML creado: {yaml_path}")

def main():
    """Función principal"""
    print("🚀 Generador de Facturas Sintéticas Argentinas")
    print("=" * 50)
    
    generator = SyntheticInvoiceGenerator()
    
    # Generar dataset con 500 imágenes
    generator.generate_dataset(500)
    
    print("\n✅ Dataset generado exitosamente!")
    print("\n📊 Estadísticas:")
    print(f"  - Total de imágenes: 500")
    print(f"  - Entrenamiento: 350 imágenes")
    print(f"  - Validación: 100 imágenes")
    print(f"  - Prueba: 50 imágenes")
    print(f"  - Clases: 36 (campos de factura argentina)")
    
    print("\n🎯 Próximos pasos:")
    print("1. Revisar algunas imágenes generadas")
    print("2. Entrenar modelo YOLO con el nuevo dataset")
    print("3. Evaluar rendimiento del modelo")

if __name__ == "__main__":
    main()
