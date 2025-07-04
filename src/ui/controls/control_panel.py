# -*- coding: utf-8 -*-
"""
Panel de controles laterales para la aplicación
Extraído de main_window.py para mejor modularización
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from ...utils.logger import setup_logger

logger = setup_logger("ControlPanel")

class ControlPanel(QWidget):
    """Panel lateral derecho con controles de la aplicación"""
    
    # Señales para comunicación con el controlador principal
    plus_button_clicked = pyqtSignal()
    record_button_clicked = pyqtSignal()
    stop_button_clicked = pyqtSignal()
    capture_button_clicked = pyqtSignal()
    annotate_button_clicked = pyqtSignal()
    reset_distance_clicked = pyqtSignal()
    clear_screen_clicked = pyqtSignal()
    settings_button_clicked = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.is_recording = False
        self.current_mode = None  # NUEVO: Modo actual
        self.setup_ui()
        logger.info("ControlPanel inicializado")
    
    def setup_ui(self):
        """Configurar interfaz del panel de controles"""
        self.setObjectName("rightPanel")
        self.setMinimumWidth(200)
        self.setMaximumWidth(300)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # === TÍTULO DEL PANEL ===
        title_label = QLabel("CONTROLES")
        title_label.setObjectName("rightPanelTitle")
        title_label.setStyleSheet("""
        QLabel#rightPanelTitle {
            color: rgba(255, 167, 38, 255);
            font-size: 14px;
            font-weight: bold;
            font-family: Arial, sans-serif;
            padding: 5px;
            text-align: center;
        }
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # === BOTÓN '+' PRINCIPAL ===
        self.plus_button = self._create_plus_button()
        
        # === BOTONES DE CONTROL ===
        self.record_button = self._create_control_button("▶️", "Iniciar Grabación", self.record_button_clicked)
        self.stop_button = self._create_control_button("⏹️", "Detener", self.stop_button_clicked)
        self.capture_button = self._create_control_button("📸", "Capturar foto", self.capture_button_clicked)
        self.annotate_button = self._create_control_button("📝", "Anotar", self.annotate_button_clicked)
        self.reset_distance_button = self._create_control_button("📏", "Resetear Distancia", self.reset_distance_clicked)
        self.clear_screen_button = self._create_control_button("🧹", "Limpiar Pantalla", self.clear_screen_clicked)
        
        # === BOTÓN DE CONFIGURACIONES ===
        self.settings_button = self._create_settings_button()
        
        # === AGREGAR ELEMENTOS AL LAYOUT ===
        layout.addWidget(title_label)
        layout.addWidget(self.plus_button, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(15)  # Espacio entre el botón + y los controles
        
        # Agregar botones de control verticalmente
        control_buttons = [
            self.record_button, self.stop_button, self.capture_button,
            self.annotate_button, self.reset_distance_button, self.clear_screen_button
        ]
        
        for button in control_buttons:
            layout.addWidget(button, alignment=Qt.AlignmentFlag.AlignCenter)
            layout.addSpacing(8)
        
        layout.addStretch()  # Empujar configuraciones hacia abajo
        layout.addWidget(self.settings_button, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(20)  # Espacio final
        
        # Aplicar estilo al panel
        self._apply_panel_style()
    
    def _create_plus_button(self):
        """Crear botón '+' principal"""
        button = QPushButton("+")
        button.setObjectName("plusButton")
        button.setMinimumSize(70, 70)
        button.setMaximumSize(70, 70)
        button.clicked.connect(self.plus_button_clicked.emit)
        
        button.setStyleSheet("""
        QPushButton#plusButton {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(255, 183, 77, 220), 
                stop:1 rgba(255, 167, 38, 220));
            color: white;
            border: 3px solid rgba(255, 255, 255, 120);
            border-radius: 35px;
            font-size: 32px;
            font-weight: bold;
            font-family: Arial, sans-serif;
        }
        QPushButton#plusButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(255, 167, 38, 250), 
                stop:1 rgba(255, 152, 0, 250));
            border: 3px solid rgba(255, 255, 255, 180);
        }
        QPushButton#plusButton:pressed {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(255, 152, 0, 200), 
                stop:1 rgba(245, 124, 0, 200));
            border: 3px solid rgba(255, 255, 255, 220);
        }
        """)
        
        return button
    
    def _create_control_button(self, icon, tooltip, signal):
        """Crear botón de control estándar"""
        button = QPushButton(icon)
        button.setMinimumSize(55, 55)
        button.setMaximumSize(55, 55)
        button.setToolTip(tooltip)
        button.clicked.connect(signal.emit)
        
        button.setStyleSheet(self._get_control_button_style())
        return button
    
    def _create_settings_button(self):
        """Crear botón de configuraciones"""
        button = QPushButton("⚙️")
        button.setObjectName("settingsButton")
        button.setMinimumSize(50, 50)
        button.setMaximumSize(50, 50)
        button.clicked.connect(self.settings_button_clicked.emit)
        
        button.setStyleSheet("""
        QPushButton#settingsButton {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(80, 80, 80, 200), 
                stop:1 rgba(60, 60, 60, 200));
            color: white;
            border: 2px solid rgba(255, 167, 38, 100);
            border-radius: 25px;
            font-size: 20px;
            font-weight: bold;
        }
        QPushButton#settingsButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(255, 167, 38, 220), 
                stop:1 rgba(255, 152, 0, 220));
            border: 2px solid rgba(255, 255, 255, 150);
        }
        QPushButton#settingsButton:pressed {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(255, 152, 0, 180), 
                stop:1 rgba(245, 124, 0, 180));
            border: 2px solid rgba(255, 255, 255, 200);
        }
        """)
        
        return button
    
    def _get_control_button_style(self):
        """Obtener estilo para botones de control"""
        return """
        QPushButton {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(70, 70, 70, 220), 
                stop:1 rgba(50, 50, 50, 220));
            color: white;
            border: 2px solid rgba(255, 255, 255, 80);
            border-radius: 27px;
            font-size: 18px;
            font-weight: bold;
        }
        QPushButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(90, 90, 90, 250), 
                stop:1 rgba(70, 70, 70, 250));
            border: 2px solid rgba(255, 255, 255, 120);
        }
        QPushButton:pressed {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(40, 40, 40, 200), 
                stop:1 rgba(20, 20, 20, 200));
            border: 2px solid rgba(255, 255, 255, 160);
        }
        """
    
    def _apply_panel_style(self):
        """Aplicar estilo al panel"""
        self.setStyleSheet("""
        QWidget#rightPanel {
            background: rgba(45, 45, 45, 150);
            border-radius: 10px;
            border: 1px solid rgba(255, 167, 38, 80);
        }
        """)
    
    def set_recording_state(self, is_recording):
        """Actualizar estado de grabación"""
        self.is_recording = is_recording
        # Aquí se puede cambiar el icono del botón según el estado
        # Por ejemplo: self.record_button.setText("⏸️" if is_recording else "▶️")
    
    def set_inspection_mode(self, mode):
        """Configurar panel según el modo de inspección"""
        self.current_mode = mode
        self._update_buttons_visibility()
        logger.info(f"ControlPanel configurado para modo: {mode}")
    
    def _update_buttons_visibility(self):
        """Actualizar visibilidad de botones según el modo"""
        if self.current_mode == "pro":
            # PRO: Todos los botones disponibles (sin botón +)
            self.plus_button.setVisible(False)            # OCULTAR
            self.record_button.setVisible(True)
            self.stop_button.setVisible(True)
            self.capture_button.setVisible(True)
            self.annotate_button.setVisible(True)
            self.reset_distance_button.setVisible(True)
            self.clear_screen_button.setVisible(True)
            self.settings_button.setVisible(True)
            
        elif self.current_mode == "rapido":
            # RÁPIDO: Todos los botones disponibles (sin botón +)
            self.plus_button.setVisible(False)            # OCULTAR
            self.record_button.setVisible(True)
            self.stop_button.setVisible(True)
            self.capture_button.setVisible(True)
            self.annotate_button.setVisible(True)         # MOSTRAR
            self.reset_distance_button.setVisible(True)   # MOSTRAR
            self.clear_screen_button.setVisible(True)     # MOSTRAR
            self.settings_button.setVisible(True)         # MOSTRAR
            
        elif self.current_mode == "basico":
            # BÁSICO: Opciones intermedias (sin botón +)
            self.plus_button.setVisible(False)            # OCULTAR
            self.record_button.setVisible(True)
            self.stop_button.setVisible(True)
            self.capture_button.setVisible(True)
            self.annotate_button.setVisible(False)        # OCULTAR
            self.reset_distance_button.setVisible(True)
            self.clear_screen_button.setVisible(True)
            self.settings_button.setVisible(True)
        
        # Forzar actualización del layout
        self.adjustSize()
        self.update()
        logger.debug(f"Botones actualizados para modo: {self.current_mode}")
    
    def get_current_mode(self):
        """Obtener modo actual"""
        return self.current_mode 