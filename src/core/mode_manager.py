# -*- coding: utf-8 -*-
"""
Gestor de modos de inspección para Welltep
Gestiona los diferentes modos: PRO, RÁPIDO, BÁSICO
"""

from enum import Enum
from ..utils.logger import setup_logger

logger = setup_logger("ModeManager")

class InspectionMode(Enum):
    PRO = "pro"
    RAPIDO = "rapido"
    BASICO = "basico"

class ModeManager:
    """Gestor de modos de inspección"""
    
    def __init__(self):
        self.current_mode = None
        self.mode_config = {
            InspectionMode.PRO: {
                "name": "Profesional",
                "description": "Funcionalidad completa\nTodas las opciones disponibles",
                "icon": "🏆",
                "control_buttons": ["plus", "record", "stop", "capture", "annotate", "reset", "clear", "settings", "report"],
                "configurable_overlays": ["fecha", "distancia", "grilla", "pozos", "tramo", "anotaciones"],
                "pdf_template": "pro_report.html"
            },
            InspectionMode.RAPIDO: {
                "name": "Rápido",
                "description": "Inspección rápida\nSolo lo esencial",
                "icon": "⚡",
                "control_buttons": ["record", "stop", "capture", "annotate", "reset", "clear", "settings", "report"],  # SIN BOTÓN +
                "configurable_overlays": ["fecha", "distancia", "grilla"],
                "pdf_template": "rapido_report.html"
            },
            InspectionMode.BASICO: {
                "name": "Básico", 
                "description": "Inspección intermedia\nOpciones básicas",
                "icon": "📝",
                "control_buttons": ["plus", "record", "stop", "capture", "reset", "clear", "settings", "report"],
                "configurable_overlays": ["fecha", "distancia", "grilla", "pozos"],
                "pdf_template": "basico_report.html"
            }
        }
        logger.info("ModeManager inicializado")
    
    def set_mode(self, mode: InspectionMode):
        """Configurar el modo actual"""
        self.current_mode = mode
        logger.info(f"Modo configurado: {mode.value} - {self.get_mode_name()}")
    
    def get_mode_config(self):
        """Obtener configuración del modo actual"""
        if self.current_mode is None:
            return None
        return self.mode_config[self.current_mode]
    
    def get_control_buttons(self):
        """Obtener botones de control permitidos"""
        config = self.get_mode_config()
        return config["control_buttons"] if config else []
    
    def get_configurable_overlays(self):
        """Obtener overlays configurables"""
        config = self.get_mode_config()
        return config["configurable_overlays"] if config else []
    
    def get_mode_name(self):
        """Obtener nombre del modo actual"""
        config = self.get_mode_config()
        return config["name"] if config else "No seleccionado"
    
    def get_mode_description(self):
        """Obtener descripción del modo actual"""
        config = self.get_mode_config()
        return config["description"] if config else ""
    
    def get_pdf_template(self):
        """Obtener template PDF del modo actual"""
        config = self.get_mode_config()
        return config["pdf_template"] if config else "default_report.html"
    
    def is_button_allowed(self, button_name):
        """Verificar si un botón está permitido en el modo actual"""
        allowed_buttons = self.get_control_buttons()
        return button_name in allowed_buttons
    
    def is_overlay_configurable(self, overlay_name):
        """Verificar si un overlay es configurable en el modo actual"""
        configurable_overlays = self.get_configurable_overlays()
        return overlay_name in configurable_overlays
    
    @staticmethod
    def get_all_modes():
        """Obtener todos los modos disponibles"""
        return [InspectionMode.PRO, InspectionMode.RAPIDO, InspectionMode.BASICO] 