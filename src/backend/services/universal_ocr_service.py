#!/usr/bin/env python3
"""
Servicio OCR Universal para procesamiento de cualquier tipo de documento
Integra preprocesamiento inteligente, detección YOLO y extracción de datos
"""

import cv2
import numpy as np
import pytesseract
from PIL import Image
import logging
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import json
import re
from datetime import datetime

from .universal_image_preprocessor import UniversalImagePreprocessor

logger = logging.getLogger(__name__)

class UniversalOCRService:
    """
    Servicio OCR universal que puede procesar cualquier tipo de documento
    """
    
    def __init__(self):
        self.preprocessor = UniversalImagePreprocessor()
        self.yolo_model = None
        self.class_mappings = self._load_class_mappings()
        
        # Configuración de Tesseract optimizada
        self.tesseract_config = {
            'lang': 'spa+eng',  # Español e inglés
            'config': '--oem 3 --psm 6',  # LSTM + PSM 6 para bloques de texto
            'timeout': 30
        }
        
        # Patrones de extracción de datos
        self.extraction_patterns = {
            'cuit': r'\b\d{2}-\d{8}-\d{1}\b',
            'dni': r'\b\d{7,8}\b',
            'fecha': r'\b\d{1,2}/\d{1,2}/\d{2,4}\b',
            'numero_factura': r'\b\d{4}-\d{8}\b',
            'importe': r'\$\s*\d{1,3}(?:\.\d{3})*(?:,\d{2})?',
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'telefono': r'\b\d{2,4}[\s-]?\d{6,8}\b'
        }
    
    def _load_class_mappings(self) -> Dict[str, List[str]]:
        """Carga mapeos de clases para diferentes tipos de documentos"""
        return {
            "FACTURA": [
                "numero_factura", "fecha_emision", "proveedor", "cuit_proveedor",
                "cliente", "cuit_cliente", "condicion_iva", "subtotal", "iva_21",
                "iva_10_5", "iva_27", "total", "items_table", "codigo_producto",
                "descripcion", "cantidad", "precio_unitario", "importe_item",
                "fecha_vencimiento", "forma_pago", "observaciones", "logo",
                "firma", "codigo_barras", "qr_code", "numero_cae", "fecha_vto_cae",
                "punto_venta", "tipo_comprobante", "moneda", "tipo_cambio",
                "importe_neto", "importe_exento", "percepciones", "retenciones", "otros_tributos"
            ],
            "DNI": [
                "numero_dni", "apellido", "nombre", "sexo", "fecha_nacimiento",
                "fecha_emision", "fecha_vencimiento", "nacionalidad", "lugar_nacimiento",
                "domicilio", "foto", "firma", "huella_dactilar", "codigo_barras",
                "numero_tramite", "ejemplar", "grupo_sanguineo", "donante_organos"
            ],
            "RECIBO": [
                "numero_recibo", "fecha", "concepto", "importe", "pagador",
                "cuit_pagador", "cobrador", "cuit_cobrador", "forma_pago",
                "observaciones", "firma", "sello", "codigo_barras", "qr_code"
            ],
            "TARJETA": [
                "numero_tarjeta", "nombre_titular", "fecha_vencimiento", "cvv",
                "banco", "tipo_tarjeta", "logo_banco", "chip", "banda_magnetica",
                "firma", "codigo_barras", "qr_code"
            ],
            "CONTRATO": [
                "titulo", "fecha_contrato", "parte_1", "parte_2", "objeto",
                "clausulas", "fecha_inicio", "fecha_fin", "valor", "moneda",
                "firma_1", "firma_2", "testigo_1", "testigo_2", "notario",
                "numero_escritura", "fecha_escritura", "observaciones"
            ]
        }
    
    def process_document(self, image_path: str, document_type: str = "UNKNOWN") -> Dict[str, Any]:
        """
        Procesa cualquier tipo de documento y extrae datos estructurados
        
        Args:
            image_path: Ruta a la imagen del documento
            document_type: Tipo de documento (opcional, se detecta automáticamente)
            
        Returns:
            Dict con datos extraídos y metadatos
        """
        try:
            logger.info(f"Procesando documento: {image_path}")
            
            # 1. Preprocesar imagen
            preprocessed_result = self.preprocessor.preprocess_image(image_path, document_type)
            processed_image = preprocessed_result['processed_image']
            detected_type = preprocessed_result['document_type']
            quality_score = preprocessed_result['quality_score']
            
            # 2. Detectar campos con YOLO (si está disponible)
            detected_fields = self._detect_fields_with_yolo(processed_image, detected_type)
            
            # 3. Extraer texto con OCR
            ocr_text = self._extract_text_with_ocr(processed_image)
            
            # 4. Extraer datos estructurados
            structured_data = self._extract_structured_data(ocr_text, detected_type, detected_fields)
            
            # 5. Validar y limpiar datos
            validated_data = self._validate_and_clean_data(structured_data, detected_type)
            
            # 6. Calcular confianza general
            confidence_score = self._calculate_confidence(quality_score, detected_fields, validated_data)
            
            return {
                'success': True,
                'document_type': detected_type,
                'quality_score': quality_score,
                'confidence_score': confidence_score,
                'raw_text': ocr_text,
                'structured_data': validated_data,
                'detected_fields': detected_fields,
                'preprocessing_info': preprocessed_result,
                'recommendations': self._get_processing_recommendations(quality_score, confidence_score)
            }
            
        except Exception as e:
            logger.error(f"Error procesando documento {image_path}: {e}")
            return {
                'success': False,
                'error': str(e),
                'document_type': document_type,
                'quality_score': 0,
                'confidence_score': 0,
                'raw_text': '',
                'structured_data': {},
                'detected_fields': [],
                'recommendations': ['Error en el procesamiento. Verificar la imagen.']
            }
    
    def _detect_fields_with_yolo(self, image: np.ndarray, document_type: str) -> List[Dict[str, Any]]:
        """
        Detecta campos en la imagen usando YOLO
        """
        try:
            # TODO: Implementar detección YOLO cuando el modelo esté disponible
            # Por ahora retornar lista vacía
            logger.info(f"Detectando campos YOLO para tipo: {document_type}")
            return []
            
        except Exception as e:
            logger.warning(f"Error en detección YOLO: {e}")
            return []
    
    def _extract_text_with_ocr(self, image: np.ndarray) -> str:
        """
        Extrae texto de la imagen usando Tesseract OCR
        """
        try:
            # Convertir imagen a PIL
            pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            
            # Configurar Tesseract
            custom_config = self.tesseract_config['config']
            
            # Extraer texto
            text = pytesseract.image_to_string(
                pil_image,
                lang=self.tesseract_config['lang'],
                config=custom_config,
                timeout=self.tesseract_config['timeout']
            )
            
            # Limpiar texto
            cleaned_text = self._clean_ocr_text(text)
            
            logger.info(f"Texto extraído: {len(cleaned_text)} caracteres")
            return cleaned_text
            
        except Exception as e:
            logger.error(f"Error en OCR: {e}")
            return ""
    
    def _clean_ocr_text(self, text: str) -> str:
        """
        Limpia el texto extraído por OCR
        """
        # Remover caracteres especiales problemáticos
        text = re.sub(r'[^\w\s@.,$/\-]', ' ', text)
        
        # Normalizar espacios
        text = re.sub(r'\s+', ' ', text)
        
        # Remover líneas vacías excesivas
        text = re.sub(r'\n\s*\n', '\n', text)
        
        return text.strip()
    
    def _extract_structured_data(self, text: str, document_type: str, detected_fields: List[Dict]) -> Dict[str, Any]:
        """
        Extrae datos estructurados del texto usando patrones y reglas
        """
        structured_data = {}
        
        try:
            # Extraer datos usando patrones regex
            for field_name, pattern in self.extraction_patterns.items():
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    structured_data[field_name] = matches[0] if len(matches) == 1 else matches
            
            # Extraer datos específicos por tipo de documento
            if document_type == "FACTURA":
                structured_data.update(self._extract_invoice_data(text))
            elif document_type == "DNI":
                structured_data.update(self._extract_dni_data(text))
            elif document_type == "RECIBO":
                structured_data.update(self._extract_receipt_data(text))
            elif document_type == "TARJETA":
                structured_data.update(self._extract_card_data(text))
            elif document_type == "CONTRATO":
                structured_data.update(self._extract_contract_data(text))
            
            # Extraer datos usando campos detectados por YOLO
            if detected_fields:
                structured_data.update(self._extract_data_from_yolo_fields(text, detected_fields))
            
            logger.info(f"Datos estructurados extraídos: {len(structured_data)} campos")
            return structured_data
            
        except Exception as e:
            logger.error(f"Error extrayendo datos estructurados: {e}")
            return {}
    
    def _extract_invoice_data(self, text: str) -> Dict[str, Any]:
        """Extrae datos específicos de facturas"""
        data = {}
        
        # Buscar número de factura
        factura_match = re.search(r'(?:factura|n[°º]|nro)[\s:]*(\d{4}-\d{8})', text, re.IGNORECASE)
        if factura_match:
            data['numero_factura'] = factura_match.group(1)
        
        # Buscar total
        total_match = re.search(r'total[\s:]*\$?\s*(\d{1,3}(?:\.\d{3})*(?:,\d{2})?)', text, re.IGNORECASE)
        if total_match:
            data['total'] = total_match.group(1)
        
        # Buscar CUIT del proveedor
        cuit_match = re.search(r'cuit[\s:]*(\d{2}-\d{8}-\d{1})', text, re.IGNORECASE)
        if cuit_match:
            data['cuit_proveedor'] = cuit_match.group(1)
        
        return data
    
    def _extract_dni_data(self, text: str) -> Dict[str, Any]:
        """Extrae datos específicos de DNI"""
        data = {}
        
        # Buscar número de DNI
        dni_match = re.search(r'dni[\s:]*(\d{7,8})', text, re.IGNORECASE)
        if dni_match:
            data['numero_dni'] = dni_match.group(1)
        
        # Buscar apellido y nombre
        nombre_match = re.search(r'apellido[\s:]*([A-ZÁÉÍÓÚÑ\s]+)', text, re.IGNORECASE)
        if nombre_match:
            data['apellido'] = nombre_match.group(1).strip()
        
        return data
    
    def _extract_receipt_data(self, text: str) -> Dict[str, Any]:
        """Extrae datos específicos de recibos"""
        data = {}
        
        # Buscar número de recibo
        recibo_match = re.search(r'recibo[\s:]*(\d+)', text, re.IGNORECASE)
        if recibo_match:
            data['numero_recibo'] = recibo_match.group(1)
        
        # Buscar concepto
        concepto_match = re.search(r'concepto[\s:]*([A-ZÁÉÍÓÚÑ\s]+)', text, re.IGNORECASE)
        if concepto_match:
            data['concepto'] = concepto_match.group(1).strip()
        
        return data
    
    def _extract_card_data(self, text: str) -> Dict[str, Any]:
        """Extrae datos específicos de tarjetas"""
        data = {}
        
        # Buscar número de tarjeta
        tarjeta_match = re.search(r'(\d{4}\s\d{4}\s\d{4}\s\d{4})', text)
        if tarjeta_match:
            data['numero_tarjeta'] = tarjeta_match.group(1)
        
        # Buscar fecha de vencimiento
        venc_match = re.search(r'(\d{2}/\d{2})', text)
        if venc_match:
            data['fecha_vencimiento'] = venc_match.group(1)
        
        return data
    
    def _extract_contract_data(self, text: str) -> Dict[str, Any]:
        """Extrae datos específicos de contratos"""
        data = {}
        
        # Buscar fecha de contrato
        fecha_match = re.search(r'fecha[\s:]*(\d{1,2}/\d{1,2}/\d{2,4})', text, re.IGNORECASE)
        if fecha_match:
            data['fecha_contrato'] = fecha_match.group(1)
        
        # Buscar valor
        valor_match = re.search(r'valor[\s:]*\$?\s*(\d{1,3}(?:\.\d{3})*(?:,\d{2})?)', text, re.IGNORECASE)
        if valor_match:
            data['valor'] = valor_match.group(1)
        
        return data
    
    def _extract_data_from_yolo_fields(self, text: str, detected_fields: List[Dict]) -> Dict[str, Any]:
        """Extrae datos usando campos detectados por YOLO"""
        data = {}
        
        for field in detected_fields:
            field_name = field.get('class_name', '')
            bbox = field.get('bbox', [])
            
            if bbox and field_name:
                # Extraer texto de la región detectada
                # TODO: Implementar extracción de texto por región
                pass
        
        return data
    
    def _validate_and_clean_data(self, data: Dict[str, Any], document_type: str) -> Dict[str, Any]:
        """
        Valida y limpia los datos extraídos
        """
        cleaned_data = {}
        
        for key, value in data.items():
            if isinstance(value, str):
                # Limpiar strings
                cleaned_value = value.strip()
                if cleaned_value:
                    cleaned_data[key] = cleaned_value
            elif isinstance(value, list):
                # Limpiar listas
                cleaned_list = [str(item).strip() for item in value if str(item).strip()]
                if cleaned_list:
                    cleaned_data[key] = cleaned_list[0] if len(cleaned_list) == 1 else cleaned_list
            else:
                cleaned_data[key] = value
        
        return cleaned_data
    
    def _calculate_confidence(self, quality_score: float, detected_fields: List[Dict], structured_data: Dict[str, Any]) -> float:
        """
        Calcula la confianza general del procesamiento
        """
        try:
            # Factor de calidad de imagen (0-40 puntos)
            quality_factor = (quality_score / 100) * 40
            
            # Factor de campos detectados (0-30 puntos)
            fields_factor = min(len(detected_fields) * 2, 30)
            
            # Factor de datos extraídos (0-30 puntos)
            data_factor = min(len(structured_data) * 3, 30)
            
            confidence = quality_factor + fields_factor + data_factor
            return min(confidence, 100)
            
        except Exception as e:
            logger.warning(f"Error calculando confianza: {e}")
            return 50.0
    
    def _get_processing_recommendations(self, quality_score: float, confidence_score: float) -> List[str]:
        """
        Genera recomendaciones basadas en la calidad del procesamiento
        """
        recommendations = []
        
        if quality_score < 60:
            recommendations.append("La calidad de la imagen es baja. Considerar tomar una nueva foto.")
            recommendations.append("Asegurar buena iluminación y que el documento esté completamente visible.")
        
        if confidence_score < 70:
            recommendations.append("La confianza en la extracción es media. Revisar los datos extraídos.")
            recommendations.append("Considerar procesar la imagen con mejor resolución.")
        
        if confidence_score >= 80:
            recommendations.append("Procesamiento exitoso con alta confianza.")
        
        return recommendations

# Función de conveniencia para uso directo
def process_any_document(image_path: str, document_type: str = "UNKNOWN") -> Dict[str, Any]:
    """
    Función de conveniencia para procesar cualquier documento
    
    Args:
        image_path: Ruta a la imagen
        document_type: Tipo de documento (opcional)
        
    Returns:
        Dict con datos extraídos
    """
    ocr_service = UniversalOCRService()
    return ocr_service.process_document(image_path, document_type)

