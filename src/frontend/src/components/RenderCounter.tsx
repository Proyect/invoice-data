import React, { useRef, useEffect, useState } from 'react';

interface RenderCounterProps {
  componentName: string;
  showDetails?: boolean;
}

const RenderCounter: React.FC<RenderCounterProps> = ({ componentName, showDetails = false }) => {
  const renderCount = useRef(0);
  const [lastRenderTime, setLastRenderTime] = useState<Date>(new Date());
  const [renderReasons, setRenderReasons] = useState<string[]>([]);
  
  useEffect(() => {
    renderCount.current += 1;
    const now = new Date();
    setLastRenderTime(now);
    
    console.log(`🔄 ${componentName} render #${renderCount.current} at ${now.toLocaleTimeString()}`);
    
    // Detectar posibles causas de re-render
    const reasons: string[] = [];
    
    if (renderCount.current === 1) {
      reasons.push('Initial mount');
    } else if (renderCount.current === 2) {
      reasons.push('State update (loading)');
    } else if (renderCount.current === 3) {
      reasons.push('State update (documents)');
    } else if (renderCount.current === 4) {
      reasons.push('State update (initialized)');
    } else {
      reasons.push('Additional re-render');
    }
    
    setRenderReasons(prev => [...prev.slice(-2), ...reasons]);
  });

  const getStatusColor = () => {
    if (renderCount.current <= 2) return '#4CAF50'; // Verde - Normal
    if (renderCount.current <= 4) return '#FF9800'; // Naranja - Aceptable
    return '#F44336'; // Rojo - Muchos re-renders
  };

  return (
    <div style={{ 
      position: 'fixed', 
      top: '10px', 
      right: '10px', 
      background: 'rgba(0,0,0,0.9)', 
      color: 'white', 
      padding: '12px',
      fontSize: '11px',
      zIndex: 9999,
      borderRadius: '6px',
      border: `2px solid ${getStatusColor()}`,
      minWidth: '200px',
      fontFamily: 'monospace'
    }}>
      <div style={{ fontWeight: 'bold', marginBottom: '4px' }}>
        🔄 {componentName}: {renderCount.current} renders
      </div>
      
      {showDetails && (
        <div style={{ fontSize: '10px', opacity: 0.8 }}>
          <div>Last: {lastRenderTime.toLocaleTimeString()}</div>
          {renderReasons.length > 0 && (
            <div>Reasons: {renderReasons.join(', ')}</div>
          )}
        </div>
      )}
      
      {renderCount.current > 4 && (
        <div style={{ 
          fontSize: '10px', 
          color: '#FFCDD2', 
          marginTop: '4px',
          fontStyle: 'italic'
        }}>
          ⚠️ Consider optimizing
        </div>
      )}
    </div>
  );
};

export default RenderCounter;

