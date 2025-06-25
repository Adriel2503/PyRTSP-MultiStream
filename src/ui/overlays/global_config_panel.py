# -*- coding: utf-8 -*-
"""
Panel de configuración global de overlays
Maneja configuraciones que afectan a todos los elementos
"""

from PyQt6.QtWidgets import (
    QGroupBox, QGridLayout, QLabel, QSlider, QSpinBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor

from .custom_widgets import ColorButton
from .style_manager import StyleManager
from ...utils.constants import CAIRO_GRID_CONFIG, CAIRO_OVERLAY_CONFIG
from ...utils.logger import setup_logger
import datetime

logger = setup_logger("GlobalConfigPanel")

class GlobalConfigPanel(QGroupBox):
    """Panel de configuración global"""
    
    def __init__(self):
        super().__init__("🌐 Configuración Global")
        
        # Timer para actualización de fecha/hora
        self.datetime_timer = QTimer()
        self.datetime_timer.timeout.connect(self.update_datetime_display)
        
        self.setup_ui()
        self.setup_styles()
        
        # Iniciar timer de fecha/hora
        self.datetime_timer.start(1000)  # Actualizar cada segundo
        
        logger.debug("GlobalConfigPanel inicializado")
    
    def setup_ui(self):
        """Configurar interfaz del panel"""
        layout = QGridLayout(self)
        layout.setContentsMargins(15, 20, 15, 15)
        layout.setSpacing(15)
        
        # === FECHA Y HORA (DISPLAY DINÁMICO) ===
        layout.addWidget(QLabel("Fecha y Hora"), 0, 0)
        self.datetime_display = QLabel()
        self.datetime_display.setStyleSheet(StyleManager.get_datetime_display_style())
        self.update_datetime_display()  # Mostrar inmediatamente
        layout.addWidget(self.datetime_display, 0, 1, 1, 2)
        
        # === CONSTANTE ===
        layout.addWidget(QLabel("Constante"), 1, 0)
        self.constant_spinbox = QSpinBox()
        self.constant_spinbox.setRange(1, 100)
        self.constant_spinbox.setValue(42)
        self.constant_spinbox.setStyleSheet(StyleManager.get_spinbox_style())
        layout.addWidget(self.constant_spinbox, 1, 1, 1, 2)
        
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
        
        # === OPACIDAD DE FONDO ===
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
        # Usar opacidad actual de las constantes
        current_grid_opacity = int(CAIRO_GRID_CONFIG['line_color'][3] * 100)
        self.grid_opacity_slider.setValue(current_grid_opacity)
        self.grid_opacity_slider.setStyleSheet(StyleManager.get_slider_style())
        self.grid_opacity_label = QLabel(f"{current_grid_opacity/100:.1f}")
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
        
        # Color de Cuadrícula - ✅ USAR COLOR ACTUAL DE CONSTANTS.PY
        layout.addWidget(QLabel("Color de Cuadrícula"), 7, 0)
        self.grid_color_button = ColorButton()
        # Convertir RGBA de constants.py a QColor
        grid_rgba = CAIRO_GRID_CONFIG['line_color']
        current_grid_color = QColor(
            int(grid_rgba[0] * 255),  # R
            int(grid_rgba[1] * 255),  # G
            int(grid_rgba[2] * 255),  # B
            int(grid_rgba[3] * 255)   # A
        )
        self.grid_color_button.set_color(current_grid_color)
        self.grid_color_hex = QLabel(current_grid_color.name().upper())
        self.grid_color_hex.setStyleSheet(StyleManager.get_color_hex_style("white", current_grid_color.name()))
        self.grid_color_button.color_changed.connect(
            lambda c: self.grid_color_hex.setText(c.name().upper())
        )
        layout.addWidget(self.grid_color_button, 7, 1)
        layout.addWidget(self.grid_color_hex, 7, 2)
    
    def setup_styles(self):
        """Aplicar estilos al panel"""
        self.setStyleSheet(StyleManager.get_group_box_style("🌐 Configuración Global"))
    
    def apply_label_styles(self, layout):
        """Aplicar estilos a las etiquetas"""
        for i in range(layout.rowCount()):
            label_item = layout.itemAtPosition(i, 0)
            if label_item and isinstance(label_item.widget(), QLabel):
                label_item.widget().setStyleSheet(StyleManager.get_label_style())
    
    def update_datetime_display(self):
        """Actualizar display de fecha y hora en tiempo real"""
        current_time = datetime.datetime.now()
        formatted_time = current_time.strftime('%Y/%m/%d %H:%M:%S')
        self.datetime_display.setText(formatted_time)
    
    def get_config(self):
        """Obtener configuración actual del panel"""
        # Obtener color de cuadrícula y convertir a RGBA normalizado
        grid_color = self.grid_color_button.get_color()
        grid_opacity = self.grid_opacity_slider.value() / 100.0
        
        grid_rgba = (
            grid_color.red() / 255.0,      # R normalizado
            grid_color.green() / 255.0,    # G normalizado  
            grid_color.blue() / 255.0,     # B normalizado
            grid_opacity                   # A del slider
        )
        
        config = {
            'font_size': self.font_size_slider.value(),
            'bg_opacity': self.bg_opacity_slider.value() / 100.0,
            'grid_opacity': grid_opacity,
            'bg_color': self.bg_color_button.get_color(),
            'text_color': self.text_color_button.get_color(),
            'grid_color': self.grid_color_button.get_color(),
            'grid_color_rgba': grid_rgba,  # ✅ RGBA para el renderer
            'constant': self.constant_spinbox.value()
        }
        
        logger.debug(f"Configuración global obtenida: {config}")
        logger.debug(f"Color de cuadrícula RGBA: {grid_rgba}")
        
        return config
    
    def load_config(self, config):
        """Cargar configuración en el panel"""
        if not config:
            return
        
        # Cargar valores si están disponibles
        if 'font_size' in config:
            self.font_size_slider.setValue(config['font_size'])
        
        if 'bg_opacity' in config:
            self.bg_opacity_slider.setValue(int(config['bg_opacity'] * 100))
        
        if 'grid_opacity' in config:
            self.grid_opacity_slider.setValue(int(config['grid_opacity'] * 100))
        
        if 'bg_color' in config and isinstance(config['bg_color'], QColor):
            self.bg_color_button.set_color(config['bg_color'])
        
        if 'text_color' in config and isinstance(config['text_color'], QColor):
            self.text_color_button.set_color(config['text_color'])
        
        if 'grid_color' in config and isinstance(config['grid_color'], QColor):
            self.grid_color_button.set_color(config['grid_color'])
        
        if 'constant' in config:
            self.constant_spinbox.setValue(config['constant'])
        
        logger.debug("Configuración cargada en GlobalConfigPanel")
    
    def cleanup(self):
        """Limpiar recursos del panel"""
        if self.datetime_timer.isActive():
            self.datetime_timer.stop()
        logger.debug("GlobalConfigPanel limpiado") 