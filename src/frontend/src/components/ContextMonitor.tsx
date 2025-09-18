import React, { useRef, useEffect, useState } from 'react';
import { useAuth } from '../contexts/SimpleAuthContext';
import { useDocuments } from '../contexts/DocumentContext';

const ContextMonitor: React.FC = () => {
  const [isVisible, setIsVisible] = useState(true);
  const authRenderCount = useRef(0);
  const docsRenderCount = useRef(0);
  const lastAuthRender = useRef(Date.now());
  const lastDocsRender = useRef(Date.now());

  // Usar los contextos para monitorear sus renders
  const authContext = useAuth();
  const docsContext = useDocuments();

  // Monitorear AuthContext - SOLO UNA VEZ AL MONTAR
  useEffect(() => {
    authRenderCount.current += 1;
    const now = Date.now();
    const timeSinceLastAuthRender = now - lastAuthRender.current;
    
    // Log SOLO UNA VEZ
    if (authRenderCount.current === 1) {
      console.log(`🔐 AuthContext inicializado`);
      console.log(`   - Auth state:`, { 
        loading: authContext.loading, 
        isAuthenticated: authContext.login,
        user: authContext.user?.username 
      });
    }
    
    lastAuthRender.current = now;
  }, []); // ✅ ARRAY VACÍO - Solo se ejecuta una vez

  // Monitorear DocumentContext - SOLO UNA VEZ AL MONTAR
  useEffect(() => {
    docsRenderCount.current += 1;
    const now = Date.now();
    const timeSinceLastDocsRender = now - lastDocsRender.current;
    
    // Log SOLO UNA VEZ
    if (docsRenderCount.current === 1) {
      console.log(`📄 DocumentContext inicializado`);
      console.log(`   - Docs state:`, { 
        loading: docsContext.loading, 
        documentsCount: docsContext.documents.length 
      });
    }
    
    lastDocsRender.current = now;
  }, []); // ✅ ARRAY VACÍO - Solo se ejecuta una vez

  if (!isVisible) return null;

  const getAuthStatus = () => {
    const timeSinceLastAuth = Date.now() - lastAuthRender.current;
    if (timeSinceLastAuth < 100) return { color: '#f44336', text: 'CRÍTICO' };
    if (timeSinceLastAuth < 500) return { color: '#ff9800', text: 'ALTO' };
    return { color: '#4caf50', text: 'NORMAL' };
  };

  const getDocsStatus = () => {
    const timeSinceLastDocs = Date.now() - lastDocsRender.current;
    if (timeSinceLastDocs < 100) return { color: '#f44336', text: 'CRÍTICO' };
    if (timeSinceLastDocs < 500) return { color: '#ff9800', text: 'ALTO' };
    return { color: '#4caf50', text: 'NORMAL' };
  };

  const authStatus = getAuthStatus();
  const docsStatus = getDocsStatus();

  return (
    <div style={{
      position: 'fixed',
      top: '10px',
      right: '10px',
      background: 'rgba(0,0,0,0.95)',
      color: 'white',
      padding: '15px',
      borderRadius: '8px',
      zIndex: 10003,
      fontSize: '11px',
      fontFamily: 'monospace',
      minWidth: '350px',
      maxWidth: '450px'
    }}>
      <div style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center', 
        marginBottom: '10px',
        borderBottom: '1px solid #333',
        paddingBottom: '8px'
      }}>
        <span style={{ fontWeight: 'bold', color: '#2196F3' }}>
          🔍 Context Monitor
        </span>
        <button
          onClick={() => setIsVisible(false)}
          style={{
            background: '#f44336',
            border: 'none',
            color: 'white',
            borderRadius: '4px',
            padding: '4px 8px',
            cursor: 'pointer',
            fontSize: '10px',
            fontWeight: 'bold'
          }}
        >
          ✕
        </button>
      </div>

      <div style={{ marginBottom: '10px' }}>
        <div style={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center',
          marginBottom: '5px',
          padding: '5px',
          background: 'rgba(255,255,255,0.1)',
          borderRadius: '4px'
        }}>
          <span>🔐 AuthContext</span>
          <span style={{ color: authStatus.color, fontWeight: 'bold' }}>
            {authStatus.text} ({authRenderCount.current} renders)
          </span>
        </div>
        <div style={{ fontSize: '10px', color: '#B0BEC5', marginLeft: '10px' }}>
          Loading: {authContext.loading ? 'Yes' : 'No'} | 
          Auth: {authContext.user ? 'Yes' : 'No'} | 
          User: {authContext.user?.username || 'None'}
        </div>
      </div>

      <div style={{ marginBottom: '10px' }}>
        <div style={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center',
          marginBottom: '5px',
          padding: '5px',
          background: 'rgba(255,255,255,0.1)',
          borderRadius: '4px'
        }}>
          <span>📄 DocumentContext</span>
          <span style={{ color: docsStatus.color, fontWeight: 'bold' }}>
            {docsStatus.text} ({docsRenderCount.current} renders)
          </span>
        </div>
        <div style={{ fontSize: '10px', color: '#B0BEC5', marginLeft: '10px' }}>
          Loading: {docsContext.loading ? 'Yes' : 'No'} | 
          Documents: {docsContext.documents.length} | 
          Type: DocumentContext
        </div>
      </div>

      <div style={{ fontSize: '10px', color: '#B0BEC5' }}>
        <div>💡 <strong>Diagnóstico:</strong></div>
        {authStatus.text === 'CRÍTICO' && (
          <div style={{ color: '#f44336' }}>⚠️ AuthContext se está actualizando constantemente</div>
        )}
        {docsStatus.text === 'CRÍTICO' && (
          <div style={{ color: '#f44336' }}>⚠️ DocumentContext se está actualizando constantemente</div>
        )}
        {authStatus.text === 'NORMAL' && docsStatus.text === 'NORMAL' && (
          <div style={{ color: '#4caf50' }}>✅ Ambos contextos funcionando normalmente</div>
        )}
      </div>
    </div>
  );
};

export default ContextMonitor;
