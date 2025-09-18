#!/usr/bin/env node
/**
 * Script para remover componentes de debug del frontend
 * Ejecutar cuando ya no necesites monitorear los re-renders
 */

const fs = require('fs');
const path = require('path');

console.log('🧹 Removiendo componentes de debug...');

// Archivos a limpiar
const filesToClean = [
  'src/contexts/DocumentContext.tsx',
  'src/contexts/AuthContext.tsx',
  'src/App.tsx'
];

// Patrones a remover
const patternsToRemove = [
  // Import de RenderCounter
  /import RenderCounter from '\.\.\/components\/RenderCounter';?\n/g,
  // Líneas con RenderCounter
  /^\s*<RenderCounter[^>]*\/>\s*$/gm,
  // Líneas con PerformanceMonitor
  /^\s*<PerformanceMonitor[^>]*\/>\s*$/gm,
  // Import de PerformanceMonitor
  /import PerformanceMonitor from '\.\.\/components\/PerformanceMonitor';?\n/g
];

filesToClean.forEach(filePath => {
  const fullPath = path.join(__dirname, filePath);
  
  if (fs.existsSync(fullPath)) {
    let content = fs.readFileSync(fullPath, 'utf8');
    let originalContent = content;
    
    // Aplicar patrones de limpieza
    patternsToRemove.forEach(pattern => {
      content = content.replace(pattern, '');
    });
    
    // Limpiar líneas vacías múltiples
    content = content.replace(/\n\s*\n\s*\n/g, '\n\n');
    
    if (content !== originalContent) {
      fs.writeFileSync(fullPath, content);
      console.log(`✅ Limpiado: ${filePath}`);
    } else {
      console.log(`ℹ️  Sin cambios: ${filePath}`);
    }
  } else {
    console.log(`❌ No encontrado: ${filePath}`);
  }
});

// Archivos de debug a eliminar
const debugFilesToDelete = [
  'src/components/RenderCounter.tsx',
  'src/components/PerformanceMonitor.tsx',
  'src/components/DebugInfo.tsx',
  'test-rerenders.html',
  'test-rerenders-fixed.html',
  'test-performance.html'
];

debugFilesToDelete.forEach(filePath => {
  const fullPath = path.join(__dirname, filePath);
  
  if (fs.existsSync(fullPath)) {
    fs.unlinkSync(fullPath);
    console.log(`🗑️  Eliminado: ${filePath}`);
  }
});

console.log('🎉 Limpieza completada!');
console.log('💡 Los componentes de debug han sido removidos del código.');
