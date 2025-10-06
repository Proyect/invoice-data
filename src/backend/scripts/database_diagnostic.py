#!/usr/bin/env python3
"""
Script de diagnóstico de base de datos
Verifica y corrige problemas de conexión y estructura
"""

import sys
import os
sys.path.append('/app')

def check_database_connection():
    """Verificar conexión a la base de datos"""
    print("🔌 Verificando conexión a base de datos...")
    
    try:
        from database import get_db
        from sqlalchemy import text
        
        db = next(get_db())
        
        # Test de conexión básico
        result = db.execute(text("SELECT 1"))
        print("   ✅ Conexión básica exitosa")
        
        return db
        
    except Exception as e:
        print(f"   ❌ Error de conexión: {e}")
        return None

def check_database_tables():
    """Verificar que las tablas existan"""
    print("\n📋 Verificando tablas de la base de datos...")
    
    try:
        db = check_database_connection()
        if not db:
            return False
            
        from sqlalchemy import text
        
        # Listar tablas
        result = db.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """))
        
        tables = [row[0] for row in result]
        print(f"   📊 Tablas encontradas: {len(tables)}")
        
        for table in tables:
            print(f"   ✅ {table}")
            
        # Verificar tabla users específicamente
        if 'users' in tables:
            result = db.execute(text("SELECT COUNT(*) FROM users"))
            user_count = result.scalar()
            print(f"   👥 Usuarios en tabla: {user_count}")
        else:
            print("   ❌ Tabla 'users' no encontrada")
            
        return True
        
    except Exception as e:
        print(f"   ❌ Error verificando tablas: {e}")
        return False

def check_database_schema():
    """Verificar esquema de la base de datos"""
    print("\n🏗️ Verificando esquema de base de datos...")
    
    try:
        db = check_database_connection()
        if not db:
            return False
            
        from sqlalchemy import text
        
        # Verificar estructura de tabla users
        result = db.execute(text("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'users'
            ORDER BY ordinal_position
        """))
        
        columns = result.fetchall()
        print(f"   📊 Columnas en tabla 'users': {len(columns)}")
        
        for col_name, data_type, is_nullable in columns:
            nullable = "NULL" if is_nullable == "YES" else "NOT NULL"
            print(f"   ✅ {col_name}: {data_type} ({nullable})")
            
        return True
        
    except Exception as e:
        print(f"   ❌ Error verificando esquema: {e}")
        return False

def test_user_operations():
    """Probar operaciones de usuario"""
    print("\n👤 Probando operaciones de usuario...")
    
    try:
        db = check_database_connection()
        if not db:
            return False
            
        from sqlalchemy import text
        
        # Buscar usuario testuser
        result = db.execute(text("""
            SELECT id, username, email, full_name, disabled
            FROM users 
            WHERE username = 'testuser'
        """))
        
        user = result.fetchone()
        
        if user:
            user_id, username, email, full_name, disabled = user
            print(f"   ✅ Usuario encontrado:")
            print(f"      ID: {user_id}")
            print(f"      Username: {username}")
            print(f"      Email: {email}")
            print(f"      Full Name: {full_name}")
            print(f"      Disabled: {disabled}")
            return True
        else:
            print("   ❌ Usuario 'testuser' no encontrado")
            return False
            
    except Exception as e:
        print(f"   ❌ Error en operaciones de usuario: {e}")
        return False

def check_documents_table():
    """Verificar tabla de documentos"""
    print("\n📄 Verificando tabla de documentos...")
    
    try:
        db = check_database_connection()
        if not db:
            return False
            
        from sqlalchemy import text
        
        # Verificar si existe tabla documents
        result = db.execute(text("""
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_name = 'documents'
        """))
        
        table_exists = result.scalar() > 0
        
        if table_exists:
            # Contar documentos
            result = db.execute(text("SELECT COUNT(*) FROM documents"))
            doc_count = result.scalar()
            print(f"   ✅ Tabla 'documents' existe: {doc_count} documentos")
            
            # Mostrar algunos documentos de ejemplo
            if doc_count > 0:
                result = db.execute(text("""
                    SELECT id, original_filename, document_type, status, created_at
                    FROM documents 
                    ORDER BY created_at DESC 
                    LIMIT 3
                """))
                
                docs = result.fetchall()
                print("   📋 Documentos recientes:")
                for doc in docs:
                    doc_id, filename, doc_type, status, created_at = doc
                    print(f"      📄 {filename} ({doc_type}) - {status}")
                    
            return True
        else:
            print("   ❌ Tabla 'documents' no existe")
            return False
            
    except Exception as e:
        print(f"   ❌ Error verificando documentos: {e}")
        return False

def main():
    """Función principal de diagnóstico"""
    print("🔍 DIAGNÓSTICO DE BASE DE DATOS")
    print("=" * 50)
    
    checks = [
        ("Conexión", check_database_connection),
        ("Tablas", check_database_tables),
        ("Esquema", check_database_schema),
        ("Operaciones de Usuario", test_user_operations),
        ("Tabla de Documentos", check_documents_table)
    ]
    
    results = []
    
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"   ❌ Error en {name}: {e}")
            results.append((name, False))
    
    # Resumen final
    print("\n" + "=" * 50)
    print("📊 RESUMEN DE DIAGNÓSTICO:")
    
    passed = 0
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 RESULTADO: {passed}/{total} checks pasaron")
    
    if passed == total:
        print("🎉 ¡Base de datos completamente funcional!")
        return 0
    else:
        print("⚠️ Base de datos con problemas menores")
        return 1

if __name__ == "__main__":
    sys.exit(main())





























