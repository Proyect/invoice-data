import { DocumentType } from '../types/document';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';

export type StatusColor = 'success' | 'warning' | 'error' | 'default';

export const getDocumentTypeLabel = (type: DocumentType | string): string => {
  switch (type) {
    case DocumentType.DNI_FRONT:
    case 'DNI_FRONT':
      return 'DNI Frente';
    case DocumentType.DNI_BACK:
    case 'DNI_BACK':
      return 'DNI Dorso';
    case DocumentType.INVOICE_A:
    case 'INVOICE_A':
      return 'Factura A';
    case DocumentType.INVOICE_B:
    case 'INVOICE_B':
      return 'Factura B';
    case DocumentType.INVOICE_C:
    case 'INVOICE_C':
      return 'Factura C';
    default:
      return String(type);
  }
};

export const getStatusColor = (status: string): StatusColor => {
  switch (status) {
    case 'COMPLETED':
      return 'success';
    case 'PENDING':
      return 'warning';
    case 'FAILED':
      return 'error';
    default:
      return 'default';
  }
};

export const getStatusLabel = (status: string): string => {
  switch (status) {
    case 'COMPLETED':
      return 'Completado';
    case 'PENDING':
      return 'Pendiente';
    case 'FAILED':
      return 'Fallido';
    default:
      return status;
  }
};

export const formatDate = (dateString: string): string => {
  try {
    return format(new Date(dateString), 'dd/MM/yyyy HH:mm', { locale: es });
  } catch {
    return dateString;
  }
};

export const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

