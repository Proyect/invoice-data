#!/usr/bin/env python3
"""
Generador universal de documentos sintéticos para entrenamiento YOLO
Incluye: Facturas, DNI, Recibos, Tarjetas, Contratos, etc.
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

class UniversalDocumentGenerator:
    def __init__(self, output_dir="datasets/universal_documents"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Crear subdirectorios
        for split in ["train", "val", "test"]:
            (self.output_dir / "images" / split).mkdir(parents=True, exist_ok=True)
            (self.output_dir / "labels" / split).mkdir(parents=True, exist_ok=True)
        
        # Configuración de tipos de documentos
        self.document_types = {
            "FACTURA": {
                "classes": [
                    "numero_factura", "fecha_emision", "proveedor", "cuit_proveedor",
                    "cliente", "cuit_cliente", "condicion_iva", "subtotal", "iva_21",
                    "iva_10_5", "iva_27", "total", "items_table", "codigo_producto",
                    "descripcion", "cantidad", "precio_unitario", "importe_item",
                    "fecha_vencimiento", "forma_pago", "observaciones", "logo",
                    "firma", "codigo_barras", "qr_code", "numero_cae", "fecha_vto_cae",
                    "punto_venta", "tipo_comprobante", "moneda", "tipo_cambio",
                    "importe_neto", "importe_exento", "percepciones", "retenciones", "otros_tributos"
                ],
                "size": (800, 1000),
                "generator": self._generate_invoice
            },
            "DNI": {
                "classes": [
                    "numero_dni", "apellido", "nombre", "sexo", "fecha_nacimiento",
                    "fecha_emision", "fecha_vencimiento", "nacionalidad", "lugar_nacimiento",
                    "domicilio", "foto", "firma", "huella_dactilar", "codigo_barras",
                    "numero_tramite", "ejemplar", "grupo_sanguineo", "donante_organos"
                ],
                "size": (600, 400),
                "generator": self._generate_dni
            },
            "RECIBO": {
                "classes": [
                    "numero_recibo", "fecha", "concepto", "importe", "pagador",
                    "cuit_pagador", "cobrador", "cuit_cobrador", "forma_pago",
                    "observaciones", "firma", "sello", "codigo_barras", "qr_code"
                ],
                "size": (600, 800),
                "generator": self._generate_receipt
            },
            "TARJETA": {
                "classes": [
                    "numero_tarjeta", "nombre_titular", "fecha_vencimiento", "cvv",
                    "banco", "tipo_tarjeta", "logo_banco", "chip", "banda_magnetica",
                    "firma", "codigo_barras", "qr_code"
                ],
                "size": (400, 250),
                "generator": self._generate_card
            },
            "CONTRATO": {
                "classes": [
                    "titulo", "fecha_contrato", "parte_1", "parte_2", "objeto",
                    "clausulas", "fecha_inicio", "fecha_fin", "valor", "moneda",
                    "firma_1", "firma_2", "testigo_1", "testigo_2", "notario",
                    "numero_escritura", "fecha_escritura", "observaciones"
                ],
                "size": (800, 1200),
                "generator": self._generate_contract
            }
        }
        
        # Datos de prueba
        self._init_test_data()
    
    def _init_test_data(self):
        """Inicializa datos de prueba para diferentes tipos de documentos"""
        self.empresas = [
            {"nombre": "TECHNOLOGY SOLUTIONS S.A.", "cuit": "30-12345678-9"},
            {"nombre": "INDUSTRIAS ARGENTINAS S.R.L.", "cuit": "30-87654321-0"},
            {"nombre": "COMERCIAL DEL SUR S.A.", "cuit": "30-11223344-5"},
            {"nombre": "SERVICIOS INTEGRALES S.A.", "cuit": "30-55667788-1"},
            {"nombre": "CONSULTORA PROFESIONAL S.R.L.", "cuit": "30-99887766-2"}
        ]
        
        self.personas = [
            {"nombre": "JUAN CARLOS PEREZ", "dni": "12345678", "cuit": "20-12345678-9"},
            {"nombre": "MARIA ELENA GONZALEZ", "dni": "87654321", "cuit": "27-87654321-0"},
            {"nombre": "CARLOS ALBERTO RODRIGUEZ", "dni": "11223344", "cuit": "20-11223344-5"},
            {"nombre": "ANA MARIA MARTINEZ", "dni": "55667788", "cuit": "27-55667788-1"},
            {"nombre": "LUIS MIGUEL FERNANDEZ", "dni": "99887766", "cuit": "20-99887766-2"}
        ]
        
        self.bancos = [
            {"nombre": "BANCO NACION", "codigo": "011"},
            {"nombre": "BANCO SANTANDER", "codigo": "072"},
            {"nombre": "BANCO GALICIA", "codigo": "007"},
            {"nombre": "BANCO MACRO", "codigo": "285"},
            {"nombre": "BANCO ITAU", "codigo": "259"}
        ]
    
    def generate_universal_dataset(self, total_images=2000):
        """Genera dataset universal con diferentes tipos de documentos"""
        print(f"🚀 Generando dataset universal con {total_images} documentos...")
        
        # Distribución de tipos de documentos
        distribution = {
            "FACTURA": int(total_images * 0.4),      # 40% facturas
            "DNI": int(total_images * 0.2),          # 20% DNI
            "RECIBO": int(total_images * 0.2),       # 20% recibos
            "TARJETA": int(total_images * 0.1),      # 10% tarjetas
            "CONTRATO": int(total_images * 0.1)      # 10% contratos
        }
        
        # Ajustar para que sume exactamente total_images
        remaining = total_images - sum(distribution.values())
        distribution["FACTURA"] += remaining
        
        print(f"📊 Distribución:")
        for doc_type, count in distribution.items():
            print(f"   {doc_type}: {count} documentos")
        
        # Generar documentos por tipo
        all_classes = set()
        for doc_type, count in distribution.items():
            if count > 0:
                print(f"\n📄 Generando {count} documentos de tipo {doc_type}...")
                classes = self._generate_documents_by_type(doc_type, count)
                all_classes.update(classes)
        
        # Crear dataset.yaml con todas las clases
        self._create_universal_dataset_yaml(all_classes)
        
        print(f"\n✅ Dataset universal generado exitosamente!")
        print(f"   Total de imágenes: {total_images}")
        print(f"   Clases únicas: {len(all_classes)}")
        print(f"   Ubicación: {self.output_dir}")
    
    def _generate_documents_by_type(self, doc_type, count):
        """Genera documentos de un tipo específico"""
        config = self.document_types[doc_type]
        classes = config["classes"]
        
        # Distribución train/val/test
        train_count = int(count * 0.7)
        val_count = int(count * 0.2)
        test_count = count - train_count - val_count
        
        splits = [
            ("train", train_count),
            ("val", val_count),
            ("test", test_count)
        ]
        
        for split_name, split_count in splits:
            if split_count > 0:
                print(f"   Generando {split_count} para {split_name}...")
                
                for i in range(split_count):
                    img, bboxes = config["generator"](f"{doc_type}_{split_name}_{i:04d}")
                    
                    # Guardar imagen
                    img_path = self.output_dir / "images" / split_name / f"{doc_type.lower()}_{i:04d}.jpg"
                    img.save(img_path, "JPEG", quality=95)
                    
                    # Guardar labels YOLO
                    label_path = self.output_dir / "labels" / split_name / f"{doc_type.lower()}_{i:04d}.txt"
                    with open(label_path, 'w') as f:
                        f.write('\n'.join(bboxes))
        
        return classes
    
    def _generate_invoice(self, doc_id):
        """Genera una factura sintética"""
        img = Image.new('RGB', (800, 1000), (255, 255, 255))
        draw = ImageDraw.Draw(img)
        
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
        cliente = random.choice(self.personas)
        numero_factura = f"{random.randint(1, 9999):04d}-{random.randint(1, 99999999):08d}"
        fecha = self.generate_date()
        
        y_pos = 20
        
        # Header
        self._draw_text_with_bbox(draw, "FACTURA", (20, y_pos), title_font, (0, 0, 0), "tipo_comprobante", bboxes)
        self._draw_text_with_bbox(draw, f"N°: {numero_factura}", (400, y_pos), header_font, (0, 0, 0), "numero_factura", bboxes)
        self._draw_text_with_bbox(draw, f"Fecha: {fecha.strftime('%d/%m/%Y')}", (400, y_pos + 25), normal_font, (0, 0, 0), "fecha_emision", bboxes)
        
        y_pos += 80
        
        # Empresa
        self._draw_text_with_bbox(draw, empresa["nombre"], (20, y_pos), header_font, (0, 0, 0), "proveedor", bboxes)
        self._draw_text_with_bbox(draw, f"CUIT: {empresa['cuit']}", (20, y_pos + 25), normal_font, (0, 0, 0), "cuit_proveedor", bboxes)
        
        y_pos += 80
        
        # Cliente
        self._draw_text_with_bbox(draw, "CLIENTE:", (20, y_pos), header_font, (0, 0, 0), "cliente", bboxes)
        self._draw_text_with_bbox(draw, cliente["nombre"], (100, y_pos), normal_font, (0, 0, 0), "cliente", bboxes)
        self._draw_text_with_bbox(draw, f"CUIT: {cliente['cuit']}", (100, y_pos + 20), normal_font, (0, 0, 0), "cuit_cliente", bboxes)
        
        y_pos += 100
        
        # Tabla de items
        self._draw_text_with_bbox(draw, "DETALLE", (20, y_pos), header_font, (0, 0, 0), "items_table", bboxes)
        y_pos += 30
        
        # Items
        for i in range(random.randint(2, 5)):
            desc = f"PRODUCTO {i+1}"
            cantidad = random.randint(1, 10)
            precio = random.randint(100, 5000)
            importe = cantidad * precio
            
            self._draw_text_with_bbox(draw, desc, (20, y_pos), small_font, (0, 0, 0), "descripcion", bboxes)
            self._draw_text_with_bbox(draw, str(cantidad), (300, y_pos), small_font, (0, 0, 0), "cantidad", bboxes)
            self._draw_text_with_bbox(draw, f"${precio}", (400, y_pos), small_font, (0, 0, 0), "precio_unitario", bboxes)
            self._draw_text_with_bbox(draw, f"${importe}", (500, y_pos), small_font, (0, 0, 0), "importe_item", bboxes)
            
            y_pos += 25
        
        # Total
        y_pos += 20
        total = random.randint(10000, 100000)
        self._draw_text_with_bbox(draw, f"TOTAL: ${total}", (500, y_pos), header_font, (0, 0, 0), "total", bboxes)
        
        return img, bboxes
    
    def _generate_dni(self, doc_id):
        """Genera un DNI sintético"""
        img = Image.new('RGB', (600, 400), (255, 255, 255))
        draw = ImageDraw.Draw(img)
        
        try:
            title_font = ImageFont.truetype("arial.ttf", 20)
            normal_font = ImageFont.truetype("arial.ttf", 14)
            small_font = ImageFont.truetype("arial.ttf", 12)
        except:
            title_font = ImageFont.load_default()
            normal_font = ImageFont.load_default()
            small_font = ImageFont.load_default()
        
        bboxes = []
        
        # Datos aleatorios
        persona = random.choice(self.personas)
        fecha_nac = self.generate_date()
        fecha_emision = self.generate_date()
        
        # Header
        self._draw_text_with_bbox(draw, "REPUBLICA ARGENTINA", (20, 20), title_font, (0, 0, 0), "nacionalidad", bboxes)
        self._draw_text_with_bbox(draw, "DOCUMENTO NACIONAL DE IDENTIDAD", (20, 45), normal_font, (0, 0, 0), "tipo_comprobante", bboxes)
        
        # Foto (simulada)
        draw.rectangle([450, 80, 550, 180], fill=(200, 200, 200), outline=(0, 0, 0))
        self._draw_text_with_bbox(draw, "FOTO", (470, 120), small_font, (0, 0, 0), "foto", bboxes)
        
        # Datos personales
        y_pos = 100
        self._draw_text_with_bbox(draw, f"APELLIDO: {persona['nombre'].split()[0]}", (20, y_pos), normal_font, (0, 0, 0), "apellido", bboxes)
        y_pos += 25
        self._draw_text_with_bbox(draw, f"NOMBRE: {persona['nombre'].split()[1]}", (20, y_pos), normal_font, (0, 0, 0), "nombre", bboxes)
        y_pos += 25
        self._draw_text_with_bbox(draw, f"DNI: {persona['dni']}", (20, y_pos), normal_font, (0, 0, 0), "numero_dni", bboxes)
        y_pos += 25
        self._draw_text_with_bbox(draw, f"SEXO: {random.choice(['M', 'F'])}", (20, y_pos), normal_font, (0, 0, 0), "sexo", bboxes)
        y_pos += 25
        self._draw_text_with_bbox(draw, f"NACIMIENTO: {fecha_nac.strftime('%d/%m/%Y')}", (20, y_pos), normal_font, (0, 0, 0), "fecha_nacimiento", bboxes)
        y_pos += 25
        self._draw_text_with_bbox(draw, f"EMISION: {fecha_emision.strftime('%d/%m/%Y')}", (20, y_pos), normal_font, (0, 0, 0), "fecha_emision", bboxes)
        
        # Firma
        y_pos += 50
        self._draw_text_with_bbox(draw, "FIRMA:", (20, y_pos), normal_font, (0, 0, 0), "firma", bboxes)
        draw.rectangle([100, y_pos, 300, y_pos + 30], fill=(255, 255, 255), outline=(0, 0, 0))
        
        return img, bboxes
    
    def _generate_receipt(self, doc_id):
        """Genera un recibo sintético"""
        img = Image.new('RGB', (600, 800), (255, 255, 255))
        draw = ImageDraw.Draw(img)
        
        try:
            title_font = ImageFont.truetype("arial.ttf", 20)
            normal_font = ImageFont.truetype("arial.ttf", 14)
            small_font = ImageFont.truetype("arial.ttf", 12)
        except:
            title_font = ImageFont.load_default()
            normal_font = ImageFont.load_default()
            small_font = ImageFont.load_default()
        
        bboxes = []
        
        # Datos aleatorios
        pagador = random.choice(self.personas)
        cobrador = random.choice(self.empresas)
        numero_recibo = f"R-{random.randint(1000, 9999)}"
        fecha = self.generate_date()
        importe = random.randint(1000, 50000)
        
        y_pos = 20
        
        # Header
        self._draw_text_with_bbox(draw, "RECIBO", (20, y_pos), title_font, (0, 0, 0), "tipo_comprobante", bboxes)
        self._draw_text_with_bbox(draw, f"N°: {numero_recibo}", (400, y_pos), normal_font, (0, 0, 0), "numero_recibo", bboxes)
        self._draw_text_with_bbox(draw, f"Fecha: {fecha.strftime('%d/%m/%Y')}", (400, y_pos + 25), normal_font, (0, 0, 0), "fecha", bboxes)
        
        y_pos += 80
        
        # Concepto
        conceptos = ["SERVICIOS PROFESIONALES", "ALQUILER", "SERVICIOS PUBLICOS", "CONSULTORIA", "MANTENIMIENTO"]
        concepto = random.choice(conceptos)
        self._draw_text_with_bbox(draw, f"CONCEPTO: {concepto}", (20, y_pos), normal_font, (0, 0, 0), "concepto", bboxes)
        
        y_pos += 50
        
        # Pagador
        self._draw_text_with_bbox(draw, "PAGADOR:", (20, y_pos), normal_font, (0, 0, 0), "pagador", bboxes)
        self._draw_text_with_bbox(draw, pagador["nombre"], (100, y_pos), normal_font, (0, 0, 0), "pagador", bboxes)
        self._draw_text_with_bbox(draw, f"CUIT: {pagador['cuit']}", (100, y_pos + 25), normal_font, (0, 0, 0), "cuit_pagador", bboxes)
        
        y_pos += 80
        
        # Cobrador
        self._draw_text_with_bbox(draw, "COBRADOR:", (20, y_pos), normal_font, (0, 0, 0), "cobrador", bboxes)
        self._draw_text_with_bbox(draw, cobrador["nombre"], (100, y_pos), normal_font, (0, 0, 0), "cobrador", bboxes)
        self._draw_text_with_bbox(draw, f"CUIT: {cobrador['cuit']}", (100, y_pos + 25), normal_font, (0, 0, 0), "cuit_cobrador", bboxes)
        
        y_pos += 80
        
        # Importe
        self._draw_text_with_bbox(draw, f"IMPORTE: ${importe}", (20, y_pos), title_font, (0, 0, 0), "importe", bboxes)
        
        y_pos += 80
        
        # Forma de pago
        formas_pago = ["EFECTIVO", "TRANSFERENCIA", "CHEQUE", "TARJETA"]
        forma_pago = random.choice(formas_pago)
        self._draw_text_with_bbox(draw, f"FORMA DE PAGO: {forma_pago}", (20, y_pos), normal_font, (0, 0, 0), "forma_pago", bboxes)
        
        # Firma
        y_pos += 100
        self._draw_text_with_bbox(draw, "FIRMA:", (20, y_pos), normal_font, (0, 0, 0), "firma", bboxes)
        draw.rectangle([100, y_pos, 300, y_pos + 30], fill=(255, 255, 255), outline=(0, 0, 0))
        
        return img, bboxes
    
    def _generate_card(self, doc_id):
        """Genera una tarjeta sintética"""
        img = Image.new('RGB', (400, 250), (255, 255, 255))
        draw = ImageDraw.Draw(img)
        
        try:
            title_font = ImageFont.truetype("arial.ttf", 16)
            normal_font = ImageFont.truetype("arial.ttf", 12)
            small_font = ImageFont.truetype("arial.ttf", 10)
        except:
            title_font = ImageFont.load_default()
            normal_font = ImageFont.load_default()
            small_font = ImageFont.load_default()
        
        bboxes = []
        
        # Datos aleatorios
        banco = random.choice(self.bancos)
        persona = random.choice(self.personas)
        numero_tarjeta = f"{random.randint(1000, 9999)} {random.randint(1000, 9999)} {random.randint(1000, 9999)} {random.randint(1000, 9999)}"
        fecha_venc = f"{random.randint(1, 12):02d}/{random.randint(25, 30)}"
        cvv = random.randint(100, 999)
        
        # Fondo de tarjeta
        draw.rectangle([0, 0, 400, 250], fill=(50, 50, 150), outline=(0, 0, 0))
        
        # Logo del banco
        self._draw_text_with_bbox(draw, banco["nombre"], (20, 20), title_font, (255, 255, 255), "logo_banco", bboxes)
        
        # Número de tarjeta
        self._draw_text_with_bbox(draw, numero_tarjeta, (20, 100), normal_font, (255, 255, 255), "numero_tarjeta", bboxes)
        
        # Nombre del titular
        self._draw_text_with_bbox(draw, persona["nombre"], (20, 150), normal_font, (255, 255, 255), "nombre_titular", bboxes)
        
        # Fecha de vencimiento
        self._draw_text_with_bbox(draw, f"VENCE: {fecha_venc}", (20, 180), small_font, (255, 255, 255), "fecha_vencimiento", bboxes)
        
        # CVV
        self._draw_text_with_bbox(draw, f"CVV: {cvv}", (300, 180), small_font, (255, 255, 255), "cvv", bboxes)
        
        # Chip
        draw.rectangle([320, 50, 350, 80], fill=(200, 200, 200), outline=(255, 255, 255))
        self._draw_text_with_bbox(draw, "CHIP", (325, 60), small_font, (0, 0, 0), "chip", bboxes)
        
        return img, bboxes
    
    def _generate_contract(self, doc_id):
        """Genera un contrato sintético"""
        img = Image.new('RGB', (800, 1200), (255, 255, 255))
        draw = ImageDraw.Draw(img)
        
        try:
            title_font = ImageFont.truetype("arial.ttf", 20)
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
        parte1 = random.choice(self.personas)
        parte2 = random.choice(self.empresas)
        fecha_contrato = self.generate_date()
        valor = random.randint(50000, 500000)
        
        y_pos = 20
        
        # Título
        self._draw_text_with_bbox(draw, "CONTRATO DE PRESTACION DE SERVICIOS", (20, y_pos), title_font, (0, 0, 0), "titulo", bboxes)
        
        y_pos += 50
        
        # Fecha
        self._draw_text_with_bbox(draw, f"Fecha: {fecha_contrato.strftime('%d/%m/%Y')}", (20, y_pos), normal_font, (0, 0, 0), "fecha_contrato", bboxes)
        
        y_pos += 50
        
        # Partes
        self._draw_text_with_bbox(draw, "PARTE 1:", (20, y_pos), header_font, (0, 0, 0), "parte_1", bboxes)
        self._draw_text_with_bbox(draw, parte1["nombre"], (100, y_pos), normal_font, (0, 0, 0), "parte_1", bboxes)
        
        y_pos += 30
        
        self._draw_text_with_bbox(draw, "PARTE 2:", (20, y_pos), header_font, (0, 0, 0), "parte_2", bboxes)
        self._draw_text_with_bbox(draw, parte2["nombre"], (100, y_pos), normal_font, (0, 0, 0), "parte_2", bboxes)
        
        y_pos += 50
        
        # Objeto
        self._draw_text_with_bbox(draw, "OBJETO:", (20, y_pos), header_font, (0, 0, 0), "objeto", bboxes)
        self._draw_text_with_bbox(draw, "Prestacion de servicios profesionales de consultoria", (20, y_pos + 25), normal_font, (0, 0, 0), "objeto", bboxes)
        
        y_pos += 80
        
        # Valor
        self._draw_text_with_bbox(draw, f"VALOR: ${valor}", (20, y_pos), header_font, (0, 0, 0), "valor", bboxes)
        
        y_pos += 50
        
        # Fechas
        self._draw_text_with_bbox(draw, f"INICIO: {fecha_contrato.strftime('%d/%m/%Y')}", (20, y_pos), normal_font, (0, 0, 0), "fecha_inicio", bboxes)
        self._draw_text_with_bbox(draw, f"FIN: {(fecha_contrato + timedelta(days=365)).strftime('%d/%m/%Y')}", (300, y_pos), normal_font, (0, 0, 0), "fecha_fin", bboxes)
        
        y_pos += 100
        
        # Firmas
        self._draw_text_with_bbox(draw, "FIRMA PARTE 1:", (20, y_pos), normal_font, (0, 0, 0), "firma_1", bboxes)
        draw.rectangle([150, y_pos, 300, y_pos + 30], fill=(255, 255, 255), outline=(0, 0, 0))
        
        y_pos += 50
        
        self._draw_text_with_bbox(draw, "FIRMA PARTE 2:", (20, y_pos), normal_font, (0, 0, 0), "firma_2", bboxes)
        draw.rectangle([150, y_pos, 300, y_pos + 30], fill=(255, 255, 255), outline=(0, 0, 0))
        
        return img, bboxes
    
    def _draw_text_with_bbox(self, draw, text, position, font, color, class_name, bboxes):
        """Dibuja texto y guarda bounding box para YOLO"""
        x, y = position
        bbox = draw.textbbox((x, y), text, font=font)
        draw.text((x, y), text, font=font, fill=color)
        
        # Convertir a formato YOLO (normalizado)
        img_width, img_height = 800, 1000  # Tamaño base
        x_center = (bbox[0] + bbox[2]) / 2 / img_width
        y_center = (bbox[1] + bbox[3]) / 2 / img_height
        width = (bbox[2] - bbox[0]) / img_width
        height = (bbox[3] - bbox[1]) / img_height
        
        class_id = 0  # Se asignará correctamente en el dataset.yaml
        bboxes.append(f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}")
    
    def generate_date(self):
        """Genera fecha aleatoria del último año"""
        start_date = datetime.now() - timedelta(days=365)
        random_days = random.randint(0, 365)
        return start_date + timedelta(days=random_days)
    
    def _create_universal_dataset_yaml(self, all_classes):
        """Crea el archivo dataset.yaml universal"""
        # Crear mapeo de clases únicas
        unique_classes = sorted(list(all_classes))
        class_mapping = {i: name for i, name in enumerate(unique_classes)}
        
        dataset_yaml = {
            'train': str(self.output_dir / "images" / "train"),
            'val': str(self.output_dir / "images" / "val"),
            'test': str(self.output_dir / "images" / "test"),
            'nc': len(unique_classes),
            'names': class_mapping
        }
        
        yaml_path = self.output_dir / "dataset.yaml"
        with open(yaml_path, 'w') as f:
            yaml.dump(dataset_yaml, f, default_flow_style=False)
        
        print(f"Dataset YAML universal creado: {yaml_path}")
        print(f"Total de clases: {len(unique_classes)}")

def main():
    """Función principal"""
    print("🚀 Generador Universal de Documentos Sintéticos")
    print("=" * 60)
    
    generator = UniversalDocumentGenerator()
    
    # Generar dataset universal con 2000 imágenes
    generator.generate_universal_dataset(2000)
    
    print("\n✅ Dataset universal generado exitosamente!")
    print("\n📊 Estadísticas:")
    print(f"  - Total de imágenes: 2000")
    print(f"  - Tipos de documentos: 5 (Factura, DNI, Recibo, Tarjeta, Contrato)")
    print(f"  - Distribución: 40% Facturas, 20% DNI, 20% Recibos, 10% Tarjetas, 10% Contratos")
    print(f"  - Clases únicas: Múltiples campos por tipo de documento")
    
    print("\n🎯 Próximos pasos:")
    print("1. Entrenar modelo YOLO universal")
    print("2. Probar con documentos reales")
    print("3. Integrar en sistema OCR")

if __name__ == "__main__":
    main()
