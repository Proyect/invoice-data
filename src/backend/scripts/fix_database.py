#!/usr/bin/env python3
"""
Script de reparación de base de datos
Corrige problemas comunes de estructura y datos
"""

import sys
import os
sys.path.append('/app')

def fix_database_structure():
    """Reparar estructura de la base de datos"""
    print("🔧 Reparando estructura de base de datos...")
    
    try:
        from database import get_db, engine
        from sqlalchemy import text
        
        db = next(get_db())
        
        # Verificar y crear tabla users si no existe
        print("   📋 Verificando tabla 'users'...")
        result = db.execute(text("""
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_name = 'users'
        """))
        
        if result.scalar() == 0:
            print("   🔨 Creando tabla 'users'...")
            db.execute(text("""
                CREATE TABLE users (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    username VARCHAR(50) UNIQUE NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    full_name VARCHAR(100) NOT NULL,
                    hashed_password VARCHAR(255) NOT NULL,
                    disabled BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            db.commit()
            print("   ✅ Tabla 'users' creada")
        else:
            print("   ✅ Tabla 'users' existe")
            
        # Verificar y crear tabla documents si no existe
        print("   📋 Verificando tabla 'documents'...")
        result = db.execute(text("""
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_name = 'documents'
        """))
        
        if result.scalar() == 0:
            print("   🔨 Creando tabla 'documents'...")
            db.execute(text("""
                CREATE TABLE documents (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    user_id UUID REFERENCES users(id),
                    original_filename VARCHAR(255) NOT NULL,
                    document_type VARCHAR(50) NOT NULL,
                    status VARCHAR(50) DEFAULT 'PENDING',
                    file_path VARCHAR(500),
                    extracted_data JSONB,
                    structured_data JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            db.commit()
            print("   ✅ Tabla 'documents' creada")
        else:
            print("   ✅ Tabla 'documents' existe")
            
        return True
        
    except Exception as e:
        print(f"   ❌ Error reparando estructura: {e}")
        return False

def fix_user_data():
    """Reparar datos de usuarios"""
    print("\n👤 Reparando datos de usuarios...")
    
    try:
        from database import get_db
        from sqlalchemy import text
        
        db = next(get_db())
        
        # Verificar si existe usuario testuser
        result = db.execute(text("""
            SELECT COUNT(*) FROM users WHERE username = 'testuser'
        """))
        
        if result.scalar() == 0:
            print("   🔨 Creando usuario 'testuser'...")
            
            # Hash de la contraseña 'testpassword'
            hashed_password = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4p3x8L2k4K"
            
            db.execute(text("""
                INSERT INTO users (username, email, full_name, hashed_password, disabled)
                VALUES ('testuser', 'test@example.com', 'Usuario de Prueba', :password, FALSE)
            """), {"password": hashed_password})
            
            db.commit()
            print("   ✅ Usuario 'testuser' creado")
        else:
            print("   ✅ Usuario 'testuser' existe")
            
        return True
        
    except Exception as e:
        print(f"   ❌ Error reparando usuarios: {e}")
        return False

def fix_document_data():
    """Reparar datos de documentos"""
    print("\n📄 Reparando datos de documentos...")
    
    try:
        from database import get_db
        from sqlalchemy import text
        
        db = next(get_db())
        
        # Verificar si hay documentos
        result = db.execute(text("SELECT COUNT(*) FROM documents"))
        doc_count = result.scalar()
        
        if doc_count == 0:
            print("   🔨 Creando documento de prueba...")
            
            # Obtener ID del usuario testuser
            result = db.execute(text("SELECT id FROM users WHERE username = 'testuser'"))
            user_id = result.scalar()
            
            if user_id:
                db.execute(text("""
                    INSERT INTO documents (user_id, original_filename, document_type, status, file_path, created_at)
                    VALUES (:user_id, 'test_invoice.jpg', 'INVOICE', 'COMPLETED', 'models/yolo_models/test_invoice.jpg', CURRENT_TIMESTAMP)
                """), {"user_id": user_id})
                
                db.commit()
                print("   ✅ Documento de prueba creado")
            else:
                print("   ⚠️ No se puede crear documento sin usuario")
        else:
            print(f"   ✅ {doc_count} documentos encontrados")
            
        return True
        
    except Exception as e:
        print(f"   ❌ Error reparando documentos: {e}")
        return False

def main():
    """Función principal de reparación"""
    print("🔧 REPARACIÓN DE BASE DE DATOS")
    print("=" * 50)
    
    fixes = [
        ("Estructura", fix_database_structure),
        ("Datos de Usuario", fix_user_data),
        ("Datos de Documentos", fix_document_data)
    ]
    
    results = []
    
    for name, fix_func in fixes:
        try:
            result = fix_func()
            results.append((name, result))
        except Exception as e:
            print(f"   ❌ Error en {name}: {e}")
            results.append((name, False))
    
    # Resumen final
    print("\n" + "=" * 50)
    print("📊 RESUMEN DE REPARACIÓN:")
    
    passed = 0
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 RESULTADO: {passed}/{total} reparaciones exitosas")
    
    if passed == total:
        print("🎉 ¡Base de datos reparada exitosamente!")
        return 0
    else:
        print("⚠️ Base de datos reparada parcialmente")
        return 1

if __name__ == "__main__":
    sys.exit(main())

