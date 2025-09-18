import React, { useState } from 'react';

interface TestPanelProps {
  children: React.ReactNode;
}

const TestPanel: React.FC<TestPanelProps> = ({ children }) => {
  const [isVisible, setIsVisible] = useState(true);

  if (!isVisible) return null;

  return (
    <div style={{
      position: 'fixed',
      top: '10px',
      right: '10px',
      background: 'rgba(0,0,0,0.9)',
      color: 'white',
      padding: '15px',
      borderRadius: '8px',
      zIndex: 10001,
      fontSize: '12px',
      fontFamily: 'monospace',
      minWidth: '250px',
      maxWidth: '300px'
    }}>
      <div style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center', 
        marginBottom: '10px',
        borderBottom: '1px solid #333',
        paddingBottom: '8px'
      }}>
        <span style={{ fontWeight: 'bold', color: '#4CAF50' }}>🧪 Test Panel</span>
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
          ✕ Cerrar
        </button>
      </div>
      <div style={{ fontSize: '11px', color: '#B0BEC5', marginBottom: '10px' }}>
        Panel de pruebas para verificar el funcionamiento del sistema
      </div>
      <div>
        {children}
      </div>
    </div>
  );
};

export default TestPanel;

