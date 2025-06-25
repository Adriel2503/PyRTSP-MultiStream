# -*- coding: utf-8 -*-
"""
Panel de configuración de elementos específicos de overlays
Maneja toggles para diferentes elementos como grid, fecha, pozos, etc.
"""

from PyQt6.QtWidgets import (
    QGroupBox, QGridLayout, QLabel, QWidget, QHBoxLayout
)
from PyQt6.QtCore import Qt

from .custom_widgets import ToggleSwitch
from .style_manager import StyleManager
from ...utils.logger import setup_logger

logger = setup_logger("ElementsConfigPanel")

class ElementsConfigPanel(QGroupBox):
    """Panel de configuración de elementos específicos de overlays"""
    
    def __init__(self, parent=None):
        super().__init__("🎛️ Elementos en Pantalla", parent)
        
        # Diccionario de toggles para elementos
        self.element_toggles = {}
        
        self.setup_ui()
        logger.info("ElementsConfigPanel inicializado")
    
    def setup_ui(self):
        """Configurar interfaz del panel"""
        self.setStyleSheet(StyleManager.get_group_box_style("#FF9800"))
        
        layout = QGridLayout(self)
        layout.setContentsMargins(15, 20, 15, 15)
        layout.setSpacing(15)
        
        # Definir elementos disponibles
        elements = [
            ("Fecha y Hora", "fecha_enabled"),
            ("Referencia Tramo", "tramo_enabled"),
            ("Pozo Desde", "pozo_inicial_enabled"),
            ("Pozo Hasta", "pozo_final_enabled"),
            ("Cuadrículas", "grid_enabled"),
            ("Distancia", "distancia_enabled")
        ]
        
        # Crear widgets para cada elemento
        for i, (name, key) in enumerate(elements):
            row = i // 2
            col = i % 2
            
            element_widget = self.create_element_widget(name, key)
            layout.addWidget(element_widget, row, col)
    
    def create_element_widget(self, name, key):
        """Crear widget para un elemento individual"""
        # Container principal
        element_widget = QWidget()
        element_layout = QHBoxLayout(element_widget)
        element_layout.setContentsMargins(10, 8, 10, 8)
        element_layout.setSpacing(10)
        
        # Icono indicador de estado
        status_icon = QLabel("●")
        status_icon.setFixedSize(20, 20)
        status_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_icon.setStyleSheet(StyleManager.get_status_icon_style(True))
        
        # Etiqueta del elemento
        label = QLabel(name)
        label.setStyleSheet(StyleManager.get_label_style())
        
        # Toggle switch
        toggle = ToggleSwitch()
        toggle.setChecked(True)  # Por defecto habilitado
        
        # Conectar toggle con icono de estado
        def update_status(checked, icon=status_icon):
            icon.setStyleSheet(StyleManager.get_status_icon_style(checked))
        
        toggle.toggled.connect(update_status)
        
        # Agregar al layout
        element_layout.addWidget(status_icon)
        element_layout.addWidget(label)
        element_layout.addStretch()
        element_layout.addWidget(toggle)
        
        # Aplicar estilo al container
        element_widget.setStyleSheet(StyleManager.get_element_widget_style())
        
        # Guardar referencia al toggle
        self.element_toggles[key] = toggle
        
        logger.debug(f"Elemento creado: {name} ({key})")
        return element_widget
    
    def get_config(self):
        """Obtener configuración actual de elementos"""
        config = {}
        for key, toggle in self.element_toggles.items():
            config[key] = toggle.isChecked()
        
        logger.debug(f"Configuración de elementos obtenida: {config}")
        return config
    
    def load_config(self, config):
        """Cargar configuración en los elementos"""
        if not config:
            logger.debug("No hay configuración para cargar")
            return
        
        for key, toggle in self.element_toggles.items():
            if key in config:
                toggle.setChecked(config[key])
                logger.debug(f"Elemento {key} configurado: {config[key]}")
    
    def get_element_state(self, key):
        """Obtener estado de un elemento específico"""
        if key in self.element_toggles:
            return self.element_toggles[key].isChecked()
        return False
    
    def set_element_state(self, key, enabled):
        """Establecer estado de un elemento específico"""
        if key in self.element_toggles:
            self.element_toggles[key].setChecked(enabled)
            logger.debug(f"Estado de {key} establecido: {enabled}")
    
    def get_available_elements(self):
        """Obtener lista de elementos disponibles"""
        return list(self.element_toggles.keys())
    
    def enable_all_elements(self):
        """Habilitar todos los elementos"""
        for toggle in self.element_toggles.values():
            toggle.setChecked(True)
        logger.info("Todos los elementos habilitados")
    
    def disable_all_elements(self):
        """Deshabilitar todos los elementos"""
        for toggle in self.element_toggles.values():
            toggle.setChecked(False)
        logger.info("Todos los elementos deshabilitados")
    
    def get_enabled_elements_count(self):
        """Obtener número de elementos habilitados"""
        count = sum(1 for toggle in self.element_toggles.values() if toggle.isChecked())
        return count 