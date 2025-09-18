/**
 * Utilidades de diagnóstico para problemas de descarga
 */

export interface DownloadDiagnostics {
  browserSupport: boolean;
  blobSupport: boolean;
  downloadSupport: boolean;
  issues: string[];
  recommendations: string[];
}

export function diagnoseDownloadSupport(): DownloadDiagnostics {
  const issues: string[] = [];
  const recommendations: string[] = [];

  // Verificar soporte de Blob
  const blobSupport = typeof Blob !== 'undefined' && typeof URL !== 'undefined';
  if (!blobSupport) {
    issues.push('El navegador no soporta Blob o URL.createObjectURL');
    recommendations.push('Actualiza tu navegador a una versión más reciente');
  }

  // Verificar soporte de descarga
  const downloadSupport = typeof document.createElement === 'function';
  if (!downloadSupport) {
    issues.push('No se puede crear elementos DOM para descarga');
    recommendations.push('Verifica que JavaScript esté habilitado');
  }

  // Verificar navegador
  const userAgent = navigator.userAgent;
  const isOldBrowser = userAgent.includes('MSIE') || userAgent.includes('Trident');
  if (isOldBrowser) {
    issues.push('Navegador muy antiguo detectado');
    recommendations.push('Usa Chrome, Firefox, Safari o Edge moderno');
  }

  // Verificar HTTPS (para algunos navegadores)
  const isSecureContext = window.isSecureContext || window.location.protocol === 'https:';
  if (!isSecureContext && window.location.hostname !== 'localhost') {
    issues.push('Conexión no segura (HTTP)');
    recommendations.push('Usa HTTPS para mejor compatibilidad');
  }

  // Verificar memoria disponible (aproximado)
  const memoryInfo = (performance as any).memory;
  if (memoryInfo) {
    const usedMB = memoryInfo.usedJSHeapSize / (1024 * 1024);
    const totalMB = memoryInfo.totalJSHeapSize / (1024 * 1024);
    
    if (usedMB / totalMB > 0.9) {
      issues.push('Memoria del navegador casi llena');
      recommendations.push('Cierra otras pestañas y recarga la página');
    }
  }

  return {
    browserSupport: !isOldBrowser,
    blobSupport,
    downloadSupport,
    issues,
    recommendations
  };
}

export function testDownloadCapability(): Promise<boolean> {
  return new Promise((resolve) => {
    try {
      // Crear un blob de prueba
      const testBlob = new Blob(['test content'], { type: 'text/plain' });
      const testUrl = URL.createObjectURL(testBlob);
      
      // Crear un enlace de prueba
      const testLink = document.createElement('a');
      testLink.href = testUrl;
      testLink.download = 'test-download.txt';
      testLink.style.display = 'none';
      
      // Agregar al DOM temporalmente
      document.body.appendChild(testLink);
      
      // Simular clic
      testLink.click();
      
      // Limpiar
      document.body.removeChild(testLink);
      URL.revokeObjectURL(testUrl);
      
      resolve(true);
    } catch (error) {
      console.error('Error en test de descarga:', error);
      resolve(false);
    }
  });
}

export function logDownloadError(error: any, documentId: string, filename: string): void {
  console.group('🔍 DIAGNÓSTICO DE ERROR DE DESCARGA');
  console.log('Document ID:', documentId);
  console.log('Filename:', filename);
  console.log('Error:', error);
  console.log('Error message:', error.message);
  console.log('Error stack:', error.stack);
  
  if (error.response) {
    console.log('Response status:', error.response.status);
    console.log('Response data:', error.response.data);
    console.log('Response headers:', error.response.headers);
  }
  
  // Diagnóstico del navegador
  const diagnostics = diagnoseDownloadSupport();
  console.log('Browser diagnostics:', diagnostics);
  
  console.groupEnd();
}

export function getDownloadErrorSuggestion(error: any): string {
  if (error.response?.status === 404) {
    return 'El archivo no existe en el servidor. Verifica que el documento esté disponible.';
  }
  
  if (error.response?.status === 403) {
    return 'No tienes permisos para descargar este archivo. Verifica tu sesión.';
  }
  
  if (error.response?.status === 500) {
    return 'Error del servidor. Intenta nuevamente en unos minutos.';
  }
  
  if (error.code === 'ECONNABORTED') {
    return 'La descarga tardó demasiado tiempo. Verifica tu conexión a internet.';
  }
  
  if (error.message?.includes('blob')) {
    return 'Problema con el archivo descargado. Intenta con otro navegador.';
  }
  
  if (error.message?.includes('network')) {
    return 'Problema de conexión. Verifica tu internet y recarga la página.';
  }
  
  return 'Error desconocido. Intenta recargar la página o contacta soporte.';
}
