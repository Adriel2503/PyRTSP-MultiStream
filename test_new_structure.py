#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de prueba para la nueva estructura de carpetas por modos
Verifica que PathManager y SessionManager funcionen correctamente
"""

import sys
import os
import json
from pathlib import Path

# Agregar src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_path_manager():
    """Probar el PathManager con diferentes modos"""
    print("🔍 PROBANDO PATHMANAGER...")
    
    try:
        from src.utils.path_manager import get_path_manager
        from src.core.mode_manager import InspectionMode
        
        path_manager = get_path_manager()
        
        # Probar cada modo
        for mode in [InspectionMode.PRO, InspectionMode.RAPIDO, InspectionMode.BASICO]:
            print(f"\n📋 Probando modo: {mode.name}")
            
            # Configurar modo
            path_manager.set_current_mode(mode)
            
            # Generar rutas
            recording_path = path_manager.generate_recording_filename()
            capture_path = path_manager.generate_capture_filename()
            session_path = path_manager.generate_session_filename()
            
            print(f"  📹 Grabación: {recording_path}")
            print(f"  📷 Captura: {capture_path}")
            print(f"  📄 Sesión: {session_path}")
            
            # Verificar que las carpetas existen
            for path in [recording_path, capture_path, session_path]:
                parent_dir = os.path.dirname(path)
                if os.path.exists(parent_dir):
                    print(f"  ✅ Directorio existe: {parent_dir}")
                else:
                    print(f"  ❌ Directorio NO existe: {parent_dir}")
                    return False
        
        print("\n✅ PathManager funcionando correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error en PathManager: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_session_manager():
    """Probar el SessionManager"""
    print("\n🔍 PROBANDO SESSIONMANAGER...")
    
    try:
        from src.utils.session_manager import get_session_manager
        from src.core.mode_manager import InspectionMode
        
        session_manager = get_session_manager()
        
        # Iniciar sesión
        session_id = session_manager.start_session(
            InspectionMode.PRO, 
            {"test": "data"}
        )
        print(f"  📋 Sesión iniciada: {session_id}")
        
        # Simular datos de inspección
        inspection_data = {
            "operario": "Test User",
            "ciudad": "Test City",
            "ref_tramo": "TRAMO-001"
        }
        session_manager.update_inspection_data(inspection_data)
        print("  📝 Datos de inspección actualizados")
        
        # Simular archivos generados
        session_manager.add_recording("test_recording.mp4")
        session_manager.add_capture("test_capture.jpg")
        print("  📁 Archivos simulados registrados")
        
        # Obtener info de sesión
        session_info = session_manager.get_current_session_info()
        print(f"  📊 Archivos registrados: {len(session_info['files_generated']['recordings'])} grabaciones, {len(session_info['files_generated']['captures'])} capturas")
        
        # Finalizar sesión
        success = session_manager.end_session()
        if success:
            print("  ✅ Sesión finalizada y guardada correctamente")
        else:
            print("  ❌ Error finalizando sesión")
            return False
        
        print("\n✅ SessionManager funcionando correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error en SessionManager: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_directory_structure():
    """Verificar que la estructura de directorios se crea correctamente"""
    print("\n🔍 VERIFICANDO ESTRUCTURA DE DIRECTORIOS...")
    
    expected_structure = {
        "metadatos": {
            "profesional": ["grabaciones", "capturas", "reportes", "sesiones"],
            "rapido": ["grabaciones", "capturas", "reportes", "sesiones"],
            "basico": ["grabaciones", "capturas", "reportes", "sesiones"]
        }
    }
    
    try:
        for mode_folder, subdirs in expected_structure["metadatos"].items():
            mode_path = os.path.join("metadatos", mode_folder)
            print(f"\n📁 Verificando modo: {mode_folder}")
            
            if not os.path.exists(mode_path):
                print(f"  ❌ Carpeta de modo no existe: {mode_path}")
                return False
            
            for subdir in subdirs:
                full_path = os.path.join(mode_path, subdir)
                if os.path.exists(full_path):
                    print(f"  ✅ {subdir}/")
                else:
                    print(f"  ❌ {subdir}/ NO EXISTE")
                    return False
        
        print("\n✅ Estructura de directorios correcta")
        return True
        
    except Exception as e:
        print(f"❌ Error verificando estructura: {e}")
        return False

def test_session_json_format():
    """Verificar que los archivos JSON de sesión se generan correctamente"""
    print("\n🔍 VERIFICANDO FORMATO JSON DE SESIÓN...")
    
    try:
        # Buscar archivos JSON en sesiones/
        session_files = []
        for root, dirs, files in os.walk("metadatos"):
            if "sesiones" in root:
                for file in files:
                    if file.endswith(".json"):
                        session_files.append(os.path.join(root, file))
        
        if not session_files:
            print("  ⚠️ No se encontraron archivos de sesión (ejecuta primero el test de SessionManager)")
            return True
        
        # Verificar el último archivo
        latest_session = max(session_files, key=os.path.getmtime)
        print(f"  📄 Verificando: {latest_session}")
        
        with open(latest_session, 'r', encoding='utf-8') as f:
            session_data = json.load(f)
        
        # Verificar campos requeridos
        required_fields = [
            "session_id", "mode", "start_time", "end_time",
            "inspection_data", "overlays_used", "files_generated", "session_stats"
        ]
        
        for field in required_fields:
            if field in session_data:
                print(f"  ✅ {field}")
            else:
                print(f"  ❌ Campo faltante: {field}")
                return False
        
        print(f"  📊 Modo: {session_data['mode']}")
        print(f"  📊 Duración: {session_data['session_stats']['duration_seconds']:.1f}s")
        print(f"  📊 Archivos: {session_data['session_stats']['recordings_count']} grabaciones, {session_data['session_stats']['captures_count']} capturas")
        
        print("\n✅ Formato JSON de sesión correcto")
        return True
        
    except Exception as e:
        print(f"❌ Error verificando JSON: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Ejecutar todas las pruebas"""
    print("🚀 PROBANDO NUEVA ESTRUCTURA DE CARPETAS POR MODOS")
    print("=" * 60)
    
    tests = [
        ("PathManager", test_path_manager),
        ("SessionManager", test_session_manager), 
        ("Estructura de Directorios", test_directory_structure),
        ("Formato JSON", test_session_json_format)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n🧪 EJECUTANDO: {test_name}")
        print("-" * 40)
        results[test_name] = test_func()
    
    # Resumen final
    print("\n" + "=" * 60)
    print("📋 RESUMEN DE PRUEBAS:")
    
    all_passed = True
    for test_name, passed in results.items():
        status = "✅ PASÓ" if passed else "❌ FALLÓ"
        print(f"  {test_name}: {status}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n🎉 ¡TODAS LAS PRUEBAS PASARON!")
        print("✅ La nueva estructura está lista para usar")
    else:
        print("\n⚠️ Algunas pruebas fallaron")
        print("❌ Revisa los errores antes de usar en producción")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)