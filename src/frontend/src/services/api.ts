import axios, { AxiosInstance, AxiosResponse } from 'axios';
import { LoginCredentials, TokenResponse } from '../types/auth';
import { DocumentType, DocumentUploadResponse, DocumentStatus, ExtractedData, StructuredData } from '../types/document';

class ApiService {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1',
      timeout: 30000,
    });

    // Interceptor para agregar el token de autenticación
    this.api.interceptors.request.use((config) => {
      const token = localStorage.getItem('token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    // Interceptor para manejar errores de respuesta
    this.api.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          localStorage.removeItem('token');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  // Servicios de autenticación
  async login(credentials: LoginCredentials): Promise<TokenResponse> {
    try {
      const params = new URLSearchParams();
      params.append('username', credentials.username);
      params.append('password', credentials.password);

      console.log('Enviando petición de login a:', this.api.defaults.baseURL + '/token');
      
      const response: AxiosResponse<TokenResponse> = await this.api.post('/token', params, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      });
      
      console.log('Respuesta completa del servidor:', response);
      console.log('Datos de la respuesta:', response.data);
      
      return response.data;
    } catch (error: any) {
      console.error('Error en la petición de login:', error);
      console.error('Respuesta del error:', error.response?.data);
      throw error;
    }
  }

  // Servicios de documentos
  async uploadDocument(file: File, documentType: DocumentType): Promise<DocumentUploadResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const response: AxiosResponse<DocumentUploadResponse> = await this.api.post(
      `/documents/upload?document_type=${documentType}`, 
      formData, 
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  }

  async getDocumentStatus(documentId: string): Promise<DocumentStatus> {
    const response: AxiosResponse<DocumentStatus> = await this.api.get(`/documents/${documentId}/status`);
    return response.data;
  }

  async getExtractedData(documentId: string): Promise<ExtractedData> {
    const response: AxiosResponse<ExtractedData> = await this.api.get(`/documents/${documentId}/extracted_data`);
    return response.data;
  }

  async getStructuredData(documentId: string): Promise<StructuredData> {
    const response: AxiosResponse<StructuredData> = await this.api.get(`/documents/${documentId}/structured_data`);
    return response.data;
  }

  async deleteDocument(documentId: string): Promise<void> {
    await this.api.delete(`/documents/${documentId}`);
  }

  async getDocuments(): Promise<any> {
    const response = await this.api.get('/documents/');
    return response.data;
  }

  async downloadDocument(documentId: string): Promise<Blob> {
    console.log(`Iniciando descarga del documento: ${documentId}`);
    try {
      const response = await this.api.get(`/documents/${documentId}/download`, {
        responseType: 'blob',
        timeout: 60000 // 60 segundos para descargas
      });
      
      console.log(`Descarga exitosa, tamaño del blob: ${response.data.size} bytes`);
      
      // Verificar que el blob no esté vacío
      if (!response.data || response.data.size === 0) {
        throw new Error('El archivo descargado está vacío');
      }
      
      return response.data;
    } catch (error: any) {
      console.error('Error en downloadDocument:', error);
      console.error('Response status:', error.response?.status);
      console.error('Response data:', error.response?.data);
      
      // Mejorar el mensaje de error
      if (error.response?.status === 404) {
        throw new Error('El archivo no fue encontrado en el servidor');
      } else if (error.response?.status === 403) {
        throw new Error('No tienes permisos para descargar este archivo');
      } else if (error.response?.status === 500) {
        throw new Error('Error interno del servidor al descargar el archivo');
      } else if (error.code === 'ECONNABORTED') {
        throw new Error('La descarga tardó demasiado tiempo');
      } else if (error.message) {
        throw new Error(error.message);
      } else {
        throw new Error('Error desconocido al descargar el archivo');
      }
    }
  }
}

export const authService = new ApiService();
export const documentService = new ApiService();

