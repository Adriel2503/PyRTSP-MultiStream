# -*- coding: utf-8 -*-
"""
Panel de configuración de elementos específicos de overlays
Maneja toggles para diferentes elementos como grid, fecha, pozos, etc.
"""

from PyQt6.QtWidgets import (
    QGridLayout, QLabel, QWidget, QHBoxLayout, QVBoxLayout
)
from PyQt6.QtCore import Qt

from .custom_widgets import EyeToggleButton
from .style_manager import StyleManager
from ...utils.logger import setup_logger
from ...utils.constants import DEFAULT_OVERLAY_ELEMENTS, OVERLAY_ELEMENTS_UI_CONFIG, FORM_DEPENDENT_ELEMENTS

logger = setup_logger("ElementsConfigPanel")

class ElementsConfigPanel(QWidget):
    """Panel de configuración de elementos específicos de overlays"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Diccionario de toggles para elementos
        self.element_toggles = {}
        
        # Estado del formulario (se actualiza externamente)
        self.form_filled = False
        
        self.setup_ui()
        self.update_form_dependent_elements()
        logger.info("ElementsConfigPanel inicializado")
    
    def setup_ui(self):
        """Configurar interfaz del panel"""
        self.setStyleSheet("background: transparent; border: none;")
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 5, 0, 0)
        main_layout.setSpacing(10)
        
        # Título eliminado según solicitud del usuario
        
        # Layout de grid para los controles
        layout = QGridLayout()
        layout.setContentsMargins(15, 10, 15, 15)
        layout.setSpacing(5)
        
        # Usar configuración centralizada de constants.py
        elements = [(name, key, DEFAULT_OVERLAY_ELEMENTS[key]) 
                   for name, key in OVERLAY_ELEMENTS_UI_CONFIG]
        
        # Crear widgets para cada elemento
        for i, (name, key, default_state) in enumerate(elements):
            row = i // 2
            col = i % 2
            
            element_widget = self.create_element_widget(name, key, default_state)
            layout.addWidget(element_widget, row, col)
        
        # Agregar el layout de grid al layout principal
        main_layout.addLayout(layout)
    
    def create_element_widget(self, name, key, default_state=True):
        """Crear widget para un elemento individual"""
        # Container principal
        element_widget = QWidget()
        element_layout = QHBoxLayout(element_widget)
        element_layout.setContentsMargins(10, 8, 10, 8)
        element_layout.setSpacing(10)
        
        # Etiqueta del elemento
        label = QLabel(name)
        label.setStyleSheet(StyleManager.get_label_style())
        
        # Eye toggle button
        toggle = EyeToggleButton()
        toggle.setChecked(default_state)  # Usar estado inicial configurado
        
        # Agregar al layout (SIN icono de estado)
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
    
    def set_form_filled(self, filled):
        """Establecer estado del formulario"""
        self.form_filled = filled
        self.update_form_dependent_elements()
        logger.info(f"Estado del formulario actualizado: {filled}")
    
    def update_form_dependent_elements(self):
        """Actualizar disponibilidad de elementos dependientes del formulario"""
        for key, toggle in self.element_toggles.items():
            if key in FORM_DEPENDENT_ELEMENTS:
                # Habilitar/deshabilitar según estado del formulario
                toggle.setEnabled(self.form_filled)
                if not self.form_filled:
                    # Si no hay formulario, forzar a cerrado
                    toggle.setChecked(False)
                    # Cambiar tooltip para indicar que requiere formulario
                    toggle.setToolTip("⚠️ Requiere llenar formulario de inspección")
                else:
                    # Si hay formulario, habilitar y activar por defecto
                    toggle.setChecked(True)
                    toggle.setToolTip("Elemento disponible - Click para mostrar/ocultar")
                
                logger.debug(f"Elemento {key} {'habilitado' if self.form_filled else 'bloqueado'}")
    
    def is_form_filled(self):
        """Verificar si el formulario ha sido llenado"""
        return self.form_filled 