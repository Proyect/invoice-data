#!/usr/bin/env python3
"""
Script de pruebas para el frontend del sistema OCR
Verifica la compilación, componentes y funcionalidad
"""

import os
import sys
import subprocess
import time
import requests
import json
from pathlib import Path

def print_header(title):
    """Imprime un encabezado formateado"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def print_status(test_name, success, details=""):
    """Imprime el estado de una prueba"""
    status = "[PASS]" if success else "[FAIL]"
    print(f"{status} {test_name}")
    if details:
        print(f"    {details}")

def run_command(command, cwd=None, timeout=60):
    """Ejecuta un comando y retorna el resultado"""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            cwd=cwd, 
            capture_output=True, 
            text=True, 
            timeout=timeout
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Timeout"
    except Exception as e:
        return False, "", str(e)

def test_node_environment():
    """Prueba el entorno Node.js"""
    print_header("PRUEBAS DEL ENTORNO NODE.JS")
    
    # Verificar Node.js
    success, stdout, stderr = run_command("node --version")
    if success:
        print_status("Node.js instalado", True, stdout.strip())
    else:
        print_status("Node.js instalado", False, stderr)
        return False
    
    # Verificar npm
    success, stdout, stderr = run_command("npm --version")
    if success:
        print_status("npm disponible", True, stdout.strip())
    else:
        print_status("npm disponible", False, stderr)
        return False
    
    return True

def test_dependencies():
    """Prueba las dependencias del frontend"""
    print_header("PRUEBAS DE DEPENDENCIAS FRONTEND")
    
    # Verificar package.json
    if not os.path.exists("package.json"):
        print_status("Archivo package.json", False, "No encontrado")
        return False
    
    print_status("Archivo package.json", True, "Encontrado")
    
    # Verificar node_modules
    if not os.path.exists("node_modules"):
        print_status("node_modules", False, "No encontrado - ejecuta 'npm install'")
        return False
    
    print_status("node_modules", True, "Directorio encontrado")
    
    # Verificar dependencias críticas
    critical_deps = [
        "react",
        "react-dom",
        "@mui/material",
        "@mui/icons-material",
        "react-router-dom",
        "axios",
        "react-hot-toast"
    ]
    
    all_deps_ok = True
    for dep in critical_deps:
        dep_path = os.path.join("node_modules", dep)
        if os.path.exists(dep_path):
            print_status(f"Dependencia {dep}", True)
        else:
            print_status(f"Dependencia {dep}", False, "No encontrada")
            all_deps_ok = False
    
    return all_deps_ok

def test_typescript_compilation():
    """Prueba la compilación de TypeScript"""
    print_header("PRUEBAS DE COMPILACIÓN TYPESCRIPT")
    
    # Verificar tsconfig.json
    if not os.path.exists("tsconfig.json"):
        print_status("tsconfig.json", False, "No encontrado")
        return False
    
    print_status("tsconfig.json", True, "Encontrado")
    
    # Ejecutar verificación de tipos
    success, stdout, stderr = run_command("npx tsc --noEmit")
    if success:
        print_status("Verificación de tipos", True, "Sin errores de TypeScript")
    else:
        print_status("Verificación de tipos", False, stderr)
        return False
    
    return True

def test_build_process():
    """Prueba el proceso de construcción"""
    print_header("PRUEBAS DE CONSTRUCCIÓN")
    
    # Limpiar build anterior si existe
    if os.path.exists("build"):
        import shutil
        shutil.rmtree("build")
        print_status("Limpieza de build anterior", True)
    
    # Ejecutar build
    success, stdout, stderr = run_command("npm run build", timeout=120)
    if success:
        print_status("Construcción exitosa", True, "Build completado")
        
        # Verificar archivos generados
        build_files = [
            "build/index.html",
            "build/static/js",
            "build/static/css"
        ]
        
        for file_path in build_files:
            if os.path.exists(file_path):
                print_status(f"Archivo {file_path}", True)
            else:
                print_status(f"Archivo {file_path}", False, "No generado")
        
        return True
    else:
        print_status("Construcción exitosa", False, stderr)
        return False

def test_linting():
    """Prueba el linting del código"""
    print_header("PRUEBAS DE LINTING")
    
    # Verificar si ESLint está configurado
    if os.path.exists(".eslintrc.json") or "eslint" in open("package.json").read():
        success, stdout, stderr = run_command("npm run lint", timeout=60)
        if success:
            print_status("ESLint", True, "Sin errores de linting")
        else:
            print_status("ESLint", False, stderr)
            return False
    else:
        print_status("ESLint", True, "No configurado (opcional)")
    
    return True

def test_component_imports():
    """Prueba las importaciones de componentes"""
    print_header("PRUEBAS DE IMPORTACIONES")
    
    # Verificar archivos de componentes principales
    main_components = [
        "src/App.tsx",
        "src/pages/Login.tsx",
        "src/pages/Dashboard.tsx",
        "src/pages/DocumentList.tsx",
        "src/pages/DocumentUpload.tsx",
        "src/components/Navbar.tsx",
        "src/contexts/StableAuthContext.tsx",
        "src/contexts/OptimizedDocumentContext.tsx"
    ]
    
    all_components_ok = True
    for component in main_components:
        if os.path.exists(component):
            print_status(f"Componente {component}", True)
        else:
            print_status(f"Componente {component}", False, "No encontrado")
            all_components_ok = False
    
    return all_components_ok

def test_api_integration():
    """Prueba la integración con la API"""
    print_header("PRUEBAS DE INTEGRACIÓN API")
    
    # Verificar archivo de configuración de API
    api_file = "src/services/api.ts"
    if not os.path.exists(api_file):
        print_status("Archivo api.ts", False, "No encontrado")
        return False
    
    print_status("Archivo api.ts", True, "Encontrado")
    
    # Verificar configuración de URL de API
    with open(api_file, 'r', encoding='utf-8') as f:
        content = f.read()
        if "REACT_APP_API_URL" in content:
            print_status("Configuración API URL", True, "Variable de entorno configurada")
        else:
            print_status("Configuración API URL", False, "Variable de entorno no encontrada")
    
    return True

def test_environment_variables():
    """Prueba las variables de entorno"""
    print_header("PRUEBAS DE VARIABLES DE ENTORNO")
    
    # Verificar archivo .env.local
    env_files = [".env.local", ".env", ".env.example"]
    env_found = False
    
    for env_file in env_files:
        if os.path.exists(env_file):
            print_status(f"Archivo {env_file}", True, "Encontrado")
            env_found = True
            
            # Verificar variables importantes
            with open(env_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if "REACT_APP_API_URL" in content:
                    print_status("REACT_APP_API_URL", True, "Configurada")
                else:
                    print_status("REACT_APP_API_URL", False, "No configurada")
        else:
            print_status(f"Archivo {env_file}", False, "No encontrado")
    
    if not env_found:
        print_status("Variables de entorno", False, "Ningún archivo de entorno encontrado")
        return False
    
    return True

def test_development_server():
    """Prueba el servidor de desarrollo"""
    print_header("PRUEBAS DE SERVIDOR DE DESARROLLO")
    
    # Verificar que el puerto 3000 esté disponible
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        if response.status_code == 200:
            print_status("Servidor de desarrollo", True, "Corriendo en puerto 3000")
        else:
            print_status("Servidor de desarrollo", False, f"Status: {response.status_code}")
    except requests.exceptions.RequestException:
        print_status("Servidor de desarrollo", False, "No está corriendo")
        print("    Para iniciar: npm start")
    
    return True

def test_production_build():
    """Prueba el build de producción"""
    print_header("PRUEBAS DE BUILD DE PRODUCCIÓN")
    
    # Verificar que el build existe
    if not os.path.exists("build"):
        print_status("Directorio build", False, "No existe - ejecuta 'npm run build'")
        return False
    
    print_status("Directorio build", True, "Encontrado")
    
    # Verificar archivos críticos del build
    critical_files = [
        "build/index.html",
        "build/static/js",
        "build/static/css"
    ]
    
    all_files_ok = True
    for file_path in critical_files:
        if os.path.exists(file_path):
            print_status(f"Archivo {file_path}", True)
        else:
            print_status(f"Archivo {file_path}", False, "No encontrado")
            all_files_ok = False
    
    return all_files_ok

def main():
    """Función principal"""
    print_header("SISTEMA DE PRUEBAS FRONTEND - OCR DOCUMENT PROCESSOR")
    print(f"Directorio de trabajo: {os.getcwd()}")
    print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Cambiar al directorio del frontend
    frontend_dir = Path(__file__).parent
    os.chdir(frontend_dir)
    
    # Ejecutar todas las pruebas
    tests = [
        ("Entorno Node.js", test_node_environment),
        ("Dependencias", test_dependencies),
        ("Compilación TypeScript", test_typescript_compilation),
        ("Proceso de construcción", test_build_process),
        ("Linting", test_linting),
        ("Importaciones de componentes", test_component_imports),
        ("Integración API", test_api_integration),
        ("Variables de entorno", test_environment_variables),
        ("Servidor de desarrollo", test_development_server),
        ("Build de producción", test_production_build),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print_status(test_name, False, f"Error: {str(e)}")
            results[test_name] = False
    
    # Resumen final
    print_header("RESUMEN DE PRUEBAS FRONTEND")
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    print(f"Pruebas pasadas: {passed}/{total}")
    print(f"Porcentaje de éxito: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print_status("RESULTADO GENERAL", True, "Todas las pruebas pasaron")
        return 0
    else:
        print_status("RESULTADO GENERAL", False, f"{total-passed} pruebas fallaron")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
