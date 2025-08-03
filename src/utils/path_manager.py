# -*- coding: utf-8 -*-
"""
Gestor de rutas inteligente para organización por modos de inspección
Gestiona la estructura metadatos/ con subdirectorios por modo
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict

from .logger import setup_logger
from ..core.mode_manager import InspectionMode

logger = setup_logger("PathManager")

class PathManager:
    """Gestor inteligente de rutas por modo de inspección"""
    
    def __init__(self):
        self.base_dir = "metadatos"
        self.mode_folders = {
            InspectionMode.PRO: "profesional",
            InspectionMode.RAPIDO: "rapido", 
            InspectionMode.BASICO: "basico"
        }
        self.current_mode = None
        
        # Crear estructura base
        self._ensure_directory_structure()
        logger.info("PathManager inicializado con estructura de carpetas por modo")
    
    def set_current_mode(self, mode: InspectionMode):
        """Configurar el modo actual para determinar rutas"""
        self.current_mode = mode
        mode_name = self.mode_folders[mode]
        logger.info(f"PathManager configurado para modo: {mode.value} → {mode_name}/")
        
        # Asegurar que existan las carpetas para este modo
        self._ensure_mode_directories(mode)
    
    def get_current_mode_folder(self) -> str:
        """Obtener el nombre de carpeta del modo actual"""
        if self.current_mode is None:
            logger.warning("No hay modo configurado, usando 'profesional' por defecto")
            return "profesional"
        return self.mode_folders[self.current_mode]
    
    def get_recording_path(self, filename: Optional[str] = None) -> str:
        """Obtener ruta para grabaciones según el modo actual"""
        mode_folder = self.get_current_mode_folder()
        base_path = os.path.join(self.base_dir, mode_folder, "grabaciones")
        
        if filename:
            return os.path.join(base_path, filename)
        return base_path
    
    def get_capture_path(self, filename: Optional[str] = None) -> str:
        """Obtener ruta para capturas según el modo actual"""
        mode_folder = self.get_current_mode_folder() 
        base_path = os.path.join(self.base_dir, mode_folder, "capturas")
        
        if filename:
            return os.path.join(base_path, filename)
        return base_path
    
    def get_reports_path(self, filename: Optional[str] = None) -> str:
        """Obtener ruta para reportes según el modo actual"""
        mode_folder = self.get_current_mode_folder()
        base_path = os.path.join(self.base_dir, mode_folder, "reportes")
        
        if filename:
            return os.path.join(base_path, filename)
        return base_path
    
    def get_sessions_path(self, filename: Optional[str] = None) -> str:
        """Obtener ruta para metadatos de sesión según el modo actual"""
        mode_folder = self.get_current_mode_folder()
        base_path = os.path.join(self.base_dir, mode_folder, "sesiones")
        
        if filename:
            return os.path.join(base_path, filename)
        return base_path
    
    def generate_recording_filename(self) -> str:
        """Generar nombre de archivo para grabación con timestamp"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"inspeccion_{timestamp}.mp4"
        return self.get_recording_path(filename)
    
    def generate_capture_filename(self) -> str:
        """Generar nombre de archivo para captura con timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"captura_{timestamp}.jpg"
        return self.get_capture_path(filename)
    
    def generate_session_filename(self) -> str:
        """Generar nombre de archivo para metadatos de sesión"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"sesion_{timestamp}.json"
        return self.get_sessions_path(filename)
    
    def _ensure_directory_structure(self):
        """Crear estructura completa de directorios"""
        logger.info("Creando estructura de directorios...")
        
        for mode, folder_name in self.mode_folders.items():
            mode_path = os.path.join(self.base_dir, folder_name)
            
            # Crear subdirectorios para cada modo
            subdirs = ["grabaciones", "capturas", "reportes", "sesiones"]
            for subdir in subdirs:
                full_path = os.path.join(mode_path, subdir)
                os.makedirs(full_path, exist_ok=True)
                logger.debug(f"✅ Directorio creado: {full_path}")
        
        logger.info("✅ Estructura de directorios creada exitosamente")
    
    def _ensure_mode_directories(self, mode: InspectionMode):
        """Asegurar que existan los directorios para un modo específico"""
        folder_name = self.mode_folders[mode]
        mode_path = os.path.join(self.base_dir, folder_name)
        
        subdirs = ["grabaciones", "capturas", "reportes", "sesiones"]
        for subdir in subdirs:
            full_path = os.path.join(mode_path, subdir)
            os.makedirs(full_path, exist_ok=True)
    
    def get_directory_info(self) -> Dict[str, Dict[str, str]]:
        """Obtener información de todos los directorios por modo"""
        info = {}
        
        for mode, folder_name in self.mode_folders.items():
            mode_path = os.path.join(self.base_dir, folder_name)
            info[mode.value] = {
                "folder": folder_name,
                "grabaciones": os.path.join(mode_path, "grabaciones"),
                "capturas": os.path.join(mode_path, "capturas"), 
                "reportes": os.path.join(mode_path, "reportes"),
                "sesiones": os.path.join(mode_path, "sesiones")
            }
        
        return info
    
    def get_current_session_id(self) -> str:
        """Obtener ID de sesión actual basado en timestamp"""
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def get_capture_path(self, filename: str) -> str:
        """Obtener ruta completa de un archivo de captura"""
        captures_dir = os.path.join(self.base_dir, self.get_current_mode_folder(), "capturas")
        return os.path.join(captures_dir, filename)
    
    def get_reports_path(self, filename: str) -> str:
        """Obtener ruta completa de un archivo de reporte"""
        reports_dir = os.path.join(self.base_dir, self.get_current_mode_folder(), "reportes")
        return os.path.join(reports_dir, filename)

# Instancia global
_path_manager = None

def get_path_manager() -> PathManager:
    """Obtener instancia global del PathManager"""
    global _path_manager
    if _path_manager is None:
        _path_manager = PathManager()
    return _path_manager