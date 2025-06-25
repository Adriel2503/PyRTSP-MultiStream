# -*- coding: utf-8 -*-
"""
Diálogo modularizado de configuración de overlays
Coordinador principal que usa paneles especializados
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QScrollArea, QWidget
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
        
        self.setup_ui()
        self.load_current_config()
        logger.info("OverlayConfigDialog modularizado inicializado")
    
    def setup_ui(self):
        """Configurar interfaz del diálogo"""
        self.setWindowTitle("⚙️ Configuración de Overlays")
        self.setModal(True)
        self.setFixedSize(520, 750)
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)
        
        # === ÁREA DE SCROLL CON PANELES ===
        scroll_area = self.create_scroll_area()
        main_layout.addWidget(scroll_area)
        
        # === BOTONES ===
        buttons_layout = self.create_buttons_layout()
        main_layout.addLayout(buttons_layout)
        
        # Aplicar estilo general
        self.setStyleSheet(StyleManager.get_dialog_style())
    
    def create_scroll_area(self):
        """Crear área de scroll con paneles"""
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # === PANEL DE CONFIGURACIÓN GLOBAL ===
        self.global_panel = GlobalConfigPanel()
        scroll_layout.addWidget(self.global_panel)
        
        # === PANEL DE CONFIGURACIÓN DE ELEMENTOS ===
        self.elements_panel = ElementsConfigPanel()
        scroll_layout.addWidget(self.elements_panel)
        
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet(StyleManager.get_scroll_area_style())
        
        return scroll_area
    
    def create_buttons_layout(self):
        """Crear layout de botones"""
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(15)
        
        # Botón Cancelar
        cancel_button = QPushButton("❌ Cancelar")
        cancel_button.setFixedSize(120, 40)
        cancel_button.clicked.connect(self.reject)
        cancel_button.setStyleSheet(StyleManager.get_button_style())
        
        # Botón Aplicar
        apply_button = QPushButton("✅ Aplicar Cambios")
        apply_button.setFixedSize(150, 40)
        apply_button.clicked.connect(self.apply_config)
        apply_button.setStyleSheet(StyleManager.get_apply_button_style())
        
        buttons_layout.addWidget(cancel_button)
        buttons_layout.addStretch()
        buttons_layout.addWidget(apply_button)
        
        return buttons_layout
    
    def load_current_config(self):
        """Cargar configuración actual en los paneles"""
        if not self.current_config:
            logger.debug("No hay configuración actual para cargar")
            return
        
        # Cargar configuración en panel global
        if self.global_panel:
            self.global_panel.load_config(self.current_config)
        
        # Cargar configuración en panel de elementos
        if self.elements_panel:
            self.elements_panel.load_config(self.current_config)
        
        logger.debug(f"Configuración actual cargada: {self.current_config}")
    
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