import React, { useRef, useEffect, useState } from 'react';

interface EffectInfo {
  effectName: string;
  executionCount: number;
  lastExecution: number;
  timeSinceLastExecution: number;
  averageTimeBetweenExecutions: number;
  executionHistory: number[];
}

const EffectMonitor: React.FC = () => {
  const [isVisible, setIsVisible] = useState(true);
  const [effects, setEffects] = useState<EffectInfo[]>([]);
  const effectCounters = useRef<Map<string, number>>(new Map());
  const effectHistory = useRef<Map<string, number[]>>(new Map());
  const lastExecution = useRef<Map<string, number>>(new Map());

  // Monitorear useEffect del componente principal - SOLO UNA VEZ AL MONTAR
  useEffect(() => {
    const effectName = 'AppContent-main-effect';
    const now = Date.now();
    
    // Actualizar contador
    const currentCount = effectCounters.current.get(effectName) || 0;
    effectCounters.current.set(effectName, currentCount + 1);
    
    // Actualizar historial
    const history = effectHistory.current.get(effectName) || [];
    const lastExec = lastExecution.current.get(effectName) || now;
    const timeSinceLast = now - lastExec;
    
    history.push(timeSinceLast);
    if (history.length > 10) history.shift();
    effectHistory.current.set(effectName, history);
    lastExecution.current.set(effectName, now);
    
    // Calcular promedio
    const average = history.length > 0 ? history.reduce((a, b) => a + b, 0) / history.length : 0;
    
    console.log(`🔄 EffectMonitor - ${effectName}:`);
    console.log(`   - Ejecución #${currentCount + 1}`);
    console.log(`   - Tiempo desde última: ${timeSinceLast}ms`);
    console.log(`   - Promedio: ${Math.round(average)}ms`);
    
    if (timeSinceLast < 100 && currentCount > 3) {
      console.warn(`⚠️ EFECTO MUY FRECUENTE: ${effectName} - ${timeSinceLast}ms`);
    }
    
    // Actualizar estado SOLO UNA VEZ
    if (currentCount === 0) {
      setEffects([{
        effectName,
        executionCount: 1,
        lastExecution: now,
        timeSinceLastExecution: timeSinceLast,
        averageTimeBetweenExecutions: Math.round(average),
        executionHistory: [...history]
      }]);
    }
  }, []); // ✅ ARRAY VACÍO - Solo se ejecuta una vez al montar

  if (!isVisible) return null;

  const getStatusColor = (effect: EffectInfo) => {
    if (effect.averageTimeBetweenExecutions < 100) return '#f44336'; // Rojo
    if (effect.averageTimeBetweenExecutions < 500) return '#ff9800'; // Naranja
    return '#4caf50'; // Verde
  };

  const getStatusText = (effect: EffectInfo) => {
    if (effect.averageTimeBetweenExecutions < 100) return 'CRÍTICO';
    if (effect.averageTimeBetweenExecutions < 500) return 'ALTO';
    return 'NORMAL';
  };

  return (
    <div style={{
      position: 'fixed',
      top: '50%',
      left: '50%',
      transform: 'translate(-50%, -50%)',
      background: 'rgba(0,0,0,0.95)',
      color: 'white',
      padding: '15px',
      borderRadius: '8px',
      zIndex: 10004,
      fontSize: '11px',
      fontFamily: 'monospace',
      minWidth: '400px',
      maxWidth: '500px',
      maxHeight: '80vh',
      overflow: 'auto'
    }}>
      <div style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center', 
        marginBottom: '15px',
        borderBottom: '1px solid #333',
        paddingBottom: '8px'
      }}>
        <span style={{ fontWeight: 'bold', color: '#FF9800' }}>
          🔄 Effect Monitor
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

      {effects.length === 0 ? (
        <div style={{ color: '#B0BEC5', textAlign: 'center', padding: '20px' }}>
          Monitoreando efectos...
        </div>
      ) : (
        effects.map((effect, index) => {
          const statusColor = getStatusColor(effect);
          const statusText = getStatusText(effect);
          
          return (
            <div key={index} style={{
              marginBottom: '10px',
              padding: '10px',
              background: 'rgba(255,255,255,0.1)',
              borderRadius: '4px',
              border: `1px solid ${statusColor}`
            }}>
              <div style={{ 
                display: 'flex', 
                justifyContent: 'space-between', 
                alignItems: 'center',
                marginBottom: '5px'
              }}>
                <span style={{ fontWeight: 'bold' }}>{effect.effectName}</span>
                <span style={{ color: statusColor, fontWeight: 'bold' }}>
                  {statusText}
                </span>
              </div>
              
              <div style={{ fontSize: '10px', color: '#B0BEC5' }}>
                <div>Ejecuciones: {effect.executionCount}</div>
                <div>Tiempo desde última: <span style={{ color: statusColor }}>{effect.timeSinceLastExecution}ms</span></div>
                <div>Promedio: <span style={{ color: statusColor }}>{effect.averageTimeBetweenExecutions}ms</span></div>
                <div>Últimos intervalos: [{effect.executionHistory.slice(-3).map(t => `${t}ms`).join(', ')}]</div>
              </div>
              
              {statusText === 'CRÍTICO' && (
                <div style={{ color: '#f44336', fontSize: '10px', marginTop: '5px' }}>
                  ⚠️ EFECTO EN BUCLE INFINITO - Revisar dependencias
                </div>
              )}
            </div>
          );
        })
      )}

      <div style={{ 
        marginTop: '15px', 
        padding: '10px', 
        background: 'rgba(255,255,255,0.05)', 
        borderRadius: '4px',
        fontSize: '10px',
        color: '#B0BEC5'
      }}>
        <div><strong>💡 Diagnóstico:</strong></div>
        <div>• <strong>CRÍTICO:</strong> Efecto ejecutándose cada &lt;100ms (bucle infinito)</div>
        <div>• <strong>ALTO:</strong> Efecto ejecutándose cada 100-500ms (frecuente)</div>
        <div>• <strong>NORMAL:</strong> Efecto ejecutándose cada &gt;500ms (estable)</div>
      </div>
    </div>
  );
};

export default EffectMonitor;
