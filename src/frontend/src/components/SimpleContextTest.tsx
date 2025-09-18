import React, { useState } from 'react';

const SimpleContextTest: React.FC = () => {
  const [isVisible, setIsVisible] = useState(true);

  if (!isVisible) return null;

  return (
    <div style={{
      position: 'fixed',
      top: '10px',
      right: '10px',
      background: 'blue',
      color: 'white',
      padding: '10px',
      borderRadius: '4px',
      zIndex: 10000,
      fontSize: '12px',
      fontFamily: 'monospace',
      minWidth: '200px'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '5px' }}>
        <span>🔧 Simple Test - Contextos OK</span>
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
    </div>
  );
};

export default SimpleContextTest;
