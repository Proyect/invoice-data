#!/usr/bin/env python3
"""
Preprocesador universal de imágenes para OCR
Maneja cualquier tipo de documento: facturas, DNI, recibos, etc.
"""

import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import logging
from typing import Tuple, Optional, Dict, Any
from pathlib import Path
import json

logger = logging.getLogger(__name__)

class UniversalImagePreprocessor:
    """
    Preprocesador universal que optimiza cualquier imagen para OCR
    """
    
    def __init__(self):
        self.preprocessing_config = {
            'auto_rotate': True,
            'auto_contrast': True,
            'auto_denoise': True,
            'auto_skew_correction': True,
            'auto_perspective_correction': True,
            'enhance_text': True,
            'remove_background': True
        }
    
    def preprocess_image(self, image_path: str, document_type: str = "UNKNOWN") -> Dict[str, Any]:
        """
        Preprocesa una imagen para optimizar el OCR
        
        Args:
            image_path: Ruta a la imagen
            document_type: Tipo de documento (FACTURA, DNI, RECIBO, etc.)
            
        Returns:
            Dict con la imagen procesada y metadatos
        """
        try:
            # Cargar imagen
            original_image = self._load_image(image_path)
            if original_image is None:
                raise ValueError("No se pudo cargar la imagen")
            
            # Detectar tipo de documento si no se especifica
            if document_type == "UNKNOWN":
                document_type = self._detect_document_type(original_image)
            
            # Aplicar preprocesamiento específico según el tipo
            processed_image = self._apply_document_specific_preprocessing(original_image, document_type)
            
            # Aplicar preprocesamiento universal
            processed_image = self._apply_universal_preprocessing(processed_image)
            
            # Validar calidad de la imagen procesada
            quality_score = self._assess_image_quality(processed_image)
            
            return {
                'processed_image': processed_image,
                'original_image': original_image,
                'document_type': document_type,
                'quality_score': quality_score,
                'preprocessing_applied': self._get_applied_preprocessing(),
                'recommendations': self._get_quality_recommendations(quality_score)
            }
            
        except Exception as e:
            logger.error(f"Error preprocesando imagen {image_path}: {e}")
            raise
    
    def _load_image(self, image_path: str) -> Optional[np.ndarray]:
        """Carga una imagen desde archivo"""
        try:
            # Intentar con OpenCV primero
            image = cv2.imread(image_path)
            if image is not None:
                return image
            
            # Si falla, intentar con PIL y convertir
            pil_image = Image.open(image_path)
            if pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')
            
            # Convertir PIL a OpenCV
            image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
            return image
            
        except Exception as e:
            logger.error(f"Error cargando imagen {image_path}: {e}")
            return None
    
    def _detect_document_type(self, image: np.ndarray) -> str:
        """
        Detecta el tipo de documento basado en características visuales
        """
        try:
            # Convertir a escala de grises para análisis
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Detectar características específicas
            features = self._extract_document_features(gray)
            
            # Clasificar basado en características
            if features['has_barcode'] and features['aspect_ratio'] > 1.5:
                return "DNI"
            elif features['has_table_structure'] and features['text_density'] > 0.3:
                return "FACTURA"
            elif features['has_logo'] and features['text_density'] > 0.2:
                return "RECIBO"
            elif features['aspect_ratio'] < 1.2 and features['text_density'] > 0.4:
                return "TARJETA"
            else:
                return "DOCUMENTO_GENERAL"
                
        except Exception as e:
            logger.warning(f"Error detectando tipo de documento: {e}")
            return "DOCUMENTO_GENERAL"
    
    def _extract_document_features(self, gray_image: np.ndarray) -> Dict[str, Any]:
        """Extrae características del documento para clasificación"""
        features = {
            'aspect_ratio': gray_image.shape[1] / gray_image.shape[0],
            'text_density': 0.0,
            'has_barcode': False,
            'has_table_structure': False,
            'has_logo': False,
            'brightness': 0.0,
            'contrast': 0.0
        }
        
        try:
            # Calcular densidad de texto
            edges = cv2.Canny(gray_image, 50, 150)
            text_pixels = np.sum(edges > 0)
            total_pixels = gray_image.shape[0] * gray_image.shape[1]
            features['text_density'] = text_pixels / total_pixels
            
            # Detectar códigos de barras
            features['has_barcode'] = self._detect_barcode(gray_image)
            
            # Detectar estructura de tabla
            features['has_table_structure'] = self._detect_table_structure(gray_image)
            
            # Detectar logo
            features['has_logo'] = self._detect_logo(gray_image)
            
            # Calcular brillo y contraste
            features['brightness'] = np.mean(gray_image)
            features['contrast'] = np.std(gray_image)
            
        except Exception as e:
            logger.warning(f"Error extrayendo características: {e}")
        
        return features
    
    def _detect_barcode(self, gray_image: np.ndarray) -> bool:
        """Detecta si hay códigos de barras en la imagen"""
        try:
            # Detectar líneas horizontales (códigos de barras)
            horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 1))
            horizontal_lines = cv2.morphologyEx(gray_image, cv2.MORPH_OPEN, horizontal_kernel)
            
            # Contar líneas horizontales
            contours, _ = cv2.findContours(horizontal_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            return len(contours) > 5
            
        except:
            return False
    
    def _detect_table_structure(self, gray_image: np.ndarray) -> bool:
        """Detecta si hay estructura de tabla"""
        try:
            # Detectar líneas horizontales y verticales
            horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
            vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))
            
            horizontal_lines = cv2.morphologyEx(gray_image, cv2.MORPH_OPEN, horizontal_kernel)
            vertical_lines = cv2.morphologyEx(gray_image, cv2.MORPH_OPEN, vertical_kernel)
            
            # Contar líneas
            h_contours, _ = cv2.findContours(horizontal_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            v_contours, _ = cv2.findContours(vertical_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            return len(h_contours) > 3 and len(v_contours) > 3
            
        except:
            return False
    
    def _detect_logo(self, gray_image: np.ndarray) -> bool:
        """Detecta si hay un logo en la imagen"""
        try:
            # Buscar regiones con alta densidad de píxeles blancos (logos típicamente)
            _, binary = cv2.threshold(gray_image, 200, 255, cv2.THRESH_BINARY)
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Buscar contornos grandes que podrían ser logos
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 1000:  # Área mínima para considerar logo
                    return True
            
            return False
            
        except:
            return False
    
    def _apply_document_specific_preprocessing(self, image: np.ndarray, document_type: str) -> np.ndarray:
        """Aplica preprocesamiento específico según el tipo de documento"""
        processed = image.copy()
        
        if document_type == "DNI":
            # Para DNI: mejorar contraste y corregir perspectiva
            processed = self._enhance_contrast(processed, factor=1.5)
            processed = self._correct_perspective(processed)
            
        elif document_type == "FACTURA":
            # Para facturas: mejorar texto y estructura de tabla
            processed = self._enhance_text_clarity(processed)
            processed = self._improve_table_structure(processed)
            
        elif document_type == "RECIBO":
            # Para recibos: mejorar legibilidad general
            processed = self._enhance_readability(processed)
            
        return processed
    
    def _apply_universal_preprocessing(self, image: np.ndarray) -> np.ndarray:
        """Aplica preprocesamiento universal a cualquier imagen"""
        processed = image.copy()
        
        # 1. Corrección de rotación automática
        if self.preprocessing_config['auto_rotate']:
            processed = self._auto_rotate(processed)
        
        # 2. Corrección de perspectiva
        if self.preprocessing_config['auto_perspective_correction']:
            processed = self._correct_perspective(processed)
        
        # 3. Mejora de contraste
        if self.preprocessing_config['auto_contrast']:
            processed = self._enhance_contrast(processed)
        
        # 4. Reducción de ruido
        if self.preprocessing_config['auto_denoise']:
            processed = self._denoise(processed)
        
        # 5. Mejora de texto
        if self.preprocessing_config['enhance_text']:
            processed = self._enhance_text_clarity(processed)
        
        # 6. Corrección de sesgo
        if self.preprocessing_config['auto_skew_correction']:
            processed = self._correct_skew(processed)
        
        # 7. Remoción de fondo
        if self.preprocessing_config['remove_background']:
            processed = self._remove_background(processed)
        
        return processed
    
    def _auto_rotate(self, image: np.ndarray) -> np.ndarray:
        """Corrige automáticamente la rotación de la imagen"""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 50, 150, apertureSize=3)
            
            # Detectar líneas
            lines = cv2.HoughLines(edges, 1, np.pi/180, threshold=100)
            
            if lines is not None:
                angles = []
                for line in lines:
                    rho, theta = line[0]
                    angle = theta * 180 / np.pi
                    if -45 <= angle <= 45:
                        angles.append(angle)
                
                if angles:
                    # Calcular ángulo promedio
                    avg_angle = np.median(angles)
                    
                    # Rotar si el ángulo es significativo
                    if abs(avg_angle) > 1:
                        h, w = image.shape[:2]
                        center = (w // 2, h // 2)
                        rotation_matrix = cv2.getRotationMatrix2D(center, avg_angle, 1.0)
                        image = cv2.warpAffine(image, rotation_matrix, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
            
            return image
            
        except Exception as e:
            logger.warning(f"Error en auto-rotación: {e}")
            return image
    
    def _correct_perspective(self, image: np.ndarray) -> np.ndarray:
        """Corrige la perspectiva de la imagen"""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Detectar contornos
            edges = cv2.Canny(gray, 50, 150)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Buscar el contorno más grande (probablemente el documento)
            if contours:
                largest_contour = max(contours, key=cv2.contourArea)
                
                # Aproximar el contorno a un rectángulo
                epsilon = 0.02 * cv2.arcLength(largest_contour, True)
                approx = cv2.approxPolyDP(largest_contour, epsilon, True)
                
                if len(approx) == 4:
                    # Aplicar corrección de perspectiva
                    pts1 = np.float32(approx)
                    h, w = image.shape[:2]
                    pts2 = np.float32([[0, 0], [w, 0], [w, h], [0, h]])
                    
                    matrix = cv2.getPerspectiveTransform(pts1, pts2)
                    image = cv2.warpPerspective(image, matrix, (w, h))
            
            return image
            
        except Exception as e:
            logger.warning(f"Error en corrección de perspectiva: {e}")
            return image
    
    def _enhance_contrast(self, image: np.ndarray, factor: float = 1.2) -> np.ndarray:
        """Mejora el contraste de la imagen"""
        try:
            # Convertir a LAB para mejor control del contraste
            lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            
            # Aplicar CLAHE (Contrast Limited Adaptive Histogram Equalization)
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
            l = clahe.apply(l)
            
            # Reconstruir imagen
            lab = cv2.merge([l, a, b])
            image = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
            
            return image
            
        except Exception as e:
            logger.warning(f"Error mejorando contraste: {e}")
            return image
    
    def _denoise(self, image: np.ndarray) -> np.ndarray:
        """Reduce el ruido de la imagen"""
        try:
            # Aplicar filtro bilateral para reducir ruido manteniendo bordes
            image = cv2.bilateralFilter(image, 9, 75, 75)
            
            # Aplicar filtro de mediana para ruido de sal y pimienta
            image = cv2.medianBlur(image, 3)
            
            return image
            
        except Exception as e:
            logger.warning(f"Error reduciendo ruido: {e}")
            return image
    
    def _enhance_text_clarity(self, image: np.ndarray) -> np.ndarray:
        """Mejora la claridad del texto"""
        try:
            # Convertir a escala de grises
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Aplicar umbralización adaptativa
            binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
            
            # Aplicar morfología para limpiar el texto
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))
            binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
            
            # Convertir de vuelta a BGR
            image = cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)
            
            return image
            
        except Exception as e:
            logger.warning(f"Error mejorando claridad de texto: {e}")
            return image
    
    def _correct_skew(self, image: np.ndarray) -> np.ndarray:
        """Corrige el sesgo (skew) de la imagen"""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Detectar líneas para calcular el ángulo de sesgo
            edges = cv2.Canny(gray, 50, 150, apertureSize=3)
            lines = cv2.HoughLines(edges, 1, np.pi/180, threshold=100)
            
            if lines is not None:
                angles = []
                for line in lines:
                    rho, theta = line[0]
                    angle = theta * 180 / np.pi
                    if -45 <= angle <= 45:
                        angles.append(angle)
                
                if angles:
                    skew_angle = np.median(angles)
                    
                    # Corregir sesgo si es significativo
                    if abs(skew_angle) > 0.5:
                        h, w = image.shape[:2]
                        center = (w // 2, h // 2)
                        rotation_matrix = cv2.getRotationMatrix2D(center, -skew_angle, 1.0)
                        image = cv2.warpAffine(image, rotation_matrix, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
            
            return image
            
        except Exception as e:
            logger.warning(f"Error corrigiendo sesgo: {e}")
            return image
    
    def _remove_background(self, image: np.ndarray) -> np.ndarray:
        """Remueve el fondo de la imagen"""
        try:
            # Convertir a escala de grises
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Aplicar umbralización para separar texto del fondo
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Invertir si es necesario
            if np.mean(binary) > 127:
                binary = cv2.bitwise_not(binary)
            
            # Aplicar morfología para limpiar
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
            binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
            
            # Crear máscara
            mask = cv2.merge([binary, binary, binary])
            
            # Aplicar máscara
            image = cv2.bitwise_and(image, mask)
            
            return image
            
        except Exception as e:
            logger.warning(f"Error removiendo fondo: {e}")
            return image
    
    def _enhance_readability(self, image: np.ndarray) -> np.ndarray:
        """Mejora la legibilidad general de la imagen"""
        try:
            # Mejorar contraste
            image = self._enhance_contrast(image, factor=1.3)
            
            # Reducir ruido
            image = self._denoise(image)
            
            # Mejorar nitidez
            kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
            image = cv2.filter2D(image, -1, kernel)
            
            return image
            
        except Exception as e:
            logger.warning(f"Error mejorando legibilidad: {e}")
            return image
    
    def _improve_table_structure(self, image: np.ndarray) -> np.ndarray:
        """Mejora la estructura de tablas en la imagen"""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Detectar líneas horizontales y verticales
            horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
            vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))
            
            horizontal_lines = cv2.morphologyEx(gray, cv2.MORPH_OPEN, horizontal_kernel)
            vertical_lines = cv2.morphologyEx(gray, cv2.MORPH_OPEN, vertical_kernel)
            
            # Combinar líneas
            table_structure = cv2.addWeighted(horizontal_lines, 0.5, vertical_lines, 0.5, 0.0)
            
            # Aplicar a la imagen original
            image = cv2.addWeighted(image, 0.8, cv2.cvtColor(table_structure, cv2.COLOR_GRAY2BGR), 0.2, 0.0)
            
            return image
            
        except Exception as e:
            logger.warning(f"Error mejorando estructura de tabla: {e}")
            return image
    
    def _assess_image_quality(self, image: np.ndarray) -> float:
        """Evalúa la calidad de la imagen procesada"""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Calcular métricas de calidad
            brightness = np.mean(gray)
            contrast = np.std(gray)
            
            # Detectar bordes (indicador de nitidez)
            edges = cv2.Canny(gray, 50, 150)
            edge_density = np.sum(edges > 0) / (gray.shape[0] * gray.shape[1])
            
            # Calcular score de calidad (0-100)
            quality_score = 0
            
            # Brillo óptimo: 100-200
            if 100 <= brightness <= 200:
                quality_score += 30
            elif 80 <= brightness <= 220:
                quality_score += 20
            else:
                quality_score += 10
            
            # Contraste óptimo: > 50
            if contrast > 50:
                quality_score += 30
            elif contrast > 30:
                quality_score += 20
            else:
                quality_score += 10
            
            # Densidad de bordes (nitidez)
            if edge_density > 0.1:
                quality_score += 40
            elif edge_density > 0.05:
                quality_score += 30
            else:
                quality_score += 20
            
            return min(quality_score, 100)
            
        except Exception as e:
            logger.warning(f"Error evaluando calidad: {e}")
            return 50.0
    
    def _get_applied_preprocessing(self) -> list:
        """Retorna lista de preprocesamientos aplicados"""
        applied = []
        for key, value in self.preprocessing_config.items():
            if value:
                applied.append(key)
        return applied
    
    def _get_quality_recommendations(self, quality_score: float) -> list:
        """Retorna recomendaciones basadas en la calidad de la imagen"""
        recommendations = []
        
        if quality_score < 60:
            recommendations.append("Considerar tomar una nueva foto con mejor iluminación")
            recommendations.append("Asegurar que el documento esté completamente visible")
            recommendations.append("Evitar sombras y reflejos")
        
        if quality_score < 80:
            recommendations.append("Verificar que el documento esté plano y sin arrugas")
            recommendations.append("Usar una resolución más alta si es posible")
        
        if quality_score >= 80:
            recommendations.append("Imagen de buena calidad para OCR")
        
        return recommendations

# Función de conveniencia para uso directo
def preprocess_image_for_ocr(image_path: str, document_type: str = "UNKNOWN") -> np.ndarray:
    """
    Función de conveniencia para preprocesar una imagen
    
    Args:
        image_path: Ruta a la imagen
        document_type: Tipo de documento
        
    Returns:
        Imagen preprocesada como numpy array
    """
    preprocessor = UniversalImagePreprocessor()
    result = preprocessor.preprocess_image(image_path, document_type)
    return result['processed_image']
