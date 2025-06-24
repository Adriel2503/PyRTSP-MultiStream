# -*- coding: utf-8 -*-
"""
Diálogo de configuración de overlays
Permite habilitar/deshabilitar elementos visuales del video
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QCheckBox, QPushButton, QGroupBox, QGridLayout,
    QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from ..utils.logger import setup_logger

logger = setup_logger("OverlayConfigDialog")

class OverlayConfigDialog(QDialog):
    """Diálogo para configurar la visibilidad de overlays"""
    
    # Señal emitida cuando se cambia la configuración
    overlay_config_changed = pyqtSignal(dict)
    
    def __init__(self, parent=None, current_config=None):
        super().__init__(parent)
        self.current_config = current_config or {}
        self.setup_ui()
        logger.info("Diálogo de configuración de overlays inicializado")
    
    def setup_ui(self):
        """Configurar la interfaz del diálogo"""
        self.setWindowTitle("⚙️ Configuración de Overlays")
        self.setModal(True)
        self.setFixedSize(500, 600)
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 15, 20, 20)
        main_layout.setSpacing(10)
        
        # === TÍTULO ===
        title_label = QLabel("Configuración de Elementos Visuales")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont("Arial", 14, QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet("""
        QLabel {
            color: rgba(255, 167, 38, 255);
            padding: 5px;
            margin-bottom: 5px;
        }
        """)
        main_layout.addWidget(title_label)
        
        # === GRUPO CUADRÍCULAS ===
        grid_group = QGroupBox("📐 Cuadrículas")
        grid_group.setStyleSheet("""
        QGroupBox {
            font-weight: bold;
            font-size: 12px;
            color: white;
            border: 2px solid rgba(255, 167, 38, 100);
            border-radius: 8px;
            margin-top: 10px;
            padding-top: 10px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 10px 0 10px;
            color: rgba(255, 167, 38, 255);
        }
        """)
        
        grid_layout = QVBoxLayout(grid_group)
        grid_layout.setContentsMargins(15, 15, 15, 15)
        
        self.grid_checkbox = QCheckBox("Mostrar cuadrículas de referencia")
        self.grid_checkbox.setChecked(True)  # Por defecto activadas
        self.grid_checkbox.setStyleSheet("""
        QCheckBox {
            color: white;
            font-size: 11px;
            spacing: 8px;
        }
        QCheckBox::indicator {
            width: 18px;
            height: 18px;
        }
        QCheckBox::indicator:unchecked {
            border: 2px solid rgba(255, 255, 255, 150);
            background-color: transparent;
            border-radius: 3px;
        }
        QCheckBox::indicator:checked {
            border: 2px solid rgba(255, 167, 38, 255);
            background-color: rgba(255, 167, 38, 255);
            border-radius: 3px;
        }
        QCheckBox::indicator:checked::after {
            content: "✓";
            color: white;
            font-weight: bold;
        }
        """)
        grid_layout.addWidget(self.grid_checkbox)
        main_layout.addWidget(grid_group)
        
        # === GRUPO INFORMACIÓN ===
        info_group = QGroupBox("📊 Información en Pantalla")
        info_group.setStyleSheet("""
        QGroupBox {
            font-weight: bold;
            font-size: 12px;
            color: white;
            border: 2px solid rgba(255, 167, 38, 100);
            border-radius: 8px;
            margin-top: 10px;
            padding-top: 10px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 10px 0 10px;
            color: rgba(255, 167, 38, 255);
        }
        """)
        
        info_layout = QGridLayout(info_group)
        info_layout.setContentsMargins(15, 15, 15, 15)
        info_layout.setSpacing(10)
        
        # Checkbox para cada elemento
        self.fecha_checkbox = QCheckBox("📅 Fecha y hora")
        self.fecha_checkbox.setChecked(True)  # Por defecto activada
        
        self.tramo_checkbox = QCheckBox("🔗 Referencia de tramo")
        self.tramo_checkbox.setChecked(True)  # Por defecto activada
        
        self.pozo_inicial_checkbox = QCheckBox("⬇️ Pozo inicial")
        self.pozo_inicial_checkbox.setChecked(True)  # Por defecto activada
        
        self.pozo_final_checkbox = QCheckBox("⬆️ Pozo final")
        self.pozo_final_checkbox.setChecked(True)  # Por defecto activada
        
        # Estilo para todos los checkboxes de información
        checkbox_style = """
        QCheckBox {
            color: white;
            font-size: 11px;
            spacing: 8px;
        }
        QCheckBox::indicator {
            width: 18px;
            height: 18px;
        }
        QCheckBox::indicator:unchecked {
            border: 2px solid rgba(255, 255, 255, 150);
            background-color: transparent;
            border-radius: 3px;
        }
        QCheckBox::indicator:checked {
            border: 2px solid rgba(255, 167, 38, 255);
            background-color: rgba(255, 167, 38, 255);
            border-radius: 3px;
        }
        QCheckBox::indicator:checked::after {
            content: "✓";
            color: white;
            font-weight: bold;
        }
        """
        
        for checkbox in [self.fecha_checkbox, self.tramo_checkbox, 
                        self.pozo_inicial_checkbox, self.pozo_final_checkbox]:
            checkbox.setStyleSheet(checkbox_style)
        
        # Agregar checkboxes al grid layout (2 columnas)
        info_layout.addWidget(self.fecha_checkbox, 0, 0)
        info_layout.addWidget(self.tramo_checkbox, 0, 1)
        info_layout.addWidget(self.pozo_inicial_checkbox, 1, 0)
        info_layout.addWidget(self.pozo_final_checkbox, 1, 1)
        
        main_layout.addWidget(info_group)
        
        # === LÍNEA SEPARADORA ===
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        line.setStyleSheet("QFrame { color: rgba(255, 167, 38, 100); }")
        main_layout.addWidget(line)
        
        # === BOTONES ===
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        
        # Botón Cancelar
        cancel_button = QPushButton("❌ Cancelar")
        cancel_button.setFixedSize(120, 35)
        cancel_button.clicked.connect(self.reject)
        cancel_button.setStyleSheet("""
        QPushButton {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(100, 100, 100, 200), 
                stop:1 rgba(80, 80, 80, 200));
            color: white;
            border: none;
            border-radius: 6px;
            font-weight: bold;
            font-size: 11px;
        }
        QPushButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(120, 120, 120, 250), 
                stop:1 rgba(100, 100, 100, 250));
        }
        QPushButton:pressed {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(80, 80, 80, 200), 
                stop:1 rgba(60, 60, 60, 200));
        }
        """)
        
        # Botón Aplicar
        apply_button = QPushButton("✅ Aplicar")
        apply_button.setFixedSize(120, 35)
        apply_button.clicked.connect(self.apply_config)
        apply_button.setStyleSheet("""
        QPushButton {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(255, 167, 38, 220), 
                stop:1 rgba(255, 152, 0, 220));
            color: white;
            border: none;
            border-radius: 6px;
            font-weight: bold;
            font-size: 11px;
        }
        QPushButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(255, 152, 0, 250), 
                stop:1 rgba(245, 124, 0, 250));
        }
        QPushButton:pressed {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(255, 152, 0, 200), 
                stop:1 rgba(245, 124, 0, 200));
        }
        """)
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(cancel_button)
        buttons_layout.addWidget(apply_button)
        
        main_layout.addLayout(buttons_layout)
        
        # Agregar spacer para empujar todo hacia arriba
        main_layout.addStretch()
        
        # Estilo general del diálogo
        self.setStyleSheet("""
        QDialog {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #2d2d2d, stop:1 #1a1a1a);
            border: 2px solid rgba(255, 167, 38, 150);
            border-radius: 10px;
        }
        """)
        
        # Cargar configuración actual después de crear los checkboxes
        self.load_current_config()
    
    def load_current_config(self):
        """Cargar configuración actual desde el video widget"""
        # Actualizar checkboxes según la configuración actual
        self.grid_checkbox.setChecked(self.current_config.get('grid_enabled', True))
        self.fecha_checkbox.setChecked(self.current_config.get('fecha_enabled', True))
        self.tramo_checkbox.setChecked(self.current_config.get('tramo_enabled', True))
        self.pozo_inicial_checkbox.setChecked(self.current_config.get('pozo_inicial_enabled', True))
        self.pozo_final_checkbox.setChecked(self.current_config.get('pozo_final_enabled', True))
        
        logger.info(f"Configuración cargada: {self.current_config}")
    
    def apply_config(self):
        """Aplicar la configuración seleccionada"""
        config = {
            'grid_enabled': self.grid_checkbox.isChecked(),
            'fecha_enabled': self.fecha_checkbox.isChecked(),
            'tramo_enabled': self.tramo_checkbox.isChecked(),
            'pozo_inicial_enabled': self.pozo_inicial_checkbox.isChecked(),
            'pozo_final_enabled': self.pozo_final_checkbox.isChecked()
        }
        
        logger.info(f"Aplicando configuración de overlays: {config}")
        
        # Emitir señal con la nueva configuración
        self.overlay_config_changed.emit(config)
        
        # Cerrar diálogo
        self.accept()
    
    def get_current_config(self):
        """Obtener configuración actual de los checkboxes"""
        return {
            'grid_enabled': self.grid_checkbox.isChecked(),
            'fecha_enabled': self.fecha_checkbox.isChecked(),
            'tramo_enabled': self.tramo_checkbox.isChecked(),
            'pozo_inicial_enabled': self.pozo_inicial_checkbox.isChecked(),
            'pozo_final_enabled': self.pozo_final_checkbox.isChecked()
        } 