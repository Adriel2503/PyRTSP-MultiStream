# -*- coding: utf-8 -*-
"""
Ventana de selección de modo de inspección
Permite elegir entre PRO, RÁPIDO y BÁSICO
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from ..utils.logger import setup_logger
from ..core.mode_manager import ModeManager, InspectionMode

logger = setup_logger("ModeSelector")

class ModeSelector(QWidget):
    """Ventana de selección de modo de inspección"""
    
    mode_selected = pyqtSignal(str)  # Emite el modo seleccionado
    
    def __init__(self):
        super().__init__()
        self.mode_manager = ModeManager()
        self.setup_ui()
        logger.info("ModeSelector inicializado")
    
    def setup_ui(self):
        """Configurar interfaz de usuario"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(40)
        
        # === TÍTULO PRINCIPAL (SIN RECTÁNGULO) ===
        title = QLabel("Selecciona el Modo de Inspección")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                font-size: 32px;
                font-weight: bold;
                color: rgba(255, 167, 38, 255);
                margin-bottom: 20px;
                font-family: Arial, sans-serif;
                background: transparent;
                border: none;
                padding: 0px;
            }
        """)
        

        
        # === BOTONES DE MODO ===
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(50)
        
        # Crear botones para cada modo
        for mode in ModeManager.get_all_modes():
            config = self.mode_manager.mode_config[mode]
            button = self._create_mode_button(
                config["icon"],
                config["name"],
                config["description"],
                mode.value
            )
            buttons_layout.addWidget(button)
        

        
        # === AGREGAR ELEMENTOS AL LAYOUT ===
        layout.addWidget(title)
        layout.addLayout(buttons_layout)
        layout.addStretch()
        
        # === APLICAR ESTILO DE FONDO ===
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1a1a1a, stop:1 #2d2d2d);
            }
        """)
    
    def _create_mode_button(self, icon, title, description, mode_value):
        """Crear botón para un modo específico"""
        button = QPushButton()
        button.setMinimumSize(280, 220)
        button.setMaximumSize(280, 220)
        
        # Configurar texto del botón
        button_text = f"{icon}\n{title}\n\n{description}"
        button.setText(button_text)
        
        # Conectar señal
        button.clicked.connect(lambda: self._on_mode_selected(mode_value))
        
        # Aplicar estilo específico según el modo
        if mode_value == "rapido":
            # Modo RÁPIDO destacado (funcionalidad actual)
            button.setStyleSheet(self._get_highlighted_button_style())
        else:
            button.setStyleSheet(self._get_standard_button_style())
        
        return button
    
    def _get_standard_button_style(self):
        """Estilo estándar para botones de modo con rectángulos y animaciones"""
        return """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(70, 70, 70, 220), 
                    stop:1 rgba(50, 50, 50, 220));
                color: white;
                border: 2px solid rgba(255, 167, 38, 100);
                border-radius: 15px;
                font-size: 14px;
                font-weight: bold;
                padding: 20px;
                font-family: Arial, sans-serif;
                text-align: center;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 167, 38, 200), 
                    stop:1 rgba(255, 152, 0, 200));
                border: 2px solid rgba(255, 255, 255, 150);
                color: white;
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 152, 0, 180), 
                    stop:1 rgba(245, 124, 0, 180));
                border: 2px solid rgba(255, 255, 255, 200);
            }
        """
    
    def _get_highlighted_button_style(self):
        """Estilo destacado para el modo RÁPIDO con rectángulo y animaciones"""
        return """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 167, 38, 180), 
                    stop:1 rgba(255, 152, 0, 180));
                color: white;
                border: 3px solid rgba(255, 255, 255, 150);
                border-radius: 15px;
                font-size: 14px;
                font-weight: bold;
                padding: 20px;
                font-family: Arial, sans-serif;
                text-align: center;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 183, 77, 220), 
                    stop:1 rgba(255, 167, 38, 220));
                border: 3px solid rgba(255, 255, 255, 200);
                color: white;
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 152, 0, 160), 
                    stop:1 rgba(245, 124, 0, 160));
                border: 3px solid rgba(255, 255, 255, 230);
            }
        """
    
    def _on_mode_selected(self, mode_value):
        """Manejar selección de modo"""
        logger.info(f"Modo seleccionado: {mode_value}")
        self.mode_selected.emit(mode_value)
    
    def get_selected_mode_info(self, mode_value):
        """Obtener información del modo seleccionado"""
        try:
            mode = InspectionMode(mode_value)
            return self.mode_manager.mode_config[mode]
        except ValueError:
            logger.error(f"Modo inválido: {mode_value}")
            return None 