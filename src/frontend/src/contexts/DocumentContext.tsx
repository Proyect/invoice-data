import React, { createContext, useContext, useState, useEffect, useCallback, useMemo, ReactNode } from 'react';
import { documentService } from '../services/api';
import { Document, DocumentStatus, DocumentType, DocumentUploadResponse } from './../types/document';
import { useAuth } from './SimpleAuthContext';

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
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(false);
  const { user, token } = useAuth();

  // Cargar documentos solo cuando el usuario esté autenticado
  useEffect(() => {
    let isMounted = true;
    
    const loadDocuments = async () => {
      // ✅ Solo cargar si hay usuario autenticado y token
      if (!user || !token) {
        console.log('Usuario no autenticado, saltando carga de documentos');
        return;
      }
      
      try {
        setLoading(true);
        console.log('Cargando documentos iniciales...');
        const response = await documentService.getDocuments();
        
        if (isMounted) {
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
        }
      } catch (error: any) {
        console.error('Error loading initial documents:', error);
        console.error('Error details:', error.response?.data);
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };
    
    loadDocuments();
    
    return () => {
      isMounted = false;
    };
  }, [user, token]); // ✅ Ejecutar cuando cambie la autenticación

  const uploadDocument = useCallback(async (file: File, documentType: DocumentType): Promise<DocumentUploadResponse> => {
    setLoading(true);
    try {
      const response = await documentService.uploadDocument(file, documentType);
      
      const newDocument: Document = {
        id: response.document_id,
        original_filename: response.filename,
        status: response.status,
        message: response.message,
        document_type: documentType,
        uploaded_at: new Date().toISOString(),
        processed_at: undefined,
        processing_error: undefined
      };
      
      setDocuments(prev => [newDocument, ...prev]);
      return response;
    } finally {
      setLoading(false);
    }
  }, []);

  const getDocumentStatus = useCallback(async (documentId: string): Promise<DocumentStatus> => {
    return await documentService.getDocumentStatus(documentId);
  }, []);

  const getExtractedData = useCallback(async (documentId: string): Promise<any> => {
    return await documentService.getExtractedData(documentId);
  }, []);

  const getStructuredData = useCallback(async (documentId: string): Promise<any> => {
    return await documentService.getStructuredData(documentId);
  }, []);

  const deleteDocument = useCallback(async (documentId: string): Promise<void> => {
    setLoading(true);
    try {
      await documentService.deleteDocument(documentId);
      setDocuments(prev => prev.filter(doc => doc.id !== documentId));
    } finally {
      setLoading(false);
    }
  }, []);

  const downloadDocument = useCallback(async (documentId: string, filename: string): Promise<void> => {
    const blob = await documentService.downloadDocument(documentId);
    
    if (!blob || blob.size === 0) {
      throw new Error('El archivo descargado está vacío o corrupto');
    }
    
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.style.display = 'none';
    
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    setTimeout(() => {
      window.URL.revokeObjectURL(url);
    }, 100);
  }, []);

  const refreshDocuments = useCallback(async (): Promise<void> => {
    // ✅ Solo refrescar si hay usuario autenticado
    if (!user || !token) {
      console.log('Usuario no autenticado, saltando refresh de documentos');
      return;
    }
    
    setLoading(true);
    try {
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
      console.error('Error refreshing documents:', error);
    } finally {
      setLoading(false);
    }
  }, [user, token]); // ✅ Dependencias de autenticación

  // Crear valor del contexto de forma estable usando useMemo
  const contextValue = useMemo(() => ({
    documents,
    loading,
    uploadDocument,
    getDocumentStatus,
    getExtractedData,
    getStructuredData,
    deleteDocument,
    downloadDocument,
    refreshDocuments
  }), [
    documents,
    loading,
    uploadDocument,
    getDocumentStatus,
    getExtractedData,
    getStructuredData,
    deleteDocument,
    downloadDocument,
    refreshDocuments
  ]);

  return (
    <DocumentContext.Provider value={contextValue}>
      {children}
    </DocumentContext.Provider>
  );
};