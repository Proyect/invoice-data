export enum DocumentType {
  DNI_FRONT = 'DNI_FRONT',
  DNI_BACK = 'DNI_BACK',
  INVOICE_A = 'INVOICE_A',
  INVOICE_B = 'INVOICE_B',
  INVOICE_C = 'INVOICE_C'
}

export interface Document {
  id: string;
  original_filename: string;
  status: string;
  message?: string;
  document_type: DocumentType;
  uploaded_at: string;
  processed_at?: string;
  processing_error?: string;
}

export interface DocumentStatus {
  id: string;
  original_filename: string;
  status: string;
  document_type: string;
  uploaded_at: string;
  processed_at?: string;
  processing_error?: string;
}

export interface DocumentUploadResponse {
  document_id: string;
  filename: string;
  status: string;
  message: string;
}

export interface ExtractedData {
  [key: string]: {
    value: string;
    confidence: number;
    bbox: number[];
  };
}

export interface StructuredData {
  [key: string]: any;
}

