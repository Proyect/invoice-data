import React, { useEffect, useRef } from 'react';
import { useDocuments } from '../contexts/DocumentContext';

const DebugInfo: React.FC = () => {
  const { documents, loading } = useDocuments();
  const renderCount = useRef(0);
  
  useEffect(() => {
    renderCount.current += 1;
    console.log(`🔍 DebugInfo render #${renderCount.current}`);
    console.log(`📊 Documents count: ${documents.length}`);
    console.log(`⏳ Loading: ${loading}`);
  });

  return (
    <div style={{ 
      position: 'fixed', 
      top: 0, 
      right: 0, 
      background: 'rgba(0,0,0,0.8)', 
      color: 'white', 
      padding: '10px',
      fontSize: '12px',
      zIndex: 9999
    }}>
      <div>Renders: {renderCount.current}</div>
      <div>Documents: {documents.length}</div>
      <div>Loading: {loading ? 'Yes' : 'No'}</div>
    </div>
  );
};

export default DebugInfo;










