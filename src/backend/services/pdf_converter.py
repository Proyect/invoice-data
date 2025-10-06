#!/usr/bin/env python3
"""
Servicio de Conversión PDF a Imagen
==================================

Este servicio convierte archivos PDF a imágenes para procesamiento OCR.
Utiliza pdf2image para una conversión rápida y de alta calidad.

Características:
- Conversión PDF → Imagen
- Múltiples páginas
- Optimización para OCR
- Timeouts configurables
- Manejo de errores robusto
"""

from pdf2image import convert_from_path, convert_from_bytes
from PIL import Image
import cv2
import numpy as np
import logging
import time
from typing import List, Tuple, Optional
from pathlib import Path
import tempfile
import os
import io

logger = logging.getLogger(__name__)

class PDFConverter:
    """Convertidor de PDF a imágenes optimizado para OCR"""
    
    def __init__(self, dpi: int = 200, timeout_seconds: int = 30):
        """
        Inicializa el convertidor PDF
        
        Args:
            dpi: Resolución para la conversión (200 DPI es óptimo para OCR)
            timeout_seconds: Timeout máximo para conversión
        """
        self.dpi = dpi
        self.timeout_seconds = timeout_seconds
        self.conversion_stats = {
            'total_converted': 0,
            'successful': 0,
            'failed': 0,
            'avg_conversion_time': 0.0,
            'total_pages': 0
        }
    
    def convert_pdf_to_images(self, pdf_bytes: bytes, max_pages: int = 5) -> List[np.ndarray]:
        """
        Convierte PDF a lista de imágenes (numpy arrays)
        
        Args:
            pdf_bytes: Contenido del PDF como bytes
            max_pages: Máximo número de páginas a convertir (para optimizar tiempo)
            
        Returns:
            Lista de imágenes como numpy arrays
        """
        start_time = time.time()
        images = []
        
        try:
            logger.info(f"🔄 Convirtiendo PDF a imágenes (DPI: {self.dpi}, max_pages: {max_pages})")
            
            # Convertir PDF a imágenes usando pdf2image
            pil_images = convert_from_bytes(
                pdf_bytes, 
                dpi=self.dpi,
                first_page=1,
                last_page=max_pages,
                fmt='PNG'
            )
            
            total_pages = len(pil_images)
            logger.info(f"📄 PDF convertido a {total_pages} imágenes")
            
            # Convertir PIL Images a numpy arrays
            for page_num, pil_img in enumerate(pil_images):
                try:
                    # Verificar timeout
                    if time.time() - start_time > self.timeout_seconds:
                        logger.warning(f"⏰ Timeout alcanzado, convirtiendo solo {page_num} páginas")
                        break
                    
                    # Convertir PIL a numpy array
                    img_array = np.array(pil_img)
                    
                    # Convertir RGB a BGR para OpenCV
                    if len(img_array.shape) == 3 and img_array.shape[2] == 3:
                        img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
                    
                    if img_array is not None:
                        images.append(img_array)
                        logger.info(f"✅ Página {page_num + 1} convertida: {img_array.shape}")
                    else:
                        logger.warning(f"⚠️ No se pudo convertir página {page_num + 1}")
                    
                except Exception as e:
                    logger.error(f"❌ Error convirtiendo página {page_num + 1}: {e}")
                    continue
            
            # Actualizar estadísticas
            conversion_time = time.time() - start_time
            self._update_stats(len(images), True, conversion_time)
            
            logger.info(f"✅ PDF convertido: {len(images)} imágenes en {conversion_time:.2f}s")
            return images
            
        except Exception as e:
            conversion_time = time.time() - start_time
            self._update_stats(0, False, conversion_time)
            logger.error(f"❌ Error convirtiendo PDF: {e}")
            return []
    
    def convert_pdf_file_to_images(self, pdf_path: str, max_pages: int = 5) -> List[np.ndarray]:
        """
        Convierte archivo PDF a imágenes
        
        Args:
            pdf_path: Ruta al archivo PDF
            max_pages: Máximo número de páginas a convertir
            
        Returns:
            Lista de imágenes como numpy arrays
        """
        try:
            with open(pdf_path, 'rb') as f:
                pdf_bytes = f.read()
            return self.convert_pdf_to_images(pdf_bytes, max_pages)
        except Exception as e:
            logger.error(f"❌ Error leyendo archivo PDF {pdf_path}: {e}")
            return []
    
    def convert_pdf_to_single_image(self, pdf_bytes: bytes, page_number: int = 0) -> Optional[np.ndarray]:
        """
        Convierte una página específica del PDF a imagen
        
        Args:
            pdf_bytes: Contenido del PDF como bytes
            page_number: Número de página (0-indexed)
            
        Returns:
            Imagen como numpy array o None si hay error
        """
        start_time = time.time()
        
        try:
            logger.info(f"🔄 Convirtiendo página {page_number + 1} del PDF")
            
            # Convertir página específica usando pdf2image
            pil_images = convert_from_bytes(
                pdf_bytes, 
                dpi=self.dpi,
                first_page=page_number + 1,  # pdf2image usa 1-indexed
                last_page=page_number + 1,
                fmt='PNG'
            )
            
            if not pil_images:
                logger.error(f"❌ No se pudo convertir página {page_number + 1}")
                return None
            
            # Convertir PIL Image a numpy array
            pil_img = pil_images[0]
            img_array = np.array(pil_img)
            
            # Convertir RGB a BGR para OpenCV
            if len(img_array.shape) == 3 and img_array.shape[2] == 3:
                img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
            
            conversion_time = time.time() - start_time
            
            if img_array is not None:
                logger.info(f"✅ Página {page_number + 1} convertida en {conversion_time:.2f}s: {img_array.shape}")
                return img_array
            else:
                logger.error(f"❌ No se pudo convertir página {page_number + 1}")
                return None
                
        except Exception as e:
            conversion_time = time.time() - start_time
            logger.error(f"❌ Error convirtiendo página {page_number + 1}: {e}")
            return None
    
    def get_pdf_info(self, pdf_bytes: bytes) -> dict:
        """
        Obtiene información del PDF
        
        Args:
            pdf_bytes: Contenido del PDF como bytes
            
        Returns:
            Diccionario con información del PDF
        """
        try:
            # Usar pdf2image para obtener información básica
            pil_images = convert_from_bytes(pdf_bytes, dpi=72, first_page=1, last_page=1)
            
            info = {
                'pages': len(pil_images) if pil_images else 0,
                'metadata': {},  # pdf2image no extrae metadatos fácilmente
                'size_bytes': len(pdf_bytes),
                'title': '',
                'author': '',
                'subject': '',
                'creator': ''
            }
            
            # Intentar obtener más páginas para contar total
            try:
                all_pages = convert_from_bytes(pdf_bytes, dpi=72)
                info['pages'] = len(all_pages)
            except:
                pass  # Si falla, mantener el conteo básico
            
            return info
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo información del PDF: {e}")
            return {
                'pages': 0,
                'metadata': {},
                'size_bytes': len(pdf_bytes),
                'error': str(e)
            }
    
    def optimize_image_for_ocr(self, image: np.ndarray) -> np.ndarray:
        """
        Optimiza imagen convertida del PDF para OCR
        
        Args:
            image: Imagen como numpy array
            
        Returns:
            Imagen optimizada para OCR
        """
        try:
            # Redimensionar si es muy grande (optimizar velocidad)
            height, width = image.shape[:2]
            max_size = 2048  # Máximo 2048px para PDFs (más grande que imágenes normales)
            
            if height > max_size or width > max_size:
                scale = max_size / max(height, width)
                new_width = int(width * scale)
                new_height = int(height * scale)
                image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
                logger.info(f"📐 Imagen redimensionada: {width}x{height} -> {new_width}x{new_height}")
            
            # Mejorar contraste (PDFs suelen tener bajo contraste)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            enhanced = cv2.convertScaleAbs(gray, alpha=1.3, beta=20)
            
            # Convertir de vuelta a BGR
            enhanced_bgr = cv2.cvtColor(enhanced, cv2.COLOR_GRAY2BGR)
            
            logger.info("✨ Imagen optimizada para OCR")
            return enhanced_bgr
            
        except Exception as e:
            logger.error(f"❌ Error optimizando imagen: {e}")
            return image
    
    def _update_stats(self, pages_converted: int, success: bool, conversion_time: float):
        """Actualiza estadísticas de conversión"""
        self.conversion_stats['total_converted'] += 1
        self.conversion_stats['total_pages'] += pages_converted
        
        if success:
            self.conversion_stats['successful'] += 1
            
            # Actualizar promedio de tiempo
            total_time = (self.conversion_stats['avg_conversion_time'] * 
                         (self.conversion_stats['successful'] - 1) + conversion_time)
            self.conversion_stats['avg_conversion_time'] = total_time / self.conversion_stats['successful']
        else:
            self.conversion_stats['failed'] += 1
    
    def get_stats(self) -> dict:
        """Retorna estadísticas de conversión"""
        return self.conversion_stats.copy()


