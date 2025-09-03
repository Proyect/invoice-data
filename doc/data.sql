-- Tabla para almacenar los documentos originales (imágenes/PDFs)
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    original_filename VARCHAR(255) NOT NULL,
    storage_path VARCHAR(512) NOT NULL, -- Ruta al archivo en S3/MinIO
    mime_type VARCHAR(100) NOT NULL,
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed_at TIMESTAMP WITH TIME ZONE,
    status VARCHAR(50) NOT NULL DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED', 'REVIEW_NEEDED')),
    document_type VARCHAR(100) NOT NULL, -- Ej: 'DNI_FRONT', 'DNI_BACK', 'INVOICE_A', 'INVOICE_B', 'INVOICE_C'
    processing_error TEXT, -- Para registrar errores de OCR
    -- Otros campos como ID de usuario que subió el documento, etc.
);

-- Tabla para almacenar datos extraídos de DNI
CREATE TABLE extracted_dni_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    apellido VARCHAR(255),
    nombre VARCHAR(255),
    dni_numero VARCHAR(20),
    fecha_nacimiento DATE,
    nacionalidad VARCHAR(100),
    sexo CHAR(1),
    numero_tramite VARCHAR(50),
    -- Campo para almacenar el JSON crudo del resultado del OCR si lo necesitamos
    raw_ocr_output JSONB,
    extracted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabla maestra para items de facturas (si los detalles de items se repiten mucho)
-- Opcional, pero útil para normalizar descripciones comunes
-- CREATE TABLE invoice_items_master (
--     id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
--     description VARCHAR(255) UNIQUE NOT NULL
-- );

-- Tabla para almacenar datos extraídos de Facturas
CREATE TABLE extracted_invoice_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    tipo_comprobante VARCHAR(50), -- Ej: 'FACTURA_A', 'FACTURA_B'
    punto_venta VARCHAR(10),
    numero_factura VARCHAR(20),
    fecha_emision DATE,
    cuit_emisor VARCHAR(20),
    razon_social_emisor VARCHAR(255),
    domicilio_emisor TEXT,
    cuit_receptor VARCHAR(20),
    razon_social_receptor VARCHAR(255),
    condicion_iva_emisor VARCHAR(100),
    condicion_iva_receptor VARCHAR(100),
    subtotal NUMERIC(15, 2),
    total_iva NUMERIC(15, 2), -- Suma de todos los IVAs
    total_final NUMERIC(15, 2) NOT NULL,
    moneda VARCHAR(5) DEFAULT 'ARS',
    raw_ocr_output JSONB, -- Almacena el JSON crudo del OCR
    extracted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabla para los ítems individuales de una factura
CREATE TABLE invoice_line_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    invoice_data_id UUID NOT NULL REFERENCES extracted_invoice_data(id) ON DELETE CASCADE,
    description TEXT,
    quantity NUMERIC(10, 2),
    unit_price NUMERIC(15, 2),
    subtotal_item NUMERIC(15, 2),
    iva_rate NUMERIC(5, 2), -- Ej: 21.00, 10.50
    iva_amount NUMERIC(15, 2)
);

-- Tabla para almacenar los campos "flexibles" o metadatos de campos no estándar
-- Útil si tienes muchos documentos diferentes con campos no comunes,
-- o para registrar qué campos fueron confirmados por un humano.
CREATE TABLE extracted_fields_metadata (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    field_name VARCHAR(100) NOT NULL,
    field_value TEXT,
    confidence NUMERIC(5, 2), -- Confianza del OCR en este campo
    is_confirmed BOOLEAN DEFAULT FALSE, -- Si un humano validó el campo
    extracted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);