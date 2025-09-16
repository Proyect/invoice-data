// Utilidades para debugging de re-renders

let renderCount = 0;

export const logRender = (componentName: string) => {
  renderCount++;
  console.log(`🔄 ${componentName} render #${renderCount}`);
};

export const resetRenderCount = () => {
  renderCount = 0;
  console.log('🔄 Reset render count');
};

