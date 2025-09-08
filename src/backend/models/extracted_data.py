from pydantic import BaseModel, Field, validator
from datetime import datetime, date
from typing import Optional, Dict, Any, List
from decimal import Decimal
import uuid

# Modelos base para datos extraídos
class ExtractedFieldBase(BaseModel):
    """Modelo base para campos extraídos con metadata"""
    value: str
    confidence: float = Field(ge=0.0, le=1.0, description="Confianza de la detección YOLO (0-1)")
    bbox: List[int] = Field(description="Bounding box [x1, y1, x2, y2]")
    
    model_config = {"from_attributes": True}

class ExtractedTextField(ExtractedFieldBase):
    """Campo de texto extraído"""
    processed_value: Optional[str] = None  # Valor después de procesamiento/validación
    
class ExtractedDateField(ExtractedFieldBase):
    """Campo de fecha extraído"""
    parsed_date: Optional[date] = None
    date_format: Optional[str] = None
    
    @validator('parsed_date', pre=True, always=True)
    def parse_date_from_value(cls, v, values):
        if v is not None:
            return v
        
        # Intentar parsear la fecha del valor extraído
        value = values.get('value', '')
        if value:
            # Formatos comunes de fecha en documentos argentinos
            date_formats = [
                '%d/%m/%Y', '%d-%m-%Y', '%d.%m.%Y',
                '%d/%m/%y', '%d-%m-%y', '%d.%m.%y'
            ]
            
            for fmt in date_formats:
                try:
                    parsed = datetime.strptime(value.strip(), fmt).date()
                    values['date_format'] = fmt
                    return parsed
                except ValueError:
                    continue
        return None

class ExtractedNumberField(ExtractedFieldBase):
    """Campo numérico extraído"""
    parsed_number: Optional[str] = None
    is_valid: bool = False
    
    @validator('parsed_number', pre=True, always=True)
    def clean_number(cls, v, values):
        if v is not None:
            return v
            
        value = values.get('value', '')
        if value:
            # Limpiar número (remover espacios, puntos de miles, etc.)
            cleaned = value.replace(' ', '').replace('.', '').replace(',', '.')
            # Validar que sea un número
            try:
                float(cleaned)
                values['is_valid'] = True
                return cleaned
            except ValueError:
                values['is_valid'] = False
        return value

class ExtractedAmountField(ExtractedFieldBase):
    """Campo de monto/dinero extraído"""
    parsed_amount: Optional[Decimal] = None
    currency: Optional[str] = None
    
    @validator('parsed_amount', pre=True, always=True)
    def parse_amount(cls, v, values):
        if v is not None:
            return v
            
        value = values.get('value', '')
        if value:
            # Detectar moneda
            if '$' in value:
                values['currency'] = 'ARS'
            elif 'USD' in value or 'US$' in value:
                values['currency'] = 'USD'
            
            # Limpiar y parsear monto
            cleaned = value.replace('$', '').replace('USD', '').replace('US$', '')
            cleaned = cleaned.replace(' ', '').replace('.', '').replace(',', '.')
            
            try:
                return Decimal(cleaned)
            except (ValueError, TypeError, ArithmeticError):
                pass
        return None

# Modelos específicos para DNI
class ExtractedDniData(BaseModel):
    """Datos extraídos de un DNI"""
    document_id: uuid.UUID
    
    # Campos del DNI
    apellido: Optional[ExtractedTextField] = None
    nombre: Optional[ExtractedTextField] = None
    numero_dni: Optional[ExtractedNumberField] = None
    fecha_nacimiento: Optional[ExtractedDateField] = None
    fecha_emision: Optional[ExtractedDateField] = None
    fecha_vencimiento: Optional[ExtractedDateField] = None
    domicilio: Optional[ExtractedTextField] = None
    lugar_nacimiento: Optional[ExtractedTextField] = None
    
    # Metadata
    extraction_timestamp: datetime = Field(default_factory=datetime.now)
    processing_quality: Optional[str] = None  # 'high', 'medium', 'low'
    
    model_config = {"from_attributes": True}
    
    def get_summary(self) -> Dict[str, Any]:
        """Retorna un resumen de los datos extraídos"""
        return {
            "nombre_completo": f"{self.apellido.value if self.apellido else ''}, {self.nombre.value if self.nombre else ''}".strip(', '),
            "dni": self.numero_dni.parsed_number if self.numero_dni and self.numero_dni.is_valid else None,
            "fecha_nacimiento": self.fecha_nacimiento.parsed_date if self.fecha_nacimiento else None,
            "domicilio": self.domicilio.value if self.domicilio else None,
            "calidad_extraccion": self.processing_quality
        }

