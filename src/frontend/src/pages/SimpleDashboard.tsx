import React from 'react';
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  Button
} from '@mui/material';
import { useNavigate } from 'react-router-dom';

const SimpleDashboard: React.FC = () => {
  const navigate = useNavigate();

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" gutterBottom>
        Dashboard Simple
      </Typography>
      <Typography variant="body1" color="text.secondary" paragraph>
        Bienvenido al sistema de procesamiento de documentos OCR.
      </Typography>

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Acciones Disponibles
          </Typography>
          <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
            <Button
              variant="contained"
              onClick={() => navigate('/upload')}
            >
              Subir Documento
            </Button>
            <Button
              variant="outlined"
              onClick={() => navigate('/documents')}
            >
              Ver Documentos
            </Button>
          </Box>
        </CardContent>
      </Card>

      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Estado del Sistema
          </Typography>
          <Typography variant="body2" color="text.secondary">
            ✅ Frontend funcionando correctamente
          </Typography>
          <Typography variant="body2" color="text.secondary">
            ✅ Contextos cargados
          </Typography>
          <Typography variant="body2" color="text.secondary">
            ✅ Navegación activa
          </Typography>
        </CardContent>
      </Card>
    </Container>
  );
};

export default SimpleDashboard;

