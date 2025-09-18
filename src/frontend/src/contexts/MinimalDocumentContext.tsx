import React, { createContext, useContext, useState, useCallback, useMemo, ReactNode } from 'react';
import { Document, DocumentType, DocumentUploadResponse } from './../types/document';

interface DocumentContextType {
  documents: Document[];
  loading: boolean;
  uploadDocument: (file: File, documentType: DocumentType) => Promise<DocumentUploadResponse>;
  getDocumentStatus: (documentId: string) => Promise<any>;
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

  const uploadDocument = useCallback(async (file: File, documentType: DocumentType): Promise<DocumentUploadResponse> => {
    setLoading(true);
    try {
      // Simular upload
      const response: DocumentUploadResponse = {
        document_id: 'test-id',
        filename: file.name,
        status: 'PENDING',
        message: 'Document uploaded'
      };
      
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

  const getDocumentStatus = useCallback(async (documentId: string): Promise<any> => {
    console.log('getDocumentStatus called with:', documentId);
    return { status: 'COMPLETED', message: 'Mock status' };
  }, []);

  const getExtractedData = useCallback(async (documentId: string): Promise<any> => {
    console.log('getExtractedData called with:', documentId);
    return { extracted_data: 'Mock extracted data' };
  }, []);

  const getStructuredData = useCallback(async (documentId: string): Promise<any> => {
    console.log('getStructuredData called with:', documentId);
    return { structured_data: 'Mock structured data' };
  }, []);

  const deleteDocument = useCallback(async (documentId: string): Promise<void> => {
    setLoading(true);
    try {
      setDocuments(prev => prev.filter(doc => doc.id !== documentId));
    } finally {
      setLoading(false);
    }
  }, []);

  const downloadDocument = useCallback(async (documentId: string, filename: string): Promise<void> => {
    console.log('downloadDocument called with:', documentId, filename);
    // Simular descarga
    const blob = new Blob(['Mock file content'], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.style.display = 'none';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  }, []);

  const refreshDocuments = useCallback(async (): Promise<void> => {
    console.log('refreshDocuments called');
    // No hacer nada en el contexto minimalista
  }, []);

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
  }), [documents, loading, uploadDocument, getDocumentStatus, getExtractedData, getStructuredData, deleteDocument, downloadDocument, refreshDocuments]);

  return (
    <DocumentContext.Provider value={contextValue}>
      {children}
    </DocumentContext.Provider>
  );
};
