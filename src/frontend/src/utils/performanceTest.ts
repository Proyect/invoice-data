// Utilidad para testing de rendimiento
export interface PerformanceTestResult {
  testName: string;
  passed: boolean;
  message: string;
  metrics?: {
    renderCount: number;
    averageRenderTime: number;
    maxRenderTime: number;
    minRenderTime: number;
  };
}

export class PerformanceTester {
  private renderCount = 0;
  private renderTimes: number[] = [];
  private lastRenderTime = Date.now();
  private startTime = Date.now();

  constructor(private componentName: string) {}

  recordRender(): void {
    this.renderCount++;
    const now = Date.now();
    const timeSinceLastRender = now - this.lastRenderTime;
    
    this.renderTimes.push(timeSinceLastRender);
    
    // Mantener solo los últimos 100 renders
    if (this.renderTimes.length > 100) {
      this.renderTimes = this.renderTimes.slice(-100);
    }
    
    this.lastRenderTime = now;
  }

  getMetrics() {
    const averageRenderTime = this.renderTimes.length > 0 
      ? this.renderTimes.reduce((a, b) => a + b, 0) / this.renderTimes.length 
      : 0;
    const maxRenderTime = this.renderTimes.length > 0 ? Math.max(...this.renderTimes) : 0;
    const minRenderTime = this.renderTimes.length > 0 ? Math.min(...this.renderTimes) : 0;

    return {
      renderCount: this.renderCount,
      averageRenderTime,
      maxRenderTime,
      minRenderTime,
      totalTime: Date.now() - this.startTime
    };
  }

  runTests(): PerformanceTestResult[] {
    const metrics = this.getMetrics();
    const results: PerformanceTestResult[] = [];

    // Test 1: Verificar que no hay re-renders excesivos
    results.push({
      testName: 'Re-renders Controlados',
      passed: this.renderCount <= 5,
      message: this.renderCount <= 5 
        ? `✅ Solo ${this.renderCount} renders (excelente)`
        : `❌ Demasiados renders: ${this.renderCount} (debería ser ≤ 5)`,
      metrics
    });

    // Test 2: Verificar que no hay renders muy frecuentes
    results.push({
      testName: 'Frecuencia de Renders',
      passed: metrics.averageRenderTime >= 100,
      message: metrics.averageRenderTime >= 100
        ? `✅ Renders espaciados: ${metrics.averageRenderTime.toFixed(2)}ms promedio`
        : `❌ Renders muy frecuentes: ${metrics.averageRenderTime.toFixed(2)}ms promedio (debería ser ≥ 100ms)`,
      metrics
    });

    // Test 3: Verificar estabilidad de renders
    results.push({
      testName: 'Estabilidad de Renders',
      passed: metrics.maxRenderTime < 1000 && metrics.minRenderTime > 10,
      message: metrics.maxRenderTime < 1000 && metrics.minRenderTime > 10
        ? `✅ Renders estables: min ${metrics.minRenderTime}ms, max ${metrics.maxRenderTime}ms`
        : `❌ Renders inestables: min ${metrics.minRenderTime}ms, max ${metrics.maxRenderTime}ms`,
      metrics
    });

    // Test 4: Verificar que no hay bucles infinitos
    results.push({
      testName: 'Sin Bucles Infinitos',
      passed: this.renderCount <= 10,
      message: this.renderCount <= 10
        ? `✅ Sin bucles infinitos: ${this.renderCount} renders en ${metrics.totalTime}ms`
        : `❌ Posible bucle infinito: ${this.renderCount} renders en ${metrics.totalTime}ms`,
      metrics
    });

    return results;
  }

  reset(): void {
    this.renderCount = 0;
    this.renderTimes = [];
    this.lastRenderTime = Date.now();
    this.startTime = Date.now();
  }
}

// Hook para usar en componentes
export const usePerformanceTest = (componentName: string) => {
  const tester = new PerformanceTester(componentName);
  
  return {
    recordRender: () => tester.recordRender(),
    getMetrics: () => tester.getMetrics(),
    runTests: () => tester.runTests(),
    reset: () => tester.reset()
  };
};
