import React, { useState, useCallback } from 'react';
import {
  Container,
  Paper,
  Typography,
  Box,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  CircularProgress,
  Card,
  CardContent,
  LinearProgress
} from '@mui/material';
import { useDropzone } from 'react-dropzone';
import { useNavigate } from 'react-router-dom';
import { useDocuments } from '../contexts/OptimizedDocumentContext';
import { DocumentType } from '../types/document';
import { getDocumentTypeLabel, formatFileSize } from '../utils/documentUtils';
import toast from 'react-hot-toast';

const DocumentUpload: React.FC = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [documentType, setDocumentType] = useState<DocumentType>(DocumentType.DNI_FRONT);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);

  const { uploadDocument } = useDocuments();
  const navigate = useNavigate();

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (file) {
      setSelectedFile(file);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png', '.tiff', '.bmp'],
      'application/pdf': ['.pdf']
    },
    maxFiles: 1,
    maxSize: 10 * 1024 * 1024 // 10MB
  });

  const handleUpload = async () => {
    if (!selectedFile) {
      toast.error('Por favor selecciona un archivo');
      return;
    }

    try {
      setUploading(true);
      setUploadProgress(0);

      // Simular progreso de subida
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return prev;
          }
          return prev + 10;
        });
      }, 200);

      const response = await uploadDocument(selectedFile, documentType);
      
      clearInterval(progressInterval);
      setUploadProgress(100);
      
      toast.success('Documento subido exitosamente');
      navigate(`/documents/${response.document_id}`);
    } catch (error: any) {
      let errorMessage = 'Error al subir el documento';
      
      if (error.response?.data?.detail) {
        // Si detail es un string, usarlo directamente
        if (typeof error.response.data.detail === 'string') {
          errorMessage = error.response.data.detail;
        } 
        // Si detail es un array de errores (común en FastAPI)
        else if (Array.isArray(error.response.data.detail)) {
          errorMessage = error.response.data.detail.map((err: any) => 
            typeof err === 'string' ? err : err.msg || JSON.stringify(err)
          ).join(', ');
        }
        // Si detail es un objeto, convertirlo a string
        else if (typeof error.response.data.detail === 'object') {
          errorMessage = JSON.stringify(error.response.data.detail);
        }
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      console.error('Error al subir documento:', error);
      toast.error(errorMessage);
    } finally {
      setUploading(false);
      setUploadProgress(0);
    }
  };


  return (
    <Container maxWidth="md" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" gutterBottom>
        Subir Documento
      </Typography>
      <Typography variant="body1" color="text.secondary" paragraph>
        Sube un documento para procesarlo con OCR. Soporta imágenes (JPG, PNG, TIFF, BMP) y PDFs.
      </Typography>

      <Paper elevation={3} sx={{ p: 3 }}>
        {/* Zona de arrastrar y soltar */}
        <Card
          {...getRootProps()}
          sx={{
            p: 4,
            textAlign: 'center',
            cursor: 'pointer',
            border: '2px dashed',
            borderColor: isDragActive ? 'primary.main' : 'grey.300',
            backgroundColor: isDragActive ? 'action.hover' : 'background.paper',
            '&:hover': {
              borderColor: 'primary.main',
              backgroundColor: 'action.hover'
            }
          }}
        >
          <input {...getInputProps()} />
          <CardContent>
            <Typography variant="h6" gutterBottom>
              {isDragActive ? 'Suelta el archivo aquí' : 'Arrastra y suelta un archivo aquí'}
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
              o haz clic para seleccionar un archivo
            </Typography>
            <Typography variant="caption" display="block">
              Formatos soportados: JPG, PNG, TIFF, BMP, PDF
            </Typography>
            <Typography variant="caption" display="block">
              Tamaño máximo: 10MB
            </Typography>
          </CardContent>
        </Card>

        {/* Archivo seleccionado */}
        {selectedFile && (
          <Box sx={{ mt: 3 }}>
            <Alert severity="success" sx={{ mb: 2 }}>
              Archivo seleccionado: {selectedFile.name} ({formatFileSize(selectedFile.size)})
            </Alert>
          </Box>
        )}

        {/* Selector de tipo de documento */}
        <Box sx={{ mt: 3 }}>
          <FormControl fullWidth>
            <InputLabel>Tipo de Documento</InputLabel>
            <Select
              value={documentType}
              label="Tipo de Documento"
              onChange={(e) => setDocumentType(e.target.value as DocumentType)}
              disabled={uploading}
            >
              <MenuItem value={DocumentType.DNI_FRONT}>
                {getDocumentTypeLabel(DocumentType.DNI_FRONT)}
              </MenuItem>
              <MenuItem value={DocumentType.DNI_BACK}>
                {getDocumentTypeLabel(DocumentType.DNI_BACK)}
              </MenuItem>
              <MenuItem value={DocumentType.INVOICE_A}>
                {getDocumentTypeLabel(DocumentType.INVOICE_A)}
              </MenuItem>
              <MenuItem value={DocumentType.INVOICE_B}>
                {getDocumentTypeLabel(DocumentType.INVOICE_B)}
              </MenuItem>
              <MenuItem value={DocumentType.INVOICE_C}>
                {getDocumentTypeLabel(DocumentType.INVOICE_C)}
              </MenuItem>
            </Select>
          </FormControl>
        </Box>

        {/* Barra de progreso */}
        {uploading && (
          <Box sx={{ mt: 3 }}>
            <Typography variant="body2" gutterBottom>
              Subiendo documento...
            </Typography>
            <LinearProgress variant="determinate" value={uploadProgress} />
            <Typography variant="caption" color="text.secondary">
              {uploadProgress}% completado
            </Typography>
          </Box>
        )}

        {/* Botones de acción */}
        <Box sx={{ mt: 3, display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
          <Button
            variant="outlined"
            onClick={() => navigate('/')}
            disabled={uploading}
          >
            Cancelar
          </Button>
          <Button
            variant="contained"
            onClick={handleUpload}
            disabled={!selectedFile || uploading}
            startIcon={uploading ? <CircularProgress size={20} /> : undefined}
          >
            {uploading ? 'Subiendo...' : 'Subir Documento'}
          </Button>
        </Box>
      </Paper>

      {/* Información adicional */}
      <Box sx={{ mt: 3 }}>
        <Alert severity="info">
          <Typography variant="body2">
            <strong>Consejos para mejores resultados:</strong>
          </Typography>
          <Typography variant="body2" component="div">
            • Asegúrate de que el documento esté bien iluminado<br />
            • Evita sombras y reflejos<br />
            • Mantén el documento plano y sin dobleces<br />
            • Para DNI, sube primero el frente y luego el dorso por separado
          </Typography>
        </Alert>
      </Box>
    </Container>
  );
};

export default DocumentUpload;

