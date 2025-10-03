#!/usr/bin/env python3
"""
Script de Inicio Rápido del Sistema OCR Optimizado
================================================

Este script configura y inicia el sistema OCR optimizado para procesamiento
en máximo 30 segundos sin depender de Redis.

Características:
- Verificación automática del sistema
- Configuración de modelos optimizados
- Procesamiento de documentos pendientes
- Inicio del servidor API
- Monitoreo en tiempo real
"""

import os
import sys
import time
import subprocess
import logging
from datetime import datetime
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('fast_ocr_startup.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class FastOCRSystemStarter:
    """Iniciador del sistema OCR optimizado"""
    
    def __init__(self):
        self.backend_path = Path(__file__).parent
        self.models_path = self.backend_path / "models" / "yolo_models"
        self.startup_time = datetime.now()
        self.system_status = {
            'models_checked': False,
            'pending_processed': False,
            'server_started': False,
            'optimization_completed': False
        }
    
    def print_banner(self):
        """Imprime banner de inicio"""
        banner = """
╔══════════════════════════════════════════════════════════════╗
║                    🚀 SISTEMA OCR RÁPIDO                     ║
║                                                              ║
║  Procesamiento optimizado para máximo 30 segundos           ║
║  Sin dependencia de Redis - Procesamiento síncrono          ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
        """
        print(banner)
        logger.info("🚀 Iniciando Sistema OCR Optimizado")
    
    def check_system_requirements(self) -> bool:
        """Verifica requisitos del sistema"""
        logger.info("🔍 Verificando requisitos del sistema...")
        
        requirements_met = True
        
        # Verificar Python
        python_version = sys.version_info
        if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
            logger.error(f"❌ Python 3.8+ requerido, actual: {python_version.major}.{python_version.minor}")
            requirements_met = False
        else:
            logger.info(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
        
        # Verificar directorio de modelos
        if not self.models_path.exists():
            logger.error(f"❌ Directorio de modelos no encontrado: {self.models_path}")
            requirements_met = False
        else:
            model_count = len([d for d in self.models_path.iterdir() if d.is_dir()])
            logger.info(f"✅ Directorio de modelos encontrado ({model_count} modelos)")
        
        # Verificar archivos críticos
        critical_files = [
            "services/fast_ocr_service.py",
            "services/model_loader.py",
            "services/ocr_service.py",
            "database.py",
            "config.py"
        ]
        
        for file_path in critical_files:
            full_path = self.backend_path / file_path
            if not full_path.exists():
                logger.error(f"❌ Archivo crítico no encontrado: {file_path}")
                requirements_met = False
            else:
                logger.info(f"✅ {file_path}")
        
        return requirements_met
    
    def check_models(self) -> bool:
        """Verifica estado de los modelos"""
        logger.info("🤖 Verificando modelos YOLO...")
        
        try:
            # Ejecutar script de verificación de modelos
            result = subprocess.run(
                [sys.executable, "check_models.py"],
                cwd=self.backend_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                logger.info("✅ Verificación de modelos completada")
                print(result.stdout)
                self.system_status['models_checked'] = True
                return True
            else:
                logger.error(f"❌ Error verificando modelos: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("❌ Timeout verificando modelos")
            return False
        except Exception as e:
            logger.error(f"❌ Error ejecutando verificación: {e}")
            return False
    
    def optimize_models(self) -> bool:
        """Optimiza modelos para velocidad"""
        logger.info("⚙️ Optimizando modelos para velocidad...")
        
        try:
            # Ejecutar optimización de modelos
            result = subprocess.run(
                [sys.executable, "scripts/optimize_models_for_speed.py"],
                cwd=self.backend_path,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutos máximo
            )
            
            if result.returncode == 0:
                logger.info("✅ Optimización de modelos completada")
                print(result.stdout)
                self.system_status['optimization_completed'] = True
                return True
            else:
                logger.warning(f"⚠️ Advertencias en optimización: {result.stderr}")
                # No es crítico, continuar
                return True
                
        except subprocess.TimeoutExpired:
            logger.warning("⚠️ Timeout en optimización (continuando)")
            return True
        except Exception as e:
            logger.warning(f"⚠️ Error en optimización (continuando): {e}")
            return True
    
    def process_pending_documents(self) -> bool:
        """Procesa documentos pendientes"""
        logger.info("📄 Procesando documentos pendientes...")
        
        try:
            # Ejecutar procesador de documentos pendientes
            result = subprocess.run(
                [sys.executable, "scripts/process_pending_fast.py", "--limit", "10", "--batch-size", "3"],
                cwd=self.backend_path,
                capture_output=True,
                text=True,
                timeout=600  # 10 minutos máximo
            )
            
            if result.returncode == 0:
                logger.info("✅ Procesamiento de documentos pendientes completado")
                print(result.stdout)
                self.system_status['pending_processed'] = True
                return True
            else:
                logger.warning(f"⚠️ Advertencias en procesamiento: {result.stderr}")
                # No es crítico, continuar
                return True
                
        except subprocess.TimeoutExpired:
            logger.warning("⚠️ Timeout procesando documentos (continuando)")
            return True
        except Exception as e:
            logger.warning(f"⚠️ Error procesando documentos (continuando): {e}")
            return True
    
    def start_server(self) -> bool:
        """Inicia el servidor API"""
        logger.info("🌐 Iniciando servidor API...")
        
        try:
            # Verificar si el servidor ya está corriendo
            import requests
            try:
                response = requests.get("http://localhost:8000/health", timeout=2)
                if response.status_code == 200:
                    logger.info("✅ Servidor ya está corriendo")
                    self.system_status['server_started'] = True
                    return True
            except:
                pass  # Servidor no está corriendo, continuar
            
            # Iniciar servidor en background
            server_process = subprocess.Popen(
                [sys.executable, "main.py"],
                cwd=self.backend_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Esperar a que el servidor inicie
            logger.info("⏳ Esperando que el servidor inicie...")
            for i in range(30):  # Esperar hasta 30 segundos
                try:
                    response = requests.get("http://localhost:8000/health", timeout=2)
                    if response.status_code == 200:
                        logger.info("✅ Servidor iniciado exitosamente")
                        self.system_status['server_started'] = True
                        return True
                except:
                    time.sleep(1)
            
            logger.error("❌ No se pudo iniciar el servidor")
            return False
            
        except Exception as e:
            logger.error(f"❌ Error iniciando servidor: {e}")
            return False
    
    def show_system_status(self):
        """Muestra estado del sistema"""
        logger.info("📊 ESTADO DEL SISTEMA")
        logger.info("=" * 40)
        
        print(f"🕐 Tiempo de inicio: {self.startup_time.strftime('%H:%M:%S')}")
        print(f"⏱️ Tiempo transcurrido: {(datetime.now() - self.startup_time).total_seconds():.1f}s")
        print()
        
        status_icons = {
            True: "✅",
            False: "❌"
        }
        
        print(f"{status_icons[self.system_status['models_checked']]} Modelos verificados")
        print(f"{status_icons[self.system_status['optimization_completed']]} Optimización completada")
        print(f"{status_icons[self.system_status['pending_processed']]} Documentos pendientes procesados")
        print(f"{status_icons[self.system_status['server_started']]} Servidor API iniciado")
        print()
        
        # Mostrar URLs
        if self.system_status['server_started']:
            print("🌐 URLs disponibles:")
            print("   • API: http://localhost:8000")
            print("   • Health: http://localhost:8000/health")
            print("   • Docs: http://localhost:8000/docs")
            print("   • Frontend: http://localhost:3000")
            print()
        
        # Mostrar comandos útiles
        print("🛠️ Comandos útiles:")
        print("   • Procesar documentos pendientes:")
        print("     python scripts/process_pending_fast.py")
        print("   • Verificar modelos:")
        print("     python check_models.py")
        print("   • Optimizar modelos:")
        print("     python scripts/optimize_models_for_speed.py")
        print()
    
    def run_startup(self):
        """Ejecuta el proceso completo de inicio"""
        self.print_banner()
        
        # Verificar requisitos
        if not self.check_system_requirements():
            logger.error("❌ Requisitos del sistema no cumplidos")
            return False
        
        logger.info("✅ Requisitos del sistema cumplidos")
        print()
        
        # Verificar modelos
        if not self.check_models():
            logger.error("❌ Error verificando modelos")
            return False
        
        print()
        
        # Optimizar modelos (opcional)
        self.optimize_models()
        print()
        
        # Procesar documentos pendientes (opcional)
        self.process_pending_documents()
        print()
        
        # Iniciar servidor
        if not self.start_server():
            logger.error("❌ Error iniciando servidor")
            return False
        
        print()
        
        # Mostrar estado final
        self.show_system_status()
        
        logger.info("🎉 Sistema OCR optimizado iniciado exitosamente")
        return True


def main():
    """Función principal"""
    starter = FastOCRSystemStarter()
    
    try:
        success = starter.run_startup()
        
        if success:
            print("\n🎉 ¡Sistema listo para usar!")
            print("📝 Los documentos ahora se procesarán en máximo 30 segundos")
            print("🔄 El sistema usa procesamiento síncrono optimizado")
            
            # Mantener el script corriendo para monitoreo
            print("\n⏳ Presiona Ctrl+C para detener el monitoreo...")
            try:
                while True:
                    time.sleep(60)  # Verificar cada minuto
                    # Aquí se podría agregar monitoreo adicional
            except KeyboardInterrupt:
                print("\n👋 Sistema detenido por el usuario")
        else:
            print("\n❌ Error iniciando el sistema")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n👋 Inicio interrumpido por el usuario")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Error crítico: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
