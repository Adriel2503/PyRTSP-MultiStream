# -*- coding: utf-8 -*-
"""
Diálogo modularizado de configuración de overlays
Coordinador principal que usa paneles especializados
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QWidget
)
from PyQt6.QtCore import pyqtSignal

from .global_config_panel import GlobalConfigPanel
from .elements_config_panel import ElementsConfigPanel
from .style_manager import StyleManager
from ...utils.logger import setup_logger

logger = setup_logger("OverlayConfigDialog")

class OverlayConfigDialog(QDialog):
    """Diálogo modularizado para configurar overlays"""
    
    # Señal emitida cuando se cambia la configuración
    overlay_config_changed = pyqtSignal(dict)
    
    def __init__(self, parent=None, current_config=None):
        super().__init__(parent)
        self.current_config = current_config or {}
        
        # Paneles modulares
        self.global_panel = None
        self.elements_panel = None
        
        try:
            self.setup_ui()
            self.load_current_config()
            logger.info("OverlayConfigDialog modularizado inicializado")
        except Exception as e:
            logger.error(f"Error inicializando OverlayConfigDialog: {e}")
            # Asegurar que los paneles existan aunque sea con valores por defecto
            if not self.global_panel:
                logger.warning("Creando GlobalConfigPanel de emergencia")
                self.global_panel = GlobalConfigPanel()
            if not self.elements_panel:
                logger.warning("Creando ElementsConfigPanel de emergencia")
                self.elements_panel = ElementsConfigPanel()
    
    def setup_ui(self):
        """Configurar interfaz del diálogo"""
        self.setWindowTitle("Configuración")
        self.setModal(True)
        self.setFixedSize(450, 650)
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)
        
        # === PANELES DIRECTAMENTE ===
        # Panel de configuración global
        self.global_panel = GlobalConfigPanel()
        main_layout.addWidget(self.global_panel)
        
        # Panel de configuración de elementos
        self.elements_panel = ElementsConfigPanel()
        main_layout.addWidget(self.elements_panel)
        
        # === BOTONES ===
        buttons_layout = self.create_buttons_layout()
        main_layout.addLayout(buttons_layout)
        
        # Aplicar estilo general
        self.setStyleSheet(StyleManager.get_dialog_style())
    
    # Método eliminado: ya no necesitamos scroll area
    
    def create_buttons_layout(self):
        """Crear layout de botones"""
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(15)
        
        # Botón Cancelar
        cancel_button = QPushButton("Cancelar")
        cancel_button.setFixedSize(140, 40)
        cancel_button.clicked.connect(self.reject)
        cancel_button.setStyleSheet(StyleManager.get_button_style())
        
        # Botón Aplicar
        apply_button = QPushButton("Aplicar")
        apply_button.setFixedSize(140, 40)
        apply_button.clicked.connect(self.apply_config)
        apply_button.setStyleSheet(StyleManager.get_apply_button_style())
        
        buttons_layout.addWidget(cancel_button)
        buttons_layout.addStretch()
        buttons_layout.addWidget(apply_button)
        
        return buttons_layout
    
    def load_current_config(self):
        """Cargar configuración actual en los paneles"""
        if not self.current_config:
            logger.debug("No hay configuración actual - usando valores por defecto del panel")
            return
        
        # Cargar configuración en panel global
        if self.global_panel:
            self.global_panel.load_config(self.current_config)
        
        # ✅ IMPORTANTE: Cargar configuración ACTUAL de elementos (no siempre defaults)
        # Esto mantiene los cambios que el usuario ya hizo previamente
        if self.elements_panel:
            self.elements_panel.load_config(self.current_config)
            
            # Sincronizar estado del formulario
            form_filled = self.current_config.get('form_filled', False)
            self.elements_panel.set_form_filled(form_filled)
            
            logger.debug(f"Configuración de elementos cargada: {self.current_config}")
            logger.debug(f"Estado del formulario: {form_filled}")
    
    def apply_config(self):
        """Aplicar configuración de todos los paneles"""
        config = {}
        
        # Recopilar configuración del panel de elementos
        if self.elements_panel:
            elements_config = self.elements_panel.get_config()
            config.update(elements_config)
        
        # Recopilar configuración del panel global
        if self.global_panel:
            global_config = self.global_panel.get_config()
            config.update(global_config)
        
        logger.info(f"Aplicando configuración completa: {config}")
        
        # Emitir señal con configuración
        self.overlay_config_changed.emit(config)
        
        # Cerrar diálogo
        self.accept()
    
    def get_configuration_summary(self):
        """Obtener resumen de configuración actual"""
        if not self.elements_panel:
            return "Panel de elementos no disponible"
        
        enabled_count = self.elements_panel.get_enabled_elements_count()
        total_count = len(self.elements_panel.get_available_elements())
        
        return f"Elementos activos: {enabled_count}/{total_count}"
    
    def reset_to_defaults(self):
        """Resetear configuración a valores por defecto"""
        if self.elements_panel:
            self.elements_panel.enable_all_elements()
        
        # El panel global ya tiene valores por defecto al inicializarse
        logger.info("Configuración reseteada a valores por defecto")
    
    def closeEvent(self, event):
        """Limpiar recursos al cerrar"""
        # Limpiar panel global (especialmente el timer)
        if self.global_panel:
            self.global_panel.cleanup()
        
        logger.debug("OverlayConfigDialog cerrado y limpiado")
        super().closeEvent(event) 