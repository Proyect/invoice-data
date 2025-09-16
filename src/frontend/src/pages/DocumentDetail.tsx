import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  Chip,
  Grid,
  Alert,
  CircularProgress,
  Tabs,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Button,
  LinearProgress
} from '@mui/material';
import {
  ArrowBack,
  Download,
  Refresh,
  CheckCircle,
  Error,
  Schedule
} from '@mui/icons-material';
import { useParams, useNavigate } from 'react-router-dom';
import { useDocuments } from '../contexts/DocumentContext';
import { getDocumentTypeLabel, getStatusColor, formatDate } from '../utils/documentUtils';
import toast from 'react-hot-toast';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`document-tabpanel-${index}`}
      aria-labelledby={`document-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const DocumentDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { getDocumentStatus, getExtractedData, getStructuredData, downloadDocument } = useDocuments();
  
  const [documentStatus, setDocumentStatus] = useState<any>(null);
  const [extractedData, setExtractedData] = useState<any>(null);
  const [structuredData, setStructuredData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [tabValue, setTabValue] = useState(0);

  useEffect(() => {
    if (id) {
      loadDocumentData();
    }
  }, [id]);

  const loadDocumentData = async () => {
    if (!id) return;

    try {
      setLoading(true);
      const status = await getDocumentStatus(id);
      setDocumentStatus(status);

      if (status.status === 'COMPLETED') {
        try {
          const extracted = await getExtractedData(id);
          setExtractedData(extracted);
        } catch (error) {
          console.warn('No se pudieron cargar los datos extraídos');
        }

        try {
          const structured = await getStructuredData(id);
          setStructuredData(structured);
        } catch (error) {
          console.warn('No se pudieron cargar los datos estructurados');
        }
      }
    } catch (error) {
      toast.error('Error al cargar los datos del documento');
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await loadDocumentData();
    setRefreshing(false);
    toast.success('Datos actualizados');
  };

  const handleDownload = async () => {
    if (documentStatus) {
      try {
        await downloadDocument(documentStatus.id, documentStatus.original_filename);
        toast.success('Descarga iniciada');
      } catch (error) {
        console.error('Error downloading document:', error);
        toast.error('Error al descargar el documento');
      }
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'COMPLETED':
        return <CheckCircle color="success" />;
      case 'PENDING':
        return <Schedule color="warning" />;
      case 'FAILED':
        return <Error color="error" />;
      default:
        return <Schedule />;
    }
  };

  const renderExtractedData = () => {
    if (!extractedData) {
      return (
        <Alert severity="info">
          No hay datos extraídos disponibles.
        </Alert>
      );
    }

    const entries = Object.entries(extractedData);
    if (entries.length === 0) {
      return (
        <Alert severity="warning">
          No se detectaron campos en el documento.
        </Alert>
      );
    }

    return (
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell><strong>Campo</strong></TableCell>
              <TableCell><strong>Valor</strong></TableCell>
              <TableCell><strong>Confianza</strong></TableCell>
              <TableCell><strong>Posición</strong></TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {entries.map(([field, data]: [string, any]) => (
              <TableRow key={field}>
                <TableCell>
                  <Typography variant="body2" sx={{ textTransform: 'capitalize' }}>
                    {field.replace(/_/g, ' ')}
                  </Typography>
                </TableCell>
                <TableCell>
                  <Typography variant="body2">
                    {data.value || 'N/A'}
                  </Typography>
                </TableCell>
                <TableCell>
                  <Box display="flex" alignItems="center" gap={1}>
                    <LinearProgress
                      variant="determinate"
                      value={(data.confidence || 0) * 100}
                      sx={{ width: 60, height: 8, borderRadius: 4 }}
                    />
                    <Typography variant="caption">
                      {((data.confidence || 0) * 100).toFixed(1)}%
                    </Typography>
                  </Box>
                </TableCell>
                <TableCell>
                  <Typography variant="caption" color="text.secondary">
                    [{data.bbox?.join(', ')}]
                  </Typography>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    );
  };

  const renderStructuredData = () => {
    if (!structuredData) {
      return (
        <Alert severity="info">
          No hay datos estructurados disponibles.
        </Alert>
      );
    }

    return (
      <Box>
        <pre style={{ 
          backgroundColor: '#f5f5f5', 
          padding: '16px', 
          borderRadius: '4px',
          overflow: 'auto',
          fontSize: '14px'
        }}>
          {JSON.stringify(structuredData, null, 2)}
        </pre>
      </Box>
    );
  };

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="50vh">
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  if (!documentStatus) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Alert severity="error">
          No se pudo cargar la información del documento.
        </Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      {/* Header */}
      <Box display="flex" alignItems="center" gap={2} mb={3}>
        <Button
          startIcon={<ArrowBack />}
          onClick={() => navigate('/documents')}
        >
          Volver
        </Button>
        <Typography variant="h4">
          {documentStatus.original_filename}
        </Typography>
        <Box flexGrow={1} />
        <Button
          startIcon={<Refresh />}
          onClick={handleRefresh}
          disabled={refreshing}
        >
          Actualizar
        </Button>
        <Button
          startIcon={<Download />}
          variant="outlined"
          onClick={handleDownload}
        >
          Descargar
        </Button>
      </Box>

      {/* Información del documento */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Typography variant="h6" gutterBottom>
                Información del Documento
              </Typography>
              <Box display="flex" flexDirection="column" gap={1}>
                <Box display="flex" alignItems="center" gap={1}>
                  <Typography variant="body2" color="text.secondary">
                    Estado:
                  </Typography>
                  <Chip
                    icon={getStatusIcon(documentStatus.status)}
                    label={documentStatus.status}
                    color={getStatusColor(documentStatus.status)}
                    size="small"
                  />
                </Box>
                <Typography variant="body2">
                  <strong>Tipo:</strong> {getDocumentTypeLabel(documentStatus.document_type)}
                </Typography>
                <Typography variant="body2">
                  <strong>Subido:</strong> {formatDate(documentStatus.uploaded_at)}
                </Typography>
                {documentStatus.processed_at && (
                  <Typography variant="body2">
                    <strong>Procesado:</strong> {formatDate(documentStatus.processed_at)}
                  </Typography>
                )}
              </Box>
            </Grid>
            <Grid item xs={12} md={6}>
              {documentStatus.processing_error && (
                <Alert severity="error">
                  <Typography variant="subtitle2" gutterBottom>
                    Error de Procesamiento:
                  </Typography>
                  <Typography variant="body2">
                    {documentStatus.processing_error}
                  </Typography>
                </Alert>
              )}
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Tabs con datos */}
      <Card>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={tabValue} onChange={(e, newValue) => setTabValue(newValue)}>
            <Tab label="Datos Extraídos" />
            <Tab label="Datos Estructurados" />
          </Tabs>
        </Box>

        <TabPanel value={tabValue} index={0}>
          <Typography variant="h6" gutterBottom>
            Datos Extraídos por OCR
          </Typography>
          <Typography variant="body2" color="text.secondary" paragraph>
            Información extraída directamente del documento usando YOLO + Tesseract.
          </Typography>
          {renderExtractedData()}
        </TabPanel>

        <TabPanel value={tabValue} index={1}>
          <Typography variant="h6" gutterBottom>
            Datos Estructurados
          </Typography>
          <Typography variant="body2" color="text.secondary" paragraph>
            Datos procesados y estructurados según el tipo de documento.
          </Typography>
          {renderStructuredData()}
        </TabPanel>
      </Card>
    </Container>
  );
};

export default DocumentDetail;

