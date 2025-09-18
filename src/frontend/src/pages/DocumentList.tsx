import React, { useState, useEffect, useMemo } from 'react';
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  Chip,
  IconButton,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
  TextField,
  InputAdornment,
  FormControl,
  InputLabel,
  Select,
  Grid,
  Pagination,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  Button
} from '@mui/material';
import {
  MoreVert,
  Visibility,
  Download,
  Delete,
  Search,
  FilterList
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useDocuments } from '../contexts/DocumentContext';
import { DocumentType } from '../types/document';
import { getDocumentTypeLabel, getStatusColor, getStatusLabel, formatDate } from '../utils/documentUtils';
import RenderCounter from '../components/RenderCounter';
import NotificationToast from '../components/NotificationToast';

const DocumentList: React.FC = () => {
  const navigate = useNavigate();
  const { documents, loading, deleteDocument, downloadDocument } = useDocuments();
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [typeFilter, setTypeFilter] = useState('ALL');
  const [page, setPage] = useState(1);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [selectedDocument, setSelectedDocument] = useState<string | null>(null);
  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false);
  const [documentToDelete, setDocumentToDelete] = useState<string | null>(null);
  
  // Estados para notificaciones
  const [notification, setNotification] = useState({
    open: false,
    message: '',
    severity: 'success' as 'success' | 'error' | 'warning' | 'info'
  });

  const itemsPerPage = 10;

  // Filtrar documentos usando useMemo para evitar re-renders innecesarios
  const filteredDocuments = useMemo(() => {
    let filtered = documents;

    // Filtrar por término de búsqueda
    if (searchTerm) {
      filtered = filtered.filter(doc =>
        doc.original_filename.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Filtrar por estado
    if (statusFilter !== 'ALL') {
      filtered = filtered.filter(doc => doc.status === statusFilter);
    }

    // Filtrar por tipo
    if (typeFilter !== 'ALL') {
      filtered = filtered.filter(doc => doc.document_type === typeFilter);
    }

    return filtered;
  }, [documents, searchTerm, statusFilter, typeFilter]);

  // Reset page when filters change
  useEffect(() => {
    setPage(1);
  }, [searchTerm, statusFilter, typeFilter]);

  const handleMenuClick = (event: React.MouseEvent<HTMLElement>, documentId: string) => {
    setAnchorEl(event.currentTarget);
    setSelectedDocument(documentId);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    setSelectedDocument(null);
  };

  const handleViewDocument = () => {
    if (selectedDocument) {
      navigate(`/documents/${selectedDocument}`);
    }
    handleMenuClose();
  };

  const handleDeleteDocument = () => {
    if (selectedDocument) {
      setDocumentToDelete(selectedDocument);
      setDeleteConfirmOpen(true);
    }
    handleMenuClose();
  };

  const handleDownloadDocument = async () => {
    if (selectedDocument) {
      try {
        const document = documents.find(doc => doc.id === selectedDocument);
        if (document) {
          await downloadDocument(selectedDocument, document.original_filename);
          setNotification({
            open: true,
            message: `Archivo "${document.original_filename}" descargado exitosamente`,
            severity: 'success'
          });
        }
      } catch (error: any) {
        console.error('Error downloading document:', error);
        setNotification({
          open: true,
          message: error.message || 'Error al descargar el documento',
          severity: 'error'
        });
      }
    }
    handleMenuClose();
  };

  const confirmDelete = async () => {
    if (documentToDelete) {
      try {
        await deleteDocument(documentToDelete);
        setDeleteConfirmOpen(false);
        setDocumentToDelete(null);
        // Los documentos se actualizan automáticamente por el contexto
      } catch (error) {
        console.error('Error deleting document:', error);
        // Aquí podrías mostrar un mensaje de error al usuario
      }
    }
  };

  const cancelDelete = () => {
    setDeleteConfirmOpen(false);
    setDocumentToDelete(null);
  };

  const handleCloseNotification = () => {
    setNotification(prev => ({ ...prev, open: false }));
  };


  const totalPages = Math.ceil(filteredDocuments.length / itemsPerPage);
  const startIndex = (page - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const currentDocuments = filteredDocuments.slice(startIndex, endIndex);

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="50vh">
          <Typography>Cargando documentos...</Typography>
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <RenderCounter componentName="DocumentList" />
      <Typography variant="h4" gutterBottom>
        Documentos
      </Typography>
      <Typography variant="body1" color="text.secondary" paragraph>
        Gestiona todos tus documentos procesados con OCR.
      </Typography>

      {/* Filtros y búsqueda */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                placeholder="Buscar por nombre de archivo..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <Search />
                    </InputAdornment>
                  ),
                }}
              />
            </Grid>
            <Grid item xs={12} md={3}>
              <FormControl fullWidth>
                <InputLabel>Estado</InputLabel>
                <Select
                  value={statusFilter}
                  label="Estado"
                  onChange={(e) => setStatusFilter(e.target.value)}
                >
                  <MenuItem value="ALL">Todos</MenuItem>
                  <MenuItem value="COMPLETED">Completado</MenuItem>
                  <MenuItem value="PENDING">Pendiente</MenuItem>
                  <MenuItem value="FAILED">Fallido</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={3}>
              <FormControl fullWidth>
                <InputLabel>Tipo</InputLabel>
                <Select
                  value={typeFilter}
                  label="Tipo"
                  onChange={(e) => setTypeFilter(e.target.value)}
                >
                  <MenuItem value="ALL">Todos</MenuItem>
                  <MenuItem value={DocumentType.DNI_FRONT}>DNI Frente</MenuItem>
                  <MenuItem value={DocumentType.DNI_BACK}>DNI Dorso</MenuItem>
                  <MenuItem value={DocumentType.INVOICE_A}>Factura A</MenuItem>
                  <MenuItem value={DocumentType.INVOICE_B}>Factura B</MenuItem>
                  <MenuItem value={DocumentType.INVOICE_C}>Factura C</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={2}>
              <Box display="flex" alignItems="center" gap={1}>
                <FilterList color="action" />
                <Typography variant="body2" color="text.secondary">
                  {filteredDocuments.length} documentos
                </Typography>
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Lista de documentos */}
      {currentDocuments.length === 0 ? (
        <Alert severity="info">
          {documents.length === 0 
            ? 'No hay documentos aún. Sube tu primer documento para comenzar.'
            : 'No se encontraron documentos con los filtros aplicados.'
          }
        </Alert>
      ) : (
        <>
          {currentDocuments.map((document) => (
            <Card key={document.id} sx={{ mb: 2 }}>
              <CardContent>
                <Box display="flex" justifyContent="space-between" alignItems="center">
                  <Box flexGrow={1}>
                    <Typography variant="h6" gutterBottom>
                      {document.original_filename}
                    </Typography>
                    <Box display="flex" gap={1} alignItems="center" flexWrap="wrap">
                      <Chip
                        label={getStatusLabel(document.status)}
                        color={getStatusColor(document.status)}
                        size="small"
                      />
                      <Chip
                        label={getDocumentTypeLabel(document.document_type)}
                        variant="outlined"
                        size="small"
                      />
                      <Typography variant="body2" color="text.secondary">
                        Subido: {formatDate(document.uploaded_at)}
                      </Typography>
                      {document.processed_at && (
                        <Typography variant="body2" color="text.secondary">
                          Procesado: {formatDate(document.processed_at)}
                        </Typography>
                      )}
                    </Box>
                    {document.processing_error && (
                      <Alert severity="error" sx={{ mt: 1 }}>
                        Error: {document.processing_error}
                      </Alert>
                    )}
                  </Box>
                  <IconButton
                    onClick={(e) => handleMenuClick(e, document.id)}
                    aria-label="más opciones"
                  >
                    <MoreVert />
                  </IconButton>
                </Box>
              </CardContent>
            </Card>
          ))}

          {/* Paginación */}
          {totalPages > 1 && (
            <Box display="flex" justifyContent="center" mt={3}>
              <Pagination
                count={totalPages}
                page={page}
                onChange={(e, value) => setPage(value)}
                color="primary"
              />
            </Box>
          )}
        </>
      )}

      {/* Menú contextual */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
      >
        <MenuItem onClick={handleViewDocument}>
          <ListItemIcon>
            <Visibility fontSize="small" />
          </ListItemIcon>
          <ListItemText>Ver Detalles</ListItemText>
        </MenuItem>
        <MenuItem onClick={handleDownloadDocument}>
          <ListItemIcon>
            <Download fontSize="small" />
          </ListItemIcon>
          <ListItemText>Descargar</ListItemText>
        </MenuItem>
        <MenuItem onClick={handleDeleteDocument}>
          <ListItemIcon>
            <Delete fontSize="small" />
          </ListItemIcon>
          <ListItemText>Eliminar</ListItemText>
        </MenuItem>
      </Menu>

      {/* Diálogo de confirmación de eliminación */}
      <Dialog
        open={deleteConfirmOpen}
        onClose={cancelDelete}
        aria-labelledby="delete-dialog-title"
        aria-describedby="delete-dialog-description"
      >
        <DialogTitle id="delete-dialog-title">
          Confirmar eliminación
        </DialogTitle>
        <DialogContent>
          <DialogContentText id="delete-dialog-description">
            ¿Estás seguro de que quieres eliminar este documento? Esta acción no se puede deshacer.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={cancelDelete} color="primary">
            Cancelar
          </Button>
          <Button onClick={confirmDelete} color="error" variant="contained">
            Eliminar
          </Button>
        </DialogActions>
      </Dialog>

      {/* Notificación Toast */}
      <NotificationToast
        open={notification.open}
        message={notification.message}
        severity={notification.severity}
        onClose={handleCloseNotification}
      />
    </Container>
  );
};

export default DocumentList;

