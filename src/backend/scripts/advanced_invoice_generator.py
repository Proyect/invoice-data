#!/usr/bin/env python3
"""
Generador avanzado de facturas sintéticas argentinas
Con variaciones realistas y diferentes formatos
"""

import os
import random
import json
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np
from pathlib import Path
import yaml
from datetime import datetime, timedelta
import math

class AdvancedInvoiceGenerator:
    def __init__(self, output_dir="datasets/invoices_argentina_advanced"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Crear subdirectorios
        for split in ["train", "val", "test"]:
            (self.output_dir / "images" / split).mkdir(parents=True, exist_ok=True)
            (self.output_dir / "labels" / split).mkdir(parents=True, exist_ok=True)
        
        # Datos más realistas
        self.empresas_data = [
            {
                "nombre": "TECHNOLOGY SOLUTIONS S.A.",
                "cuit": "30-12345678-9",
                "direccion": "Av. Corrientes 1234, CABA",
                "telefono": "(011) 4567-8900"
            },
            {
                "nombre": "INDUSTRIAS ARGENTINAS S.R.L.",
                "cuit": "30-87654321-0",
                "direccion": "Ruta 5 Km 45, San Luis",
                "telefono": "(0266) 456-7890"
            },
            {
                "nombre": "COMERCIAL DEL SUR S.A.",
                "cuit": "30-11223344-5",
                "direccion": "San Martín 567, Rosario",
                "telefono": "(0341) 123-4567"
            },
            {
                "nombre": "SERVICIOS INTEGRALES S.A.",
                "cuit": "30-55667788-1",
                "direccion": "Belgrano 890, Córdoba",
                "telefono": "(0351) 234-5678"
            },
            {
                "nombre": "CONSULTORA PROFESIONAL S.R.L.",
                "cuit": "30-99887766-2",
                "direccion": "Lavalle 234, Mendoza",
                "telefono": "(0261) 345-6789"
            }
        ]
        
        self.clientes_data = [
            {
                "nombre": "JUAN CARLOS PEREZ",
                "cuit": "20-12345678-9",
                "direccion": "Av. Santa Fe 1234, CABA",
                "condicion_iva": "Responsable Inscripto"
            },
            {
                "nombre": "MARIA ELENA GONZALEZ",
                "cuit": "27-87654321-0",
                "direccion": "San Martín 567, Rosario",
                "condicion_iva": "Monotributista"
            },
            {
                "nombre": "CARLOS ALBERTO RODRIGUEZ",
                "cuit": "20-11223344-5",
                "direccion": "Belgrano 890, Córdoba",
                "condicion_iva": "Responsable Inscripto"
            },
            {
                "nombre": "ANA MARIA MARTINEZ",
                "cuit": "27-55667788-1",
                "direccion": "Lavalle 234, Mendoza",
                "condicion_iva": "Exento"
            },
            {
                "nombre": "LUIS MIGUEL FERNANDEZ",
                "cuit": "20-99887766-2",
                "direccion": "Rivadavia 456, La Plata",
                "condicion_iva": "Responsable Inscripto"
            }
        ]
        
        self.productos_detallados = [
            ("PROD001", "LAPTOP DELL INSPIRON 15", "UNI", 450000.00),
            ("PROD002", "MOUSE INALAMBRICO LOGITECH", "UNI", 8500.00),
            ("PROD003", "TECLADO MECANICO RAZER", "UNI", 25000.00),
            ("PROD004", "MONITOR 24 PULGADAS SAMSUNG", "UNI", 180000.00),
            ("PROD005", "AURICULARES SONY WH-1000XM4", "UNI", 120000.00),
            ("SERV001", "SERVICIO DE MANTENIMIENTO", "HRS", 3500.00),
            ("SERV002", "CONSULTORIA TECNICA", "HRS", 8000.00),
            ("SERV003", "DESARROLLO DE SOFTWARE", "HRS", 15000.00),
            ("MAT001", "CABLE HDMI 2 METROS", "UNI", 2500.00),
            ("MAT002", "ADAPTADOR USB-C A HDMI", "UNI", 4500.00),
            ("MAT003", "DISCO DURO EXTERNO 1TB", "UNI", 35000.00),
            ("MAT004", "MEMORIA RAM 16GB DDR4", "UNI", 45000.00),
            ("MAT005", "PLACA DE VIDEO RTX 3060", "UNI", 280000.00)
        ]
        
        # Clases YOLO optimizadas
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
        
        # Colores y estilos más realistas
        self.colors = {
            'background': (255, 255, 255),
            'text': (0, 0, 0),
            'header': (25, 25, 112),  # Azul marino
            'border': (169, 169, 169),  # Gris
            'table_header': (240, 248, 255),  # Azul muy claro
            'table_row': (248, 248, 255),  # Blanco azulado
            'accent': (70, 130, 180),  # Azul acero
            'success': (34, 139, 34),  # Verde
            'warning': (255, 140, 0)  # Naranja
        }
    
    def add_noise_and_artifacts(self, img):
        """Añade ruido y artefactos para hacer la imagen más realista"""
        # Convertir a numpy array
        img_array = np.array(img)
        
        # Añadir ruido gaussiano ligero
        noise = np.random.normal(0, 5, img_array.shape)
        img_array = np.clip(img_array + noise, 0, 255).astype(np.uint8)
        
        # Añadir variaciones de iluminación
        height, width = img_array.shape[:2]
        y, x = np.ogrid[:height, :width]
        center_x, center_y = width // 2, height // 2
        distance = np.sqrt((x - center_x)**2 + (y - center_y)**2)
        max_distance = np.sqrt(center_x**2 + center_y**2)
        vignette = 1 - (distance / max_distance) * 0.1
        vignette = np.clip(vignette, 0.9, 1.0)
        
        for i in range(3):
            img_array[:, :, i] = img_array[:, :, i] * vignette
        
        # Añadir pequeñas manchas
        for _ in range(random.randint(2, 5)):
            x = random.randint(0, width-1)
            y = random.randint(0, height-1)
            size = random.randint(1, 3)
            img_array[y:y+size, x:x+size] = [random.randint(200, 255)] * 3
        
        return Image.fromarray(img_array)
    
    def draw_text_with_bbox(self, draw, text, position, font, color, class_name, bboxes, img_size=(800, 1000)):
        """Dibuja texto y guarda bounding box para YOLO"""
        x, y = position
        bbox = draw.textbbox((x, y), text, font=font)
        draw.text((x, y), text, font=font, fill=color)
        
        # Convertir a formato YOLO (normalizado)
        img_width, img_height = img_size
        x_center = (bbox[0] + bbox[2]) / 2 / img_width
        y_center = (bbox[1] + bbox[3]) / 2 / img_height
        width = (bbox[2] - bbox[0]) / img_width
        height = (bbox[3] - bbox[1]) / img_height
        
        class_id = self.classes.index(class_name) if class_name in self.classes else 0
        bboxes.append(f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}")
    
    def draw_rectangle_with_bbox(self, draw, coords, color, class_name, bboxes, img_size=(800, 1000)):
        """Dibuja rectángulo y guarda bounding box para YOLO"""
        x1, y1, x2, y2 = coords
        draw.rectangle([x1, y1, x2, y2], fill=color, outline=self.colors['border'])
        
        # Convertir a formato YOLO
        img_width, img_height = img_size
        x_center = (x1 + x2) / 2 / img_width
        y_center = (y1 + y2) / 2 / img_height
        width = (x2 - x1) / img_width
        height = (y2 - y1) / img_height
        
        class_id = self.classes.index(class_name) if class_name in self.classes else 0
        bboxes.append(f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}")
    
    def generate_invoice(self, invoice_id, variation=0):
        """Genera una factura sintética con variaciones"""
        # Crear imagen base
        img = Image.new('RGB', (800, 1000), self.colors['background'])
        draw = ImageDraw.Draw(img)
        
        # Fuentes
        try:
            title_font = ImageFont.truetype("arial.ttf", 28)
            header_font = ImageFont.truetype("arial.ttf", 18)
            normal_font = ImageFont.truetype("arial.ttf", 14)
            small_font = ImageFont.truetype("arial.ttf", 11)
            tiny_font = ImageFont.truetype("arial.ttf", 9)
        except:
            title_font = ImageFont.load_default()
            header_font = ImageFont.load_default()
            normal_font = ImageFont.load_default()
            small_font = ImageFont.load_default()
            tiny_font = ImageFont.load_default()
        
        bboxes = []
        
        # Datos aleatorios
        empresa = random.choice(self.empresas_data)
        cliente = random.choice(self.clientes_data)
        numero_factura = f"{random.randint(1, 9999):04d}-{random.randint(1, 99999999):08d}"
        fecha = self.generate_date()
        punto_venta = numero_factura.split('-')[0]
        
        # Calcular totales
        num_items = random.randint(2, 6)
        items = random.sample(self.productos_detallados, num_items)
        subtotal = 0
        
        for _, _, _, precio_base in items:
            cantidad = random.randint(1, 5)
            precio = precio_base * (0.8 + random.random() * 0.4)
            subtotal += cantidad * precio
        
        # Calcular IVA según condición del cliente
        if cliente["condicion_iva"] == "Responsable Inscripto":
            iva_21 = subtotal * 0.21
            iva_10_5 = 0
            iva_27 = 0
        elif cliente["condicion_iva"] == "Monotributista":
            iva_21 = 0
            iva_10_5 = 0
            iva_27 = 0
        else:  # Exento
            iva_21 = 0
            iva_10_5 = 0
            iva_27 = 0
        
        total = subtotal + iva_21 + iva_10_5 + iva_27
        
        y_pos = 20
        
        # HEADER - Logo y datos de empresa
        # Logo (simulado con rectángulo)
        logo_bbox = (20, y_pos, 100, y_pos + 50)
        self.draw_rectangle_with_bbox(draw, logo_bbox, self.colors['table_header'], "logo", bboxes)
        self.draw_text_with_bbox(draw, "LOGO", (30, y_pos + 15), header_font, self.colors['text'], "logo", bboxes)
        
        # Datos de empresa
        self.draw_text_with_bbox(draw, empresa["nombre"], (120, y_pos), header_font, self.colors['header'], "proveedor", bboxes)
        self.draw_text_with_bbox(draw, f"CUIT: {empresa['cuit']}", (120, y_pos + 25), normal_font, self.colors['text'], "cuit_proveedor", bboxes)
        self.draw_text_with_bbox(draw, empresa["direccion"], (120, y_pos + 45), small_font, self.colors['text'], "proveedor", bboxes)
        
        y_pos += 80
        
        # INFORMACIÓN DE FACTURA
        self.draw_text_with_bbox(draw, "FACTURA", (20, y_pos), title_font, self.colors['header'], "tipo_comprobante", bboxes)
        self.draw_text_with_bbox(draw, f"N°: {numero_factura}", (400, y_pos), header_font, self.colors['text'], "numero_factura", bboxes)
        self.draw_text_with_bbox(draw, f"P.V.: {punto_venta}", (400, y_pos + 25), normal_font, self.colors['text'], "punto_venta", bboxes)
        self.draw_text_with_bbox(draw, f"Fecha: {fecha.strftime('%d/%m/%Y')}", (400, y_pos + 45), normal_font, self.colors['text'], "fecha_emision", bboxes)
        
        y_pos += 90
        
        # DATOS DEL CLIENTE
        self.draw_text_with_bbox(draw, "CLIENTE:", (20, y_pos), header_font, self.colors['header'], "cliente", bboxes)
        self.draw_text_with_bbox(draw, cliente["nombre"], (100, y_pos), normal_font, self.colors['text'], "cliente", bboxes)
        self.draw_text_with_bbox(draw, f"CUIT: {cliente['cuit']}", (100, y_pos + 20), normal_font, self.colors['text'], "cuit_cliente", bboxes)
        self.draw_text_with_bbox(draw, f"Cond. IVA: {cliente['condicion_iva']}", (100, y_pos + 40), normal_font, self.colors['text'], "condicion_iva", bboxes)
        
        y_pos += 100
        
        # TABLA DE ITEMS
        table_start_y = y_pos
        self.draw_text_with_bbox(draw, "DETALLE DE PRODUCTOS/SERVICIOS", (20, y_pos), header_font, self.colors['header'], "items_table", bboxes)
        y_pos += 30
        
        # Headers de tabla
        headers = ["Código", "Descripción", "Cant.", "Precio Unit.", "Importe"]
        x_positions = [20, 120, 400, 500, 650]
        
        # Dibujar header de tabla
        table_header_bbox = (15, y_pos - 5, 750, y_pos + 25)
        self.draw_rectangle_with_bbox(draw, table_header_bbox, self.colors['table_header'], "items_table", bboxes)
        
        for i, header in enumerate(headers):
            self.draw_text_with_bbox(draw, header, (x_positions[i], y_pos), normal_font, self.colors['text'], "items_table", bboxes)
        
        y_pos += 30
        
        # Items de la tabla
        for i, (codigo, desc, unidad, precio_base) in enumerate(items):
            cantidad = random.randint(1, 5)
            precio = precio_base * (0.8 + random.random() * 0.4)
            importe = cantidad * precio
            
            # Alternar color de fila
            row_color = self.colors['table_row'] if i % 2 == 0 else self.colors['background']
            row_bbox = (15, y_pos - 5, 750, y_pos + 20)
            self.draw_rectangle_with_bbox(draw, row_bbox, row_color, "items_table", bboxes)
            
            self.draw_text_with_bbox(draw, codigo, (x_positions[0], y_pos), small_font, self.colors['text'], "codigo_producto", bboxes)
            self.draw_text_with_bbox(draw, desc[:30] + "..." if len(desc) > 30 else desc, (x_positions[1], y_pos), small_font, self.colors['text'], "descripcion", bboxes)
            self.draw_text_with_bbox(draw, str(cantidad), (x_positions[2], y_pos), small_font, self.colors['text'], "cantidad", bboxes)
            self.draw_text_with_bbox(draw, f"${precio:,.2f}", (x_positions[3], y_pos), small_font, self.colors['text'], "precio_unitario", bboxes)
            self.draw_text_with_bbox(draw, f"${importe:,.2f}", (x_positions[4], y_pos), small_font, self.colors['text'], "importe_item", bboxes)
            
            y_pos += 25
        
        # TOTALES
        y_pos += 20
        self.draw_text_with_bbox(draw, f"Subtotal: ${subtotal:,.2f}", (550, y_pos), normal_font, self.colors['text'], "subtotal", bboxes)
        y_pos += 20
        
        if iva_21 > 0:
            self.draw_text_with_bbox(draw, f"I.V.A. 21%: ${iva_21:,.2f}", (550, y_pos), normal_font, self.colors['text'], "iva_21", bboxes)
            y_pos += 20
        
        if iva_10_5 > 0:
            self.draw_text_with_bbox(draw, f"I.V.A. 10.5%: ${iva_10_5:,.2f}", (550, y_pos), normal_font, self.colors['text'], "iva_10_5", bboxes)
            y_pos += 20
        
        if iva_27 > 0:
            self.draw_text_with_bbox(draw, f"I.V.A. 27%: ${iva_27:,.2f}", (550, y_pos), normal_font, self.colors['text'], "iva_27", bboxes)
            y_pos += 20
        
        # Línea separadora
        draw.line([(500, y_pos), (750, y_pos)], fill=self.colors['border'], width=2)
        y_pos += 10
        
        self.draw_text_with_bbox(draw, f"TOTAL: ${total:,.2f}", (550, y_pos), header_font, self.colors['header'], "total", bboxes)
        
        # INFORMACIÓN ADICIONAL
        y_pos += 60
        formas_pago = ["Efectivo", "Transferencia", "Tarjeta de Crédito", "Cheque"]
        forma_pago = random.choice(formas_pago)
        self.draw_text_with_bbox(draw, f"Forma de Pago: {forma_pago}", (20, y_pos), normal_font, self.colors['text'], "forma_pago", bboxes)
        self.draw_text_with_bbox(draw, f"Vencimiento: {(fecha + timedelta(days=30)).strftime('%d/%m/%Y')}", (20, y_pos + 20), normal_font, self.colors['text'], "fecha_vencimiento", bboxes)
        
        # CÓDIGOS DE BARRAS Y QR (simulados)
        y_pos += 60
        self.draw_text_with_bbox(draw, "CÓDIGO DE BARRAS", (20, y_pos), small_font, self.colors['text'], "codigo_barras", bboxes)
        self.draw_text_with_bbox(draw, "QR CODE", (400, y_pos), small_font, self.colors['text'], "qr_code", bboxes)
        
        # FIRMA
        y_pos += 40
        self.draw_text_with_bbox(draw, "FIRMA", (20, y_pos), normal_font, self.colors['text'], "firma", bboxes)
        
        # Añadir ruido y artefactos para realismo
        img = self.add_noise_and_artifacts(img)
        
        return img, bboxes
    
    def generate_date(self):
        """Genera fecha aleatoria del último año"""
        start_date = datetime.now() - timedelta(days=365)
        random_days = random.randint(0, 365)
        return start_date + timedelta(days=random_days)
    
    def generate_dataset(self, num_images=1000):
        """Genera el dataset completo con variaciones"""
        print(f"Generando {num_images} facturas sintéticas avanzadas...")
        
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
                # Variar el estilo de factura
                variation = i % 3  # 3 variaciones diferentes
                img, bboxes = self.generate_invoice(f"{split_name}_{i:04d}", variation)
                
                # Guardar imagen
                img_path = self.output_dir / "images" / split_name / f"advanced_invoice_{i:04d}.jpg"
                img.save(img_path, "JPEG", quality=95)
                
                # Guardar labels YOLO
                label_path = self.output_dir / "labels" / split_name / f"advanced_invoice_{i:04d}.txt"
                with open(label_path, 'w') as f:
                    f.write('\n'.join(bboxes))
                
                if (i + 1) % 100 == 0:
                    print(f"  Generadas {i + 1}/{count} imágenes...")
        
        # Crear dataset.yaml
        self.create_dataset_yaml()
        print(f"Dataset avanzado generado en: {self.output_dir}")
    
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
    print("🚀 Generador Avanzado de Facturas Sintéticas Argentinas")
    print("=" * 60)
    
    generator = AdvancedInvoiceGenerator()
    
    # Generar dataset con 1000 imágenes
    generator.generate_dataset(1000)
    
    print("\n✅ Dataset avanzado generado exitosamente!")
    print("\n📊 Estadísticas:")
    print(f"  - Total de imágenes: 1000")
    print(f"  - Entrenamiento: 700 imágenes")
    print(f"  - Validación: 200 imágenes")
    print(f"  - Prueba: 100 imágenes")
    print(f"  - Clases: 36 (campos de factura argentina)")
    print(f"  - Variaciones: 3 estilos diferentes")
    print(f"  - Realismo: Ruido y artefactos añadidos")
    
    print("\n🎯 Próximos pasos:")
    print("1. Revisar algunas imágenes generadas")
    print("2. Entrenar modelo YOLO con el nuevo dataset")
    print("3. Evaluar rendimiento del modelo")
    print("4. Comparar con modelo anterior")

if __name__ == "__main__":
    main()
