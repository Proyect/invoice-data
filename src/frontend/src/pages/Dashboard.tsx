import React, { /*useEffect, useState,*/ useMemo } from 'react';
import {
  Container,
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider
} from '@mui/material';
import {
  Upload,
  DocumentScanner,
  CheckCircle,
  Error,
  Schedule
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useDocuments } from '../contexts/DocumentContext';
//import { DocumentType } from '../types/document';
import { getDocumentTypeLabel, getStatusColor } from '../utils/documentUtils';
import { logRender } from '../utils/debugUtils';

const Dashboard: React.FC = () => {
  logRender('Dashboard');
  const navigate = useNavigate();
  const { documents, loading } = useDocuments();

  // Calcular estadísticas usando useMemo para evitar re-renders innecesarios
  const stats = useMemo(() => {
    const total = documents.length;
    const completed = documents.filter(doc => doc.status === 'COMPLETED').length;
    const pending = documents.filter(doc => doc.status === 'PENDING').length;
    const failed = documents.filter(doc => doc.status === 'FAILED').length;

    return { total, completed, pending, failed };
  }, [documents]);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'COMPLETED':
        return <CheckCircle />;
      case 'PENDING':
        return <Schedule />;
      case 'FAILED':
        return <Error />;
      default:
        return <DocumentScanner />;
    }
  };

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
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>
      <Typography variant="body1" color="text.secondary" paragraph>
        Bienvenido al sistema de procesamiento de documentos OCR. Aquí puedes ver el estado de tus documentos y acceder a las funciones principales.
      </Typography>

      {/* Estadísticas */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <DocumentScanner color="primary" sx={{ mr: 2 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Total Documentos
                  </Typography>
                  <Typography variant="h4">
                    {stats.total}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <CheckCircle color="success" sx={{ mr: 2 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Completados
                  </Typography>
                  <Typography variant="h4">
                    {stats.completed}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <Schedule color="warning" sx={{ mr: 2 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Pendientes
                  </Typography>
                  <Typography variant="h4">
                    {stats.pending}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <Error color="error" sx={{ mr: 2 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Fallidos
                  </Typography>
                  <Typography variant="h4">
                    {stats.failed}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {/* Acciones rápidas */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Acciones Rápidas
              </Typography>
              <List>
                <ListItem 
                  button 
                  onClick={() => navigate('/upload')}
                  sx={{ borderRadius: 1, mb: 1 }}
                >
                  <ListItemIcon>
                    <Upload color="primary" />
                  </ListItemIcon>
                  <ListItemText 
                    primary="Subir Nuevo Documento"
                    secondary="Procesar DNI o factura con OCR"
                  />
                </ListItem>
                <ListItem 
                  button 
                  onClick={() => navigate('/documents')}
                  sx={{ borderRadius: 1 }}
                >
                  <ListItemIcon>
                    <DocumentScanner color="primary" />
                  </ListItemIcon>
                  <ListItemText 
                    primary="Ver Todos los Documentos"
                    secondary="Gestionar documentos existentes"
                  />
                </ListItem>
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* Documentos recientes */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Documentos Recientes
              </Typography>
              {documents.length === 0 ? (
                <Typography color="text.secondary" align="center" sx={{ py: 2 }}>
                  No hay documentos aún
                </Typography>
              ) : (
                <List>
                  {documents.slice(0, 5).map((doc, index) => (
                    <React.Fragment key={doc.id}>
                      <ListItem 
                        button 
                        onClick={() => navigate(`/documents/${doc.id}`)}
                        sx={{ borderRadius: 1, mb: 1 }}
                      >
                        <ListItemIcon>
                          {getStatusIcon(doc.status)}
                        </ListItemIcon>
                        <ListItemText 
                          primary={doc.original_filename}
                          secondary={
                            <Box>
                              <Typography variant="body2" color="text.secondary">
                                {getDocumentTypeLabel(doc.document_type)}
                              </Typography>
                              <Chip 
                                label={doc.status} 
                                color={getStatusColor(doc.status)}
                                size="small"
                                sx={{ mt: 0.5 }}
                              />
                            </Box>
                          }
                        />
                      </ListItem>
                      {index < Math.min(documents.length, 5) - 1 && <Divider />}
                    </React.Fragment>
                  ))}
                </List>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Container>
  );
};

export default Dashboard;

