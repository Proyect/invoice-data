from enum import Enum

class DocumentType(str, Enum):
    """Enum para tipos de documento soportados"""
    DNI_FRONT = "DNI_FRONT"
    DNI_BACK = "DNI_BACK"
    INVOICE_A = "INVOICE_A"
    INVOICE_B = "INVOICE_B"
    INVOICE_C = "INVOICE_C"