# Modelos específicos para Facturas
class ExtractedInvoiceData(BaseModel):
    """Datos extraídos de una factura"""
    document_id: uuid.UUID
    
    # Información básica de la factura
    numero_factura: Optional[ExtractedTextField] = None
    tipo_factura: Optional[ExtractedTextField] = None  # A, B, C
    fecha_emision: Optional[ExtractedDateField] = None
    fecha_vencimiento: Optional[ExtractedDateField] = None
    
    # Emisor
    cuit_emisor: Optional[ExtractedNumberField] = None
    razon_social_emisor: Optional[ExtractedTextField] = None
    domicilio_emisor: Optional[ExtractedTextField] = None
    
    # Receptor
    cuit_receptor: Optional[ExtractedNumberField] = None
    razon_social_receptor: Optional[ExtractedTextField] = None
    domicilio_receptor: Optional[ExtractedTextField] = None
    
    # Montos
    subtotal: Optional[ExtractedAmountField] = None
    iva_21: Optional[ExtractedAmountField] = None
    iva_105: Optional[ExtractedAmountField] = None
    otros_impuestos: Optional[ExtractedAmountField] = None
    total: Optional[ExtractedAmountField] = None
    
    # Items de la factura (si se detectan)
    items: Optional[List[Dict[str, Any]]] = None
    
    # Metadata
    extraction_timestamp: datetime = Field(default_factory=datetime.now)
    processing_quality: Optional[str] = None
    
    model_config = {"from_attributes": True}
    
    def get_summary(self) -> Dict[str, Any]:
        """Retorna un resumen de los datos extraídos"""
        return {
            "numero": self.numero_factura.value if self.numero_factura else None,
            "tipo": self.tipo_factura.value if self.tipo_factura else None,
            "fecha": self.fecha_emision.parsed_date if self.fecha_emision else None,
            "emisor": self.razon_social_emisor.value if self.razon_social_emisor else None,
            "cuit_emisor": self.cuit_emisor.parsed_number if self.cuit_emisor and self.cuit_emisor.is_valid else None,
            "total": float(self.total.parsed_amount) if self.total and self.total.parsed_amount else None,
            "moneda": self.total.currency if self.total else None,
            "calidad_extraccion": self.processing_quality
        }

# Modelo genérico para respuestas de datos extraídos
class ExtractedDataResponse(BaseModel):
    """Respuesta genérica para datos extraídos"""
    document_id: uuid.UUID
    document_type: str
    extraction_status: str  # 'completed', 'partial', 'failed'
    data: Dict[str, Any]  # Datos específicos según el tipo
    metadata: Dict[str, Any] = {}
    
    model_config = {"from_attributes": True}

# Funciones de utilidad para conversión
def raw_ocr_to_dni_data(document_id: uuid.UUID, raw_data: Dict[str, Any]) -> ExtractedDniData:
    """Convierte datos raw de OCR a ExtractedDniData"""
    dni_data = ExtractedDniData(document_id=document_id)
    
    # Mapear campos detectados por YOLO
    field_mapping = {
        'dni_apellido': 'apellido',
        'dni_nombre': 'nombre', 
        'dni_numero': 'numero_dni',
        'dni_fecha_nacimiento': 'fecha_nacimiento',
        'dni_fecha_emision': 'fecha_emision',
        'dni_fecha_vencimiento': 'fecha_vencimiento',
        'dni_domicilio': 'domicilio',
        'dni_lugar_nacimiento': 'lugar_nacimiento'
    }
    
    for yolo_field, model_field in field_mapping.items():
        if yolo_field in raw_data:
            field_data = raw_data[yolo_field]
            
            if model_field in ['fecha_nacimiento', 'fecha_emision', 'fecha_vencimiento']:
                setattr(dni_data, model_field, ExtractedDateField(**field_data))
            elif model_field == 'numero_dni':
                setattr(dni_data, model_field, ExtractedNumberField(**field_data))
            else:
                setattr(dni_data, model_field, ExtractedTextField(**field_data))
    
    return dni_data

def raw_ocr_to_invoice_data(document_id: uuid.UUID, raw_data: Dict[str, Any]) -> ExtractedInvoiceData:
    """Convierte datos raw de OCR a ExtractedInvoiceData"""
    invoice_data = ExtractedInvoiceData(document_id=document_id)
    
    # Mapear campos detectados por YOLO
    field_mapping = {
        'factura_numero': 'numero_factura',
        'factura_tipo': 'tipo_factura',
        'factura_fecha_emision': 'fecha_emision',
        'factura_fecha_vencimiento': 'fecha_vencimiento',
        'emisor_cuit': 'cuit_emisor',
        'emisor_razon_social': 'razon_social_emisor',
        'emisor_domicilio': 'domicilio_emisor',
        'receptor_cuit': 'cuit_receptor',
        'receptor_razon_social': 'razon_social_receptor',
        'receptor_domicilio': 'domicilio_receptor',
        'subtotal': 'subtotal',
        'iva_21': 'iva_21',
        'iva_105': 'iva_105',
        'total': 'total'
    }
    
    for yolo_field, model_field in field_mapping.items():
        if yolo_field in raw_data:
            field_data = raw_data[yolo_field]
            
            if model_field in ['fecha_emision', 'fecha_vencimiento']:
                setattr(invoice_data, model_field, ExtractedDateField(**field_data))
            elif model_field in ['cuit_emisor', 'cuit_receptor']:
                setattr(invoice_data, model_field, ExtractedNumberField(**field_data))
            elif model_field in ['subtotal', 'iva_21', 'iva_105', 'total']:
                setattr(invoice_data, model_field, ExtractedAmountField(**field_data))
            else:
                setattr(invoice_data, model_field, ExtractedTextField(**field_data))
    
    return invoice_data