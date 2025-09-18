import React, { useRef, useEffect, useState } from 'react';
import { useDocuments } from '../contexts/DocumentContext';
import { useAuth } from '../contexts/SimpleAuthContext';

interface PerformanceStats {
  documentProviderRenders: number;
  documentListRenders: number;
  authProviderRenders: number;
  totalRenders: number;
  lastRenderTime: number;
}

const PerformanceMonitor: React.FC = () => {
  const { documents, loading } = useDocuments();
  const { user, token } = useAuth();
  
  const [stats, setStats] = useState<PerformanceStats>({
    documentProviderRenders: 0,
    documentListRenders: 0,
    authProviderRenders: 0,
    totalRenders: 0,
    lastRenderTime: Date.now()
  });
  
  const renderCount = useRef(0);
  const documentProviderRenders = useRef(0);
  const documentListRenders = useRef(0);
  const authProviderRenders = useRef(0);
  
  useEffect(() => {
    renderCount.current += 1;
    const now = Date.now();
    
    setStats(prev => ({
      ...prev,
      totalRenders: renderCount.current,
      lastRenderTime: now
    }));
    
    console.log(`🔍 PerformanceMonitor render #${renderCount.current}`, {
      documents: documents.length,
      loading,
      user: user?.username,
      hasToken: !!token,
      timestamp: new Date(now).toLocaleTimeString()
    });
  });

  // Simular contadores de otros componentes
  useEffect(() => {
    documentProviderRenders.current += 1;
    setStats(prev => ({ ...prev, documentProviderRenders: documentProviderRenders.current }));
  }, [documents, loading]);

  useEffect(() => {
    documentListRenders.current += 1;
    setStats(prev => ({ ...prev, documentListRenders: documentListRenders.current }));
  }, [documents]);

  useEffect(() => {
    authProviderRenders.current += 1;
    setStats(prev => ({ ...prev, authProviderRenders: authProviderRenders.current }));
  }, [user, token]);

  const resetCounters = () => {
    renderCount.current = 0;
    documentProviderRenders.current = 0;
    documentListRenders.current = 0;
    authProviderRenders.current = 0;
    setStats({
      documentProviderRenders: 0,
      documentListRenders: 0,
      authProviderRenders: 0,
      totalRenders: 0,
      lastRenderTime: Date.now()
    });
  };

  return (
    <div style={{ 
      position: 'fixed', 
      top: '10px', 
      left: '10px', 
      background: 'rgba(0,0,0,0.9)', 
      color: 'white', 
      padding: '15px',
      fontSize: '12px',
      zIndex: 10000,
      borderRadius: '8px',
      minWidth: '300px',
      fontFamily: 'monospace'
    }}>
      <div style={{ marginBottom: '10px', fontWeight: 'bold', color: '#4CAF50' }}>
        🔧 Performance Monitor
      </div>
      
      <div style={{ marginBottom: '5px' }}>
        <span style={{ color: '#FFC107' }}>Total Renders:</span> {stats.totalRenders}
      </div>
      
      <div style={{ marginBottom: '5px' }}>
        <span style={{ color: '#2196F3' }}>DocumentProvider:</span> {stats.documentProviderRenders}
      </div>
      
      <div style={{ marginBottom: '5px' }}>
        <span style={{ color: '#9C27B0' }}>DocumentList:</span> {stats.documentListRenders}
      </div>
      
      <div style={{ marginBottom: '5px' }}>
        <span style={{ color: '#FF9800' }}>AuthProvider:</span> {stats.authProviderRenders}
      </div>
      
      <div style={{ marginBottom: '10px', fontSize: '10px', color: '#B0BEC5' }}>
        Last: {new Date(stats.lastRenderTime).toLocaleTimeString()}
      </div>
      
      <div style={{ marginBottom: '5px' }}>
        <span style={{ color: '#4CAF50' }}>Documents:</span> {documents.length}
      </div>
      
      <div style={{ marginBottom: '5px' }}>
        <span style={{ color: '#4CAF50' }}>Loading:</span> {loading ? 'Yes' : 'No'}
      </div>
      
      <div style={{ marginBottom: '10px' }}>
        <span style={{ color: '#4CAF50' }}>User:</span> {user?.username || 'None'}
      </div>
      
      <button 
        onClick={resetCounters}
        style={{
          background: '#f44336',
          color: 'white',
          border: 'none',
          padding: '5px 10px',
          borderRadius: '4px',
          cursor: 'pointer',
          fontSize: '10px'
        }}
      >
        Reset Counters
      </button>
    </div>
  );
};

export default PerformanceMonitor;
