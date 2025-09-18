import React from 'react';
import { useAuth } from '../contexts/SimpleAuthContext';
import { useDocuments } from '../contexts/DocumentContext';

const ContextTest: React.FC = () => {
  // Los hooks deben llamarse siempre al inicio del componente
  const auth = useAuth();
  const documents = useDocuments();
  
  return (
    <div style={{
      position: 'fixed',
      top: '10px',
      right: '10px',
      background: 'green',
      color: 'white',
      padding: '10px',
      borderRadius: '4px',
      zIndex: 10000,
      fontSize: '12px',
      fontFamily: 'monospace'
    }}>
      ✅ Contextos funcionando
      <br />
      Auth: {auth.user ? 'Logged in' : 'Not logged in'}
      <br />
      Documents: {documents.documents.length}
      <br />
      Loading: {documents.loading ? 'Yes' : 'No'}
    </div>
  );
};

export default ContextTest;