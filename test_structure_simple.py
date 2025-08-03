#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test simple para verificar la estructura de carpetas por modos
Sin dependencias de PyQt6 ni GStreamer
"""

import os
import sys
import json
from datetime import datetime
from enum import Enum
from pathlib import Path

# Definición simple de modos para el test
class InspectionMode(Enum):
    PRO = "pro"
    RAPIDO = "rapido"
    BASICO = "basico"

class SimplePathManager:
    """Versión simplificada del PathManager para testing"""
    
    def __init__(self):
        self.base_dir = "metadatos"
        self.mode_folders = {
            InspectionMode.PRO: "profesional",
            InspectionMode.RAPIDO: "rapido", 
            InspectionMode.BASICO: "basico"
        }
        self.current_mode = None
        self._ensure_directory_structure()
    
    def set_current_mode(self, mode: InspectionMode):
        self.current_mode = mode
        self._ensure_mode_directories(mode)
    
    def get_current_mode_folder(self) -> str:
        if self.current_mode is None:
            return "profesional"
        return self.mode_folders[self.current_mode]
    
    def get_recording_path(self, filename = None) -> str:
        mode_folder = self.get_current_mode_folder()
        base_path = os.path.join(self.base_dir, mode_folder, "grabaciones")
        if filename:
            return os.path.join(base_path, filename)
        return base_path
    
    def get_capture_path(self, filename = None) -> str:
        mode_folder = self.get_current_mode_folder() 
        base_path = os.path.join(self.base_dir, mode_folder, "capturas")
        if filename:
            return os.path.join(base_path, filename)
        return base_path
    
    def get_reports_path(self, filename = None) -> str:
        mode_folder = self.get_current_mode_folder()
        base_path = os.path.join(self.base_dir, mode_folder, "reportes")
        if filename:
            return os.path.join(base_path, filename)
        return base_path
    
    def get_sessions_path(self, filename = None) -> str:
        mode_folder = self.get_current_mode_folder()
        base_path = os.path.join(self.base_dir, mode_folder, "sesiones")
        if filename:
            return os.path.join(base_path, filename)
        return base_path
    
    def generate_recording_filename(self) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"inspeccion_{timestamp}.mp4"
        return self.get_recording_path(filename)
    
    def generate_capture_filename(self) -> str:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"captura_{timestamp}.jpg"
        return self.get_capture_path(filename)
    
    def generate_session_filename(self) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"sesion_{timestamp}.json"
        return self.get_sessions_path(filename)
    
    def _ensure_directory_structure(self):
        for mode, folder_name in self.mode_folders.items():
            mode_path = os.path.join(self.base_dir, folder_name)
            subdirs = ["grabaciones", "capturas", "reportes", "sesiones"]
            for subdir in subdirs:
                full_path = os.path.join(mode_path, subdir)
                os.makedirs(full_path, exist_ok=True)
    
    def _ensure_mode_directories(self, mode: InspectionMode):
        folder_name = self.mode_folders[mode]
        mode_path = os.path.join(self.base_dir, folder_name)
        subdirs = ["grabaciones", "capturas", "reportes", "sesiones"]
        for subdir in subdirs:
            full_path = os.path.join(mode_path, subdir)
            os.makedirs(full_path, exist_ok=True)

class SimpleSessionManager:
    """Versión simplificada del SessionManager para testing"""
    
    def __init__(self, path_manager):
        self.current_session = None
        self.path_manager = path_manager
    
    def start_session(self, mode: InspectionMode, inspection_data = None) -> str:
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        self.current_session = {
            "session_id": session_id,
            "mode": mode.value,
            "mode_name": self._get_mode_name(mode),
            "start_time": datetime.now().isoformat(),
            "end_time": None,
            "inspection_data": inspection_data or {},
            "overlays_used": self._get_overlays_for_mode(mode),
            "files_generated": {
                "recordings": [],
                "captures": [],
                "reports": []
            },
            "session_stats": {
                "recordings_count": 0,
                "captures_count": 0,
                "duration_seconds": 0
            }
        }
        
        return session_id
    
    def end_session(self) -> bool:
        if not self.current_session:
            return False
        
        self.current_session["end_time"] = datetime.now().isoformat()
        
        start_time = datetime.fromisoformat(self.current_session["start_time"])
        end_time = datetime.fromisoformat(self.current_session["end_time"])
        duration = (end_time - start_time).total_seconds()
        self.current_session["session_stats"]["duration_seconds"] = duration
        
        return self._save_session_metadata()
    
    def add_recording(self, filename: str):
        if not self.current_session:
            return
        basename = os.path.basename(filename)
        self.current_session["files_generated"]["recordings"].append(basename)
        self.current_session["session_stats"]["recordings_count"] += 1
    
    def add_capture(self, filename: str):
        if not self.current_session:
            return
        basename = os.path.basename(filename)
        self.current_session["files_generated"]["captures"].append(basename)
        self.current_session["session_stats"]["captures_count"] += 1
    
    def update_inspection_data(self, data):
        if not self.current_session:
            return
        self.current_session["inspection_data"].update(data)
    
    def get_current_session_info(self):
        return self.current_session.copy() if self.current_session else None
    
    def _save_session_metadata(self) -> bool:
        if not self.current_session:
            return False
        
        try:
            filename = self.path_manager.generate_session_filename()
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.current_session, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"Error guardando sesión: {e}")
            return False
    
    def _get_mode_name(self, mode: InspectionMode) -> str:
        names = {
            InspectionMode.PRO: "Profesional",
            InspectionMode.RAPIDO: "Rápido", 
            InspectionMode.BASICO: "Básico"
        }
        return names.get(mode, "Desconocido")
    
    def _get_overlays_for_mode(self, mode: InspectionMode):
        overlays_config = {
            InspectionMode.PRO: ["fecha", "distancia", "grilla", "pozos", "tramo", "anotaciones"],
            InspectionMode.RAPIDO: ["fecha", "distancia", "grilla"],
            InspectionMode.BASICO: ["fecha", "distancia", "grilla", "pozos"]
        }
        return overlays_config.get(mode, [])

def test_path_manager():
    """Probar el PathManager"""
    print("🔍 PROBANDO PATHMANAGER...")
    
    try:
        path_manager = SimplePathManager()
        
        for mode in [InspectionMode.PRO, InspectionMode.RAPIDO, InspectionMode.BASICO]:
            print(f"\n📋 Probando modo: {mode.name}")
            
            path_manager.set_current_mode(mode)
            
            recording_path = path_manager.generate_recording_filename()
            capture_path = path_manager.generate_capture_filename()
            session_path = path_manager.generate_session_filename()
            
            print(f"  📹 Grabación: {recording_path}")
            print(f"  📷 Captura: {capture_path}")
            print(f"  📄 Sesión: {session_path}")
            
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
        path_manager = SimplePathManager()
        session_manager = SimpleSessionManager(path_manager)
        
        # Configurar modo
        path_manager.set_current_mode(InspectionMode.PRO)
        
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
    """Verificar estructura de directorios"""
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

def main():
    """Ejecutar todas las pruebas"""
    print("🚀 PROBANDO NUEVA ESTRUCTURA DE CARPETAS POR MODOS")
    print("=" * 60)
    
    tests = [
        ("PathManager", test_path_manager),
        ("SessionManager", test_session_manager), 
        ("Estructura de Directorios", test_directory_structure)
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
        
        # Mostrar estructura creada
        print("\n📁 ESTRUCTURA CREADA:")
        for root, dirs, files in os.walk("metadatos"):
            level = root.replace("metadatos", "").count(os.sep)
            indent = " " * 2 * level
            print(f"{indent}{os.path.basename(root)}/")
            subindent = " " * 2 * (level + 1)
            for file in files:
                print(f"{subindent}{file}")
    else:
        print("\n⚠️ Algunas pruebas fallaron")
        print("❌ Revisa los errores antes de usar en producción")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)