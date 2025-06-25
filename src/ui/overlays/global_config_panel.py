# -*- coding: utf-8 -*-
"""
Panel de configuración global para overlays
Maneja sliders, colores, opacidad y configuraciones generales
"""

import datetime
from PyQt6.QtWidgets import (
    QGroupBox, QGridLayout, QLabel, QSlider, QSpinBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor

from .custom_widgets import ColorButton
from .style_manager import StyleManager
from ...utils.logger import setup_logger

logger = setup_logger("GlobalConfigPanel")

class GlobalConfigPanel(QGroupBox):
    """Panel de configuración global de overlays"""
    
    def __init__(self, parent=None):
        super().__init__("🛠️ Configuración Global", parent)
        
        # Referencias a controles
        self.datetime_label = None
        self.constant_spinbox = None
        self.font_size_slider = None
        self.font_size_label = None
        self.bg_opacity_slider = None
        self.bg_opacity_label = None
        self.grid_opacity_slider = None
        self.grid_opacity_label = None
        self.bg_color_button = None
        self.bg_color_hex = None
        self.text_color_button = None
        self.text_color_hex = None
        self.grid_color_button = None
        self.grid_color_hex = None
        
        # Timer para fecha/hora
        self.datetime_timer = None
        
        self.setup_ui()
        self.setup_datetime_timer()
        logger.info("GlobalConfigPanel inicializado")
    
    def setup_ui(self):
        """Configurar interfaz del panel"""
        self.setStyleSheet(StyleManager.get_group_box_style("#4CAF50"))
        
        layout = QGridLayout(self)
        layout.setContentsMargins(15, 20, 15, 15)
        layout.setSpacing(12)
        
        # === FECHA Y HORA (DISPLAY) ===
        layout.addWidget(QLabel("Fecha y Hora"), 0, 0)
        self.datetime_label = QLabel("2025/06/24  14:13:19")
        self.datetime_label.setStyleSheet(StyleManager.get_datetime_label_style())
        layout.addWidget(self.datetime_label, 0, 1, 1, 2)
        
        # === CONSTANTE ===
        layout.addWidget(QLabel("Constante"), 1, 0)
        self.constant_spinbox = QSpinBox()
        self.constant_spinbox.setRange(1, 100)
        self.constant_spinbox.setValue(10)
        self.constant_spinbox.setStyleSheet(StyleManager.get_spinbox_style())
        layout.addWidget(self.constant_spinbox, 1, 1)
        
        # === TAMAÑO DE FUENTE ===
        layout.addWidget(QLabel("Tamaño de Fuente"), 2, 0)
        self.font_size_slider = QSlider(Qt.Orientation.Horizontal)
        self.font_size_slider.setRange(16, 48)
        self.font_size_slider.setValue(32)
        self.font_size_slider.setStyleSheet(StyleManager.get_slider_style())
        self.font_size_label = QLabel("32px")
        self.font_size_label.setStyleSheet(StyleManager.get_value_label_style())
        self.font_size_slider.valueChanged.connect(
            lambda v: self.font_size_label.setText(f"{v}px")
        )
        layout.addWidget(self.font_size_slider, 2, 1)
        layout.addWidget(self.font_size_label, 2, 2)
        
        # === OPACIDAD DEL FONDO ===
        layout.addWidget(QLabel("Opacidad del Fondo"), 3, 0)
        self.bg_opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.bg_opacity_slider.setRange(0, 100)
        self.bg_opacity_slider.setValue(60)
        self.bg_opacity_slider.setStyleSheet(StyleManager.get_slider_style())
        self.bg_opacity_label = QLabel("0.6")
        self.bg_opacity_label.setStyleSheet(StyleManager.get_value_label_style())
        self.bg_opacity_slider.valueChanged.connect(
            lambda v: self.bg_opacity_label.setText(f"{v/100:.1f}")
        )
        layout.addWidget(self.bg_opacity_slider, 3, 1)
        layout.addWidget(self.bg_opacity_label, 3, 2)
        
        # === OPACIDAD CUADRÍCULAS ===
        layout.addWidget(QLabel("Opacidad Cuadrículas"), 4, 0)
        self.grid_opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.grid_opacity_slider.setRange(0, 100)
        self.grid_opacity_slider.setValue(80)
        self.grid_opacity_slider.setStyleSheet(StyleManager.get_slider_style())
        self.grid_opacity_label = QLabel("0.8")
        self.grid_opacity_label.setStyleSheet(StyleManager.get_value_label_style())
        self.grid_opacity_slider.valueChanged.connect(
            lambda v: self.grid_opacity_label.setText(f"{v/100:.1f}")
        )
        layout.addWidget(self.grid_opacity_slider, 4, 1)
        layout.addWidget(self.grid_opacity_label, 4, 2)
        
        # === COLORES ===
        self.setup_color_controls(layout)
        
        # === APLICAR ESTILOS A ETIQUETAS ===
        self.apply_label_styles(layout)
    
    def setup_color_controls(self, layout):
        """Configurar controles de color"""
        # Color de Fondo
        layout.addWidget(QLabel("Color de Fondo"), 5, 0)
        self.bg_color_button = ColorButton()
        self.bg_color_button.set_color(QColor(26, 26, 26))  # #1a1a1a
        self.bg_color_hex = QLabel("#1a1a1a")
        self.bg_color_hex.setStyleSheet(StyleManager.get_color_hex_style("white", "#1a1a1a"))
        self.bg_color_button.color_changed.connect(
            lambda c: self.bg_color_hex.setText(c.name().upper())
        )
        layout.addWidget(self.bg_color_button, 5, 1)
        layout.addWidget(self.bg_color_hex, 5, 2)
        
        # Color de Texto
        layout.addWidget(QLabel("Color de Texto"), 6, 0)
        self.text_color_button = ColorButton()
        self.text_color_button.set_color(QColor(255, 255, 255))  # #ffffff
        self.text_color_hex = QLabel("#ffffff")
        self.text_color_hex.setStyleSheet(StyleManager.get_color_hex_style("black", "white"))
        self.text_color_button.color_changed.connect(
            lambda c: self.text_color_hex.setText(c.name().upper())
        )
        layout.addWidget(self.text_color_button, 6, 1)
        layout.addWidget(self.text_color_hex, 6, 2)
        
        # Color de Cuadrícula
        layout.addWidget(QLabel("Color de Cuadrícula"), 7, 0)
        self.grid_color_button = ColorButton()
        self.grid_color_button.set_color(QColor(176, 33, 33))  # #b02121
        self.grid_color_hex = QLabel("#b02121")
        self.grid_color_hex.setStyleSheet(StyleManager.get_color_hex_style("white", "#b02121"))
        self.grid_color_button.color_changed.connect(
            lambda c: self.grid_color_hex.setText(c.name().upper())
        )
        layout.addWidget(self.grid_color_button, 7, 1)
        layout.addWidget(self.grid_color_hex, 7, 2)
    
    def apply_label_styles(self, layout):
        """Aplicar estilos a las etiquetas"""
        for i in range(layout.rowCount()):
            label = layout.itemAtPosition(i, 0)
            if label and isinstance(label.widget(), QLabel):
                label.widget().setStyleSheet(StyleManager.get_label_style())
    
    def setup_datetime_timer(self):
        """Configurar timer para actualización de fecha/hora"""
        self.datetime_timer = QTimer()
        self.datetime_timer.timeout.connect(self.update_datetime)
        self.datetime_timer.start(1000)  # Actualizar cada segundo
        logger.debug("Timer de fecha/hora iniciado")
    
    def update_datetime(self):
        """Actualizar display de fecha y hora"""
        if self.datetime_label:
            now = datetime.datetime.now()
            formatted = now.strftime("%Y / %m / %d    %H : %M : %S")
            self.datetime_label.setText(formatted)
    
    def get_config(self):
        """Obtener configuración actual del panel"""
        return {
            'font_size': self.font_size_slider.value() if self.font_size_slider else 32,
            'bg_opacity': (self.bg_opacity_slider.value() / 100.0) if self.bg_opacity_slider else 0.6,
            'grid_opacity': (self.grid_opacity_slider.value() / 100.0) if self.grid_opacity_slider else 0.8,
            'constant': self.constant_spinbox.value() if self.constant_spinbox else 10,
            'bg_color': self.bg_color_button.get_color().name() if self.bg_color_button else "#1a1a1a",
            'text_color': self.text_color_button.get_color().name() if self.text_color_button else "#ffffff",
            'grid_color': self.grid_color_button.get_color().name() if self.grid_color_button else "#b02121"
        }
    
    def load_config(self, config):
        """Cargar configuración en el panel"""
        if not config:
            return
        
        if self.font_size_slider and 'font_size' in config:
            self.font_size_slider.setValue(config['font_size'])
        
        if self.bg_opacity_slider and 'bg_opacity' in config:
            self.bg_opacity_slider.setValue(int(config['bg_opacity'] * 100))
        
        if self.grid_opacity_slider and 'grid_opacity' in config:
            self.grid_opacity_slider.setValue(int(config['grid_opacity'] * 100))
        
        if self.constant_spinbox and 'constant' in config:
            self.constant_spinbox.setValue(config['constant'])
        
        logger.debug(f"Configuración cargada: {config}")
    
    def cleanup(self):
        """Limpiar recursos al cerrar"""
        if self.datetime_timer:
            self.datetime_timer.stop()
            self.datetime_timer = None
        logger.debug("GlobalConfigPanel limpiado") 