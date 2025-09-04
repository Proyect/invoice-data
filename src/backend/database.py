# ocr_api/database.py (fragmento, asumiendo lo demás ya está)

from sqlalchemy import create_engine, Column, String, DateTime, Text, Boolean, UUID, Numeric, Date, Enum as SQLEnum, func
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.types import JSON

import uuid
from datetime import datetime
from typing import Optional
from src.backend.models.documents import DocumentType # Importar el Enum para la columna

from src.backend.config import DATABASE_URL

# Configuración de la base de datos
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependencia para obtener la sesión de la DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Definición del modelo Document
class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    original_filename = Column(String(255), nullable=False)
    storage_path = Column(String(512), nullable=False) # Ruta relativa al archivo
    mime_type = Column(String(100), nullable=False)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True))
    status = Column(String(50), nullable=False, default='PENDING')
    document_type = Column(SQLEnum(DocumentType, name='document_type_enum'), nullable=False)
    processing_error = Column(Text)
    raw_ocr_output = Column(JSON) # Campo para almacenar la salida JSON de YOLO+OCR
    user_id = Column(UUID(as_uuid=True), nullable=True) # ID del usuario que subió el documento

    # Relaciones con datos extraídos, etc. (se pueden añadir más tarde)

    def __repr__(self):
        return f"<Document(id={self.id}, status='{self.status}')>"

# Modelos para ExtractedDniData y ExtractedInvoiceData - implementación básica
class ExtractedDniData(Base):
    __tablename__ = "extracted_dni_data"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), nullable=False)
    apellido = Column(String(100))
    nombre = Column(String(100))
    numero_dni = Column(String(20))
    fecha_nacimiento = Column(Date)
    fecha_emision = Column(Date)
    fecha_vencimiento = Column(Date)
    domicilio = Column(String(200))
    lugar_nacimiento = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<ExtractedDniData(document_id={self.document_id})>"

class ExtractedInvoiceData(Base):
    __tablename__ = "extracted_invoice_data"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), nullable=False)
    numero_factura = Column(String(50))
    fecha_emision = Column(Date)
    fecha_vencimiento = Column(Date)
    cuit_emisor = Column(String(20))
    razon_social_emisor = Column(String(200))
    cuit_receptor = Column(String(20))
    razon_social_receptor = Column(String(200))
    subtotal = Column(Numeric(10, 2))
    iva = Column(Numeric(10, 2))
    total = Column(Numeric(10, 2))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<ExtractedInvoiceData(document_id={self.document_id})>"

# Modelos de usuario para autenticación (si no está en otro archivo como auth_models.py)
class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=True)
    full_name = Column(String(100), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    disabled = Column(Boolean, default=False)

    def __repr__(self):
        return f"<User(username='{self.username}')>"


# Al inicio de tu aplicación (ej. en main.py o un script de inicialización)
# Llama a este para crear las tablas si no existen
def create_db_and_tables():
    Base.metadata.create_all(bind=engine)