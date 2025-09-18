import React, { useRef, useEffect, useState } from 'react';

interface RenderInfo {
  componentName: string;
  renderCount: number;
  lastRender: number;
  timeSinceLastRender: number;
  averageTimeBetweenRenders: number;
  renderHistory: number[];
}

const RenderAnalyzer: React.FC = () => {
  const [isVisible, setIsVisible] = useState(true);
  const [renderInfo, setRenderInfo] = useState<RenderInfo>({
    componentName: 'RenderAnalyzer',
    renderCount: 0,
    lastRender: Date.now(),
    timeSinceLastRender: 0,
    averageTimeBetweenRenders: 0,
    renderHistory: []
  });

  const renderCountRef = useRef(0);
  const lastRenderRef = useRef(Date.now());
  const renderHistoryRef = useRef<number[]>([]);

  useEffect(() => {
    renderCountRef.current += 1;
    const now = Date.now();
    const timeSinceLastRender = now - lastRenderRef.current;
    
    // Actualizar historial de renders (mantener solo los últimos 20)
    renderHistoryRef.current.push(timeSinceLastRender);
    if (renderHistoryRef.current.length > 20) {
      renderHistoryRef.current.shift();
    }

    // Calcular tiempo promedio entre renders
    const averageTime = renderHistoryRef.current.length > 0 
      ? renderHistoryRef.current.reduce((a, b) => a + b, 0) / renderHistoryRef.current.length 
      : 0;

    // Actualizar estado SOLO UNA VEZ al montar
    if (renderCountRef.current === 1) {
      setRenderInfo({
        componentName: 'RenderAnalyzer',
        renderCount: 1,
        lastRender: now,
        timeSinceLastRender,
        averageTimeBetweenRenders: Math.round(averageTime),
        renderHistory: [...renderHistoryRef.current]
      });
    }

    lastRenderRef.current = now;

    // Log detallado SOLO UNA VEZ
    if (renderCountRef.current === 1) {
      console.log(`🔄 RenderAnalyzer #1: Inicializado`);
      console.log(`   - Tiempo desde último render: ${timeSinceLastRender}ms`);
      console.log(`   - Promedio entre renders: ${Math.round(averageTime)}ms`);
    }
  }, []); // ✅ ARRAY VACÍO - Solo se ejecuta una vez

  if (!isVisible) return null;

  const getStatusColor = () => {
    if (renderInfo.averageTimeBetweenRenders < 50) return '#f44336'; // Rojo - muy frecuente
    if (renderInfo.averageTimeBetweenRenders < 200) return '#ff9800'; // Naranja - frecuente
    return '#4caf50'; // Verde - normal
  };

  const getStatusText = () => {
    if (renderInfo.averageTimeBetweenRenders < 50) return 'CRÍTICO';
    if (renderInfo.averageTimeBetweenRenders < 200) return 'ALTO';
    return 'NORMAL';
  };

  return (
    <div style={{
      position: 'fixed',
      top: '10px',
      left: '10px',
      background: 'rgba(0,0,0,0.95)',
      color: 'white',
      padding: '15px',
      borderRadius: '8px',
      zIndex: 10002,
      fontSize: '11px',
      fontFamily: 'monospace',
      minWidth: '300px',
      maxWidth: '400px',
      border: `2px solid ${getStatusColor()}`
    }}>
      <div style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center', 
        marginBottom: '10px',
        borderBottom: '1px solid #333',
        paddingBottom: '8px'
      }}>
        <span style={{ fontWeight: 'bold', color: getStatusColor() }}>
          🔍 Render Analyzer - {getStatusText()}
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

      <div style={{ marginBottom: '8px' }}>
        <div><strong>Total Renders:</strong> {renderInfo.renderCount}</div>
        <div><strong>Último Render:</strong> {new Date(renderInfo.lastRender).toLocaleTimeString()}</div>
        <div><strong>Tiempo desde último:</strong> <span style={{ color: getStatusColor() }}>{renderInfo.timeSinceLastRender}ms</span></div>
        <div><strong>Promedio entre renders:</strong> <span style={{ color: getStatusColor() }}>{renderInfo.averageTimeBetweenRenders}ms</span></div>
      </div>

      <div style={{ marginBottom: '8px' }}>
        <div><strong>Últimos 5 intervalos:</strong></div>
        <div style={{ fontSize: '10px', color: '#B0BEC5' }}>
          [{renderInfo.renderHistory.slice(-5).map(t => `${t}ms`).join(', ')}]
        </div>
      </div>

      <div style={{ fontSize: '10px', color: '#B0BEC5' }}>
        {renderInfo.averageTimeBetweenRenders < 50 && (
          <div style={{ color: '#f44336' }}>
            ⚠️ RENDERS MUY FRECUENTES - Revisar useEffect y contextos
          </div>
        )}
        {renderInfo.averageTimeBetweenRenders >= 50 && renderInfo.averageTimeBetweenRenders < 200 && (
          <div style={{ color: '#ff9800' }}>
            ⚠️ RENDERS FRECUENTES - Monitorear dependencias
          </div>
        )}
        {renderInfo.averageTimeBetweenRenders >= 200 && (
          <div style={{ color: '#4caf50' }}>
            ✅ RENDERS NORMALES - Sistema estable
          </div>
        )}
      </div>
    </div>
  );
};

export default RenderAnalyzer;
