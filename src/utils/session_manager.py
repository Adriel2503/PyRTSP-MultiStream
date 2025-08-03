# -*- coding: utf-8 -*-
"""
Gestor de metadatos de sesión
Maneja la información de cada sesión de inspección con archivos JSON
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional

from .logger import setup_logger
from .path_manager import get_path_manager
from ..core.mode_manager import InspectionMode

logger = setup_logger("SessionManager")

class SessionManager:
    """Gestor de metadatos de sesión de inspección"""
    
    def __init__(self):
        self.current_session = None
        self.path_manager = get_path_manager()
        logger.info("SessionManager inicializado")
    
    def start_session(self, mode: InspectionMode, inspection_data: Optional[Dict] = None) -> str:
        """Iniciar nueva sesión de inspección"""
        session_id = self.path_manager.get_current_session_id()
        
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
        
        logger.info(f"🚀 Nueva sesión iniciada: {session_id} (modo: {mode.value})")
        return session_id
    
    def end_session(self) -> bool:
        """Finalizar sesión actual y guardar metadatos"""
        if not self.current_session:
            logger.warning("No hay sesión activa para finalizar")
            return False
        
        # Actualizar tiempo de fin
        self.current_session["end_time"] = datetime.now().isoformat()
        
        # Calcular duración
        start_time = datetime.fromisoformat(self.current_session["start_time"])
        end_time = datetime.fromisoformat(self.current_session["end_time"])
        duration = (end_time - start_time).total_seconds()
        self.current_session["session_stats"]["duration_seconds"] = duration
        
        # Guardar archivo JSON
        success = self._save_session_metadata()
        
        if success:
            session_id = self.current_session["session_id"]
            logger.info(f"✅ Sesión finalizada y guardada: {session_id}")
            self.current_session = None
        
        return success
    
    def add_recording(self, filename: str):
        """Registrar nueva grabación en la sesión actual"""
        if not self.current_session:
            logger.warning("No hay sesión activa para registrar grabación")
            return
        
        # Extraer solo el nombre del archivo
        basename = os.path.basename(filename)
        self.current_session["files_generated"]["recordings"].append(basename)
        self.current_session["session_stats"]["recordings_count"] += 1
        
        logger.info(f"📹 Grabación registrada en sesión: {basename}")
    
    def add_capture(self, filename: str):
        """Registrar nueva captura en la sesión actual"""
        if not self.current_session:
            logger.warning("No hay sesión activa para registrar captura")
            return
        
        # Extraer solo el nombre del archivo
        basename = os.path.basename(filename)
        self.current_session["files_generated"]["captures"].append(basename)
        self.current_session["session_stats"]["captures_count"] += 1
        
        logger.info(f"📷 Captura registrada en sesión: {basename}")
    
    def add_report(self, filename: str):
        """Registrar nuevo reporte en la sesión actual"""
        if not self.current_session:
            logger.warning("No hay sesión activa para registrar reporte")
            return
        
        # Extraer solo el nombre del archivo
        basename = os.path.basename(filename)
        self.current_session["files_generated"]["reports"].append(basename)
        
        logger.info(f"📋 Reporte registrado en sesión: {basename}")
    
    def update_inspection_data(self, data: Dict):
        """Actualizar datos del formulario de inspección"""
        if not self.current_session:
            logger.warning("No hay sesión activa para actualizar datos")
            return
        
        self.current_session["inspection_data"].update(data)
        logger.info("📝 Datos de inspección actualizados en sesión")
    
    def get_current_session_info(self) -> Optional[Dict]:
        """Obtener información de la sesión actual"""
        return self.current_session.copy() if self.current_session else None
    
    def _save_session_metadata(self) -> bool:
        """Guardar metadatos de sesión en archivo JSON"""
        if not self.current_session:
            return False
        
        try:
            filename = self.path_manager.generate_session_filename()
            
            # Crear directorio si no existe
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            # Guardar JSON con formato legible
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.current_session, f, indent=2, ensure_ascii=False)
            
            logger.info(f"💾 Metadatos guardados: {filename}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error guardando metadatos de sesión: {e}")
            return False
    
    def _get_mode_name(self, mode: InspectionMode) -> str:
        """Obtener nombre legible del modo"""
        names = {
            InspectionMode.PRO: "Profesional",
            InspectionMode.RAPIDO: "Rápido", 
            InspectionMode.BASICO: "Básico"
        }
        return names.get(mode, "Desconocido")
    
    def _get_overlays_for_mode(self, mode: InspectionMode) -> List[str]:
        """Obtener lista de overlays disponibles para el modo"""
        overlays_config = {
            InspectionMode.PRO: ["fecha", "distancia", "grilla", "pozos", "tramo", "anotaciones"],
            InspectionMode.RAPIDO: ["fecha", "distancia", "grilla"],
            InspectionMode.BASICO: ["fecha", "distancia", "grilla", "pozos"]
        }
        return overlays_config.get(mode, [])

# Instancia global
_session_manager = None

def get_session_manager() -> SessionManager:
    """Obtener instancia global del SessionManager"""
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
    return _session_manager