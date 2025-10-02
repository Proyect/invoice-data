import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Button,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Alert,
  Box,
  Chip
} from '@mui/material';
import {
  CheckCircle,
  Error,
  Warning,
  Info,
  Refresh
} from '@mui/icons-material';
// Funciones de diagnóstico simplificadas
const diagnoseDownloadSupport = () => ({
  browserSupport: true,
  blobSupport: typeof Blob !== 'undefined',
  downloadSupport: typeof document.createElement('a').download !== 'undefined',
  issues: [] as string[],
  recommendations: [] as string[]
});

const testDownloadCapability = async (): Promise<boolean> => {
  try {
    const blob = new Blob(['test'], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'test.txt';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    return true;
  } catch {
    return false;
  }
};

const DownloadDiagnostics: React.FC = () => {
  const [diagnostics, setDiagnostics] = useState(diagnoseDownloadSupport());
  const [testResult, setTestResult] = useState<boolean | null>(null);
  const [isRunningTest, setIsRunningTest] = useState(false);

  const runTest = async () => {
    setIsRunningTest(true);
    try {
      const result = await testDownloadCapability();
      setTestResult(result);
    } catch (error) {
      setTestResult(false);
    } finally {
      setIsRunningTest(false);
    }
  };

  const refreshDiagnostics = () => {
    setDiagnostics(diagnoseDownloadSupport());
    setTestResult(null);
  };

  const getStatusIcon = (status: boolean) => {
    return status ? <CheckCircle color="success" /> : <Error color="error" />;
  };

  const getStatusColor = (status: boolean) => {
    return status ? 'success' : 'error';
  };

  return (
    <Card sx={{ mb: 2 }}>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6">🔍 Diagnóstico de Descarga</Typography>
          <Button
            variant="outlined"
            size="small"
            startIcon={<Refresh />}
            onClick={refreshDiagnostics}
          >
            Actualizar
          </Button>
        </Box>

        {/* Estado general */}
        <Box display="flex" gap={1} mb={2}>
          <Chip
            icon={getStatusIcon(diagnostics.browserSupport)}
            label="Navegador"
            color={getStatusColor(diagnostics.browserSupport)}
            size="small"
          />
          <Chip
            icon={getStatusIcon(diagnostics.blobSupport)}
            label="Blob"
            color={getStatusColor(diagnostics.blobSupport)}
            size="small"
          />
          <Chip
            icon={getStatusIcon(diagnostics.downloadSupport)}
            label="Descarga"
            color={getStatusColor(diagnostics.downloadSupport)}
            size="small"
          />
        </Box>

        {/* Test de descarga */}
        <Box mb={2}>
          <Button
            variant="contained"
            size="small"
            onClick={runTest}
            disabled={isRunningTest}
            startIcon={isRunningTest ? <Refresh /> : <Info />}
          >
            {isRunningTest ? 'Probando...' : 'Probar Descarga'}
          </Button>
          
          {testResult !== null && (
            <Alert 
              severity={testResult ? 'success' : 'error'} 
              sx={{ mt: 1 }}
            >
              {testResult 
                ? '✅ Test de descarga exitoso' 
                : '❌ Test de descarga falló'
              }
            </Alert>
          )}
        </Box>

        {/* Problemas encontrados */}
        {diagnostics.issues.length > 0 && (
          <Alert severity="warning" sx={{ mb: 2 }}>
            <Typography variant="subtitle2" gutterBottom>
              ⚠️ Problemas detectados:
            </Typography>
            <List dense>
              {diagnostics.issues.map((issue, index) => (
                <ListItem key={index} sx={{ py: 0 }}>
                  <ListItemIcon>
                    <Warning fontSize="small" />
                  </ListItemIcon>
                  <ListItemText primary={issue} />
                </ListItem>
              ))}
            </List>
          </Alert>
        )}

        {/* Recomendaciones */}
        {diagnostics.recommendations.length > 0 && (
          <Alert severity="info">
            <Typography variant="subtitle2" gutterBottom>
              💡 Recomendaciones:
            </Typography>
            <List dense>
              {diagnostics.recommendations.map((rec, index) => (
                <ListItem key={index} sx={{ py: 0 }}>
                  <ListItemIcon>
                    <Info fontSize="small" />
                  </ListItemIcon>
                  <ListItemText primary={rec} />
                </ListItem>
              ))}
            </List>
          </Alert>
        )}

        {/* Información del navegador */}
        <Box mt={2}>
          <Typography variant="caption" color="text.secondary">
            Navegador: {navigator.userAgent.split(' ')[0]} | 
            Plataforma: {navigator.platform} | 
            Seguro: {window.isSecureContext ? 'Sí' : 'No'}
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );
};

export default DownloadDiagnostics;