# Instancia global del convertidor
pdf_converter = PDFConverter(dpi=200, timeout_seconds=30)


def convert_pdf_to_images(pdf_bytes: bytes, max_pages: int = 5) -> List[np.ndarray]:
    """
    Función de conveniencia para convertir PDF a imágenes
    """
    return pdf_converter.convert_pdf_to_images(pdf_bytes, max_pages)


def convert_pdf_to_single_image(pdf_bytes: bytes, page_number: int = 0) -> Optional[np.ndarray]:
    """
    Función de conveniencia para convertir una página del PDF
    """
    return pdf_converter.convert_pdf_to_single_image(pdf_bytes, page_number)


def get_pdf_info(pdf_bytes: bytes) -> dict:
    """
    Función de conveniencia para obtener información del PDF
    """
    return pdf_converter.get_pdf_info(pdf_bytes)


if __name__ == "__main__":
    # Test del convertidor
    import sys
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
        print(f"🧪 Probando conversión de PDF: {pdf_path}")
        
        # Obtener información
        with open(pdf_path, 'rb') as f:
            pdf_bytes = f.read()
        
        info = get_pdf_info(pdf_bytes)
        print(f"📄 Información del PDF: {info}")
        
        # Convertir primera página
        image = convert_pdf_to_single_image(pdf_bytes, 0)
        if image is not None:
            print(f"✅ Primera página convertida: {image.shape}")
            
            # Guardar imagen de prueba
            cv2.imwrite("test_pdf_page.png", image)
            print("💾 Imagen guardada como test_pdf_page.png")
        else:
            print("❌ Error convirtiendo PDF")
    else:
        print("Uso: python pdf_converter.py <archivo.pdf>")
