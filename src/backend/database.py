# ocr_api/database.py (fragmento, asumiendo lo demás ya está)

from sqlalchemy import create_engine, Column, String, DateTime, Text, Boolean, UUID, Numeric, Date, Enum as SQLEnum
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.dialects.postgresql import JSONB # Importar para JSONB
import uuid
from datetime import datetime
from typing import Optional
from models.documents import DocumentType # Importar el Enum para la columna

from config import DATABASE_URL

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
    uploaded_at = Column(DateTime(timezone=True), default=datetime.now)
    processed_at = Column(DateTime(timezone=True))
    status = Column(String(50), nullable=False, default='PENDING')
    document_type = Column(SQLEnum(DocumentType, name='document_type_enum'), nullable=False)
    processing_error = Column(Text)
    raw_ocr_output = Column(JSONB) # Campo para almacenar la salida JSON de YOLO+OCR
    user_id = Column(UUID(as_uuid=True), nullable=True) # ID del usuario que subió el documento

    # Relaciones con datos extraídos, etc. (se pueden añadir más tarde)

    def __repr__(self):
        return f"<Document(id={self.id}, status='{self.status}')>"

# Modelos para ExtractedDniData y ExtractedInvoiceData, si los tienes definidos
class ExtractedDniData(Base):
     __tablename__ = "extracted_dni_data"
     # ... tus columnas ...

class ExtractedInvoiceData(Base):
     __tablename__ = "extracted_invoice_data"
#     # ... tus columnas ...

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