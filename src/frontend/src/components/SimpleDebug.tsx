import React, { useEffect, useRef } from 'react';

interface SimpleDebugProps {
  componentName: string;
}

const SimpleDebug: React.FC<SimpleDebugProps> = ({ componentName }) => {
  const renderCount = useRef(0);
  const lastRenderTime = useRef(Date.now());

  useEffect(() => {
    renderCount.current += 1;
    const now = Date.now();
    const timeSinceLastRender = now - lastRenderTime.current;
    
    console.log(`🔄 ${componentName} render #${renderCount.current} (${timeSinceLastRender}ms ago)`);
    
    // Alertar si hay renders muy frecuentes
    if (timeSinceLastRender < 50 && renderCount.current > 1) {
      console.warn(`⚠️ ${componentName}: Render muy frecuente (${timeSinceLastRender}ms)`);
    }
    
    lastRenderTime.current = now;
  }); // ✅ Sin dependencias - Solo para debugging

  return (
    <div style={{
      position: 'fixed',
      top: 10,
      right: 10,
      background: 'rgba(0,0,0,0.8)',
      color: 'white',
      padding: '5px 10px',
      borderRadius: '4px',
      fontSize: '12px',
      zIndex: 9999,
      fontFamily: 'monospace'
    }}>
      {componentName}: {renderCount.current}
    </div>
  );
};

export default SimpleDebug;
