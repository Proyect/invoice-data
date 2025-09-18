import React, { useState, useEffect } from 'react';

const StableTest: React.FC = () => {
  const [renderCount, setRenderCount] = useState(0);
  const [lastRender, setLastRender] = useState(Date.now());
  const [isVisible, setIsVisible] = useState(true);

  useEffect(() => {
    setRenderCount(prev => prev + 1);
    setLastRender(Date.now());
  });

  if (!isVisible) return null;

  return (
    <div style={{
      position: 'fixed',
      top: '10px',
      left: '10px',
      background: 'purple',
      color: 'white',
      padding: '10px',
      borderRadius: '4px',
      zIndex: 10000,
      fontSize: '12px',
      fontFamily: 'monospace',
      minWidth: '180px'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '5px' }}>
        <span>🔧 Stable Test</span>
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
        Renders: {renderCount}
        <br />
        Last: {new Date(lastRender).toLocaleTimeString()}
      </div>
    </div>
  );
};

export default StableTest;
