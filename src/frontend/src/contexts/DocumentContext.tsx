import React, { createContext, useContext, useState, useEffect, useCallback, useMemo, ReactNode } from 'react';
import { documentService } from '../services/api';
import { Document, DocumentStatus, DocumentType, DocumentUploadResponse } from './../types/document';
import { logRender } from '../utils/debugUtils';

interface DocumentContextType {
  documents: Document[];
  loading: boolean;
  uploadDocument: (file: File, documentType: DocumentType) => Promise<DocumentUploadResponse>;
  getDocumentStatus: (documentId: string) => Promise<DocumentStatus>;
  getExtractedData: (documentId: string) => Promise<any>;
  getStructuredData: (documentId: string) => Promise<any>;
  deleteDocument: (documentId: string) => Promise<void>;
  downloadDocument: (documentId: string, filename: string) => Promise<void>;
  refreshDocuments: () => Promise<void>;
}

const DocumentContext = createContext<DocumentContextType | undefined>(undefined);

export const useDocuments = () => {
  const context = useContext(DocumentContext);
  if (context === undefined) {
    throw new Error('useDocuments must be used within a DocumentProvider');
  }
  return context;
};

interface DocumentProviderProps {
  children: ReactNode;
}

export const DocumentProvider: React.FC<DocumentProviderProps> = ({ children }) => {
  logRender('DocumentProvider');
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(false);
  const [hasLoaded, setHasLoaded] = useState(false);

  // Cargar documentos automáticamente al montar el contexto (solo una vez)
  useEffect(() => {
    if (hasLoaded) return;
    
    const loadInitialDocuments = async () => {
      try {
        console.log('🔄 Cargando documentos iniciales...');
        setLoading(true);
        const response = await documentService.getDocuments();
        console.log('📄 Respuesta del servidor:', response);
        
        const documentsList = response.documents
          .map((doc: any) => ({
            id: doc.id,
            original_filename: doc.original_filename,
            status: doc.status,
            message: '',
            document_type: doc.document_type,
            uploaded_at: doc.uploaded_at,
            processed_at: doc.processed_at,
            processing_error: doc.processing_error
          }))
          .sort((a: Document, b: Document) => new Date(b.uploaded_at).getTime() - new Date(a.uploaded_at).getTime());
        
        console.log('📋 Documentos procesados:', documentsList);
        setDocuments(documentsList);
        setHasLoaded(true);
      } catch (error) {
        console.error('❌ Error loading initial documents:', error);
        if (error && typeof error === 'object' && 'response' in error) {
          console.error('Error details:', (error as any).response?.data);
        }
        setHasLoaded(true);
      } finally {
        setLoading(false);
      }
    };
    
    loadInitialDocuments();
  }, [hasLoaded]);

  const uploadDocument = useCallback(async (file: File, documentType: DocumentType): Promise<DocumentUploadResponse> => {
    try {
      setLoading(true);
      const response = await documentService.uploadDocument(file, documentType);
      
      // Convert DocumentUploadResponse to Document for state management
      const document: Document = {
        id: response.document_id,
        original_filename: response.filename,
        status: response.status,
        message: response.message,
        document_type: documentType,
        uploaded_at: new Date().toISOString(),
        processed_at: undefined,
        processing_error: undefined
      };
      
      setDocuments(prev => [document, ...prev]);
      return response;
    } catch (error) {
      throw error;
    } finally {
      setLoading(false);
    }
  }, []);

  const getDocumentStatus = useCallback(async (documentId: string): Promise<DocumentStatus> => {
    try {
      return await documentService.getDocumentStatus(documentId);
    } catch (error) {
      throw error;
    }
  }, []);

  const getExtractedData = useCallback(async (documentId: string): Promise<any> => {
    try {
      return await documentService.getExtractedData(documentId);
    } catch (error) {
      throw error;
    }
  }, []);

  const getStructuredData = useCallback(async (documentId: string): Promise<any> => {
    try {
      return await documentService.getStructuredData(documentId);
    } catch (error) {
      throw error;
    }
  }, []);

  const deleteDocument = useCallback(async (documentId: string): Promise<void> => {
    try {
      setLoading(true);
      await documentService.deleteDocument(documentId);
      // Remover el documento de la lista local
      setDocuments(prev => prev.filter(doc => doc.id !== documentId));
    } catch (error) {
      throw error;
    } finally {
      setLoading(false);
    }
  }, []);

  const downloadDocument = useCallback(async (documentId: string, filename: string): Promise<void> => {
    try {
      const blob = await documentService.downloadDocument(documentId);
      
      // Crear URL del blob y descargar
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      // Mostrar mensaje de éxito
      console.log(`Descarga iniciada: ${filename}`);
    } catch (error) {
      console.error('Error en downloadDocument:', error);
      throw error;
    }
  }, []);

  const refreshDocuments = useCallback(async (): Promise<void> => {
    try {
      setLoading(true);
      const response = await documentService.getDocuments();
      const documentsList = response.documents
        .map((doc: any) => ({
          id: doc.id,
          original_filename: doc.original_filename,
          status: doc.status,
          message: '',
          document_type: doc.document_type,
          uploaded_at: doc.uploaded_at,
          processed_at: doc.processed_at,
          processing_error: doc.processing_error
        }))
        .sort((a: Document, b: Document) => new Date(b.uploaded_at).getTime() - new Date(a.uploaded_at).getTime());
      setDocuments(documentsList);
    } catch (error) {
      console.error('Error loading documents:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  // Memoizar solo las propiedades que realmente cambian
  // Las funciones ya están memoizadas con useCallback, no necesitan estar en las dependencias
  const value = useMemo(() => ({
    documents,
    loading,
    uploadDocument,
    getDocumentStatus,
    getExtractedData,
    getStructuredData,
    deleteDocument,
    downloadDocument,
    refreshDocuments
  }), [documents, loading]);

  return (
    <DocumentContext.Provider value={value}>
      {children}
    </DocumentContext.Provider>
  );
};

