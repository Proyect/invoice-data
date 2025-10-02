import React, { useState } from 'react';
import { useDocuments } from '../contexts/OptimizedDocumentContext';

const ContextTestWithDocs: React.FC = () => {
  // Los hooks deben llamarse siempre al inicio del componente
  const { documents, loading } = useDocuments();
  const [isVisible, setIsVisible] = useState(true);

  if (!isVisible) return null;
  
  return (
    <div style={{
      position: 'fixed',
      top: '50px',
      right: '10px',
      background: 'green',
      color: 'white',
      padding: '10px',
      borderRadius: '4px',
      zIndex: 10000,
      fontSize: '12px',
      fontFamily: 'monospace',
      minWidth: '200px'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '5px' }}>
        <span>✅ DocumentContext funcionando</span>
        <button
          onClick={() => setIsVisible(false)}
          style={{
            background: 'transparent',
            border: '1px solid white',
            color: 'white',
            borderRadius: '3px',
            padding: '2px 6px',
            cursor: 'pointer',
            fontSize: '10px'
          }}
        >
          ✕
        </button>
      </div>
      <div>
        Documents: {documents.length}
        <br />
        Loading: {loading ? 'Yes' : 'No'}
      </div>
    </div>
  );
};

export default ContextTestWithDocs;
