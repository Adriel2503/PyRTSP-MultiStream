# -*- coding: utf-8 -*-
"""
Ventana principal modularizada de la aplicación PyRTSP-FastStream
Refactorizada para usar componentes modulares con separación completa de responsabilidades
"""

import sys
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QMessageBox, QStackedWidget
)
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QKeySequence, QShortcut

from ...utils.logger import setup_logger
from ..video_widget import VideoWidget
from ..login_screen import LoginScreen
from ..controls.control_panel import ControlPanel
from ..controls.stats_display import StatsDisplay
from ..controls.button_handlers import ButtonHandlers
from .window_manager import WindowManager
from .application_controller import ApplicationController

logger = setup_logger("MainWindow")

class MainWindow(QMainWindow):
    """Ventana principal modularizada con arquitectura MVC"""
    
    def __init__(self):
        super().__init__()
        # Componentes de UI
        self.video_widget = None
        self.login_screen = None
        self.stream_widget = None
        self.control_panel = None
        self.stats_display = None
        
        # Componentes de lógica
        self.window_manager = None
        self.app_controller = None
        self.button_handlers = None
        
        self.setup_ui()
        self.setup_components()
        logger.info("MainWindow modularizada inicializada con arquitectura MVC")
        
    def setup_ui(self):
        """Configurar interfaz de usuario básica"""
        self.setWindowTitle("🚀 Welltep RTSP Viewer - Sistema Profesional")
        self.setGeometry(100, 100, 1200, 700)
        self.setMinimumSize(800, 600)
        
        # Usar QStackedWidget para cambiar entre pantallas
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        # === CREAR PANTALLAS ===
        self.login_screen = LoginScreen()
        self.stream_widget = self._create_stream_widget()
        
        # Agregar atajo de teclado para desconectar (Escape)
        self.disconnect_shortcut = QShortcut(QKeySequence("Escape"), self)
        self.disconnect_shortcut.activated.connect(self._handle_disconnect_shortcut)
        
        logger.debug("UI básica configurada")
    
    def setup_components(self):
        """Configurar componentes modulares con arquitectura MVC"""
        # === INICIALIZAR GESTORES ===
        self.window_manager = WindowManager(self.stacked_widget)
        self.app_controller = ApplicationController(self)
        self.button_handlers = ButtonHandlers(self)
        
        # === REGISTRAR PANTALLAS EN WINDOW MANAGER ===
        self.window_manager.register_screens(self.login_screen, self.stream_widget)
        
        # === ESTABLECER COMPONENTES EN APPLICATION CONTROLLER ===
        self.app_controller.set_components(
            self.video_widget, 
            self.stats_display, 
            self.window_manager
        )
        
        # === CONECTAR SEÑALES ===
        self._connect_signals()
        
        logger.debug("Componentes modulares configurados con arquitectura MVC")
    
    def _create_stream_widget(self):
        """Crear widget de streaming con video y controles modulares"""
        widget = QWidget()
        widget.setObjectName("streamWidget")
        
        main_layout = QVBoxLayout(widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # === PANEL DE ESTADÍSTICAS (MODULAR) ===
        self.stats_display = StatsDisplay()
        main_layout.addWidget(self.stats_display)
        
        # === ÁREA PRINCIPAL: VIDEO + PANEL DE CONTROL ===
        content_layout = QHBoxLayout()
        content_layout.setSpacing(15)
        
        # === ÁREA DE VIDEO ===
        self.video_widget = VideoWidget()
        content_layout.addWidget(self.video_widget)
        
        # === PANEL LATERAL DERECHO (MODULAR) ===
        self.control_panel = ControlPanel()
        content_layout.addWidget(self.control_panel)
        
        # Agregar el layout de contenido al layout principal
        main_layout.addLayout(content_layout)
        
        # Aplicar estilo al widget de stream
        widget.setStyleSheet("""
        QWidget#streamWidget {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #1a1a1a, stop:1 #2d2d2d);
        }
        """)
        
        return widget
    
    def _connect_signals(self):
        """Conectar todas las señales entre componentes"""
        # === SEÑALES DEL LOGIN SCREEN ===
        self.login_screen.connection_requested.connect(self.app_controller.handle_connection_request)
        
        # === SEÑALES DEL PANEL DE CONTROL ===
        if self.control_panel and self.button_handlers:
            self.control_panel.plus_button_clicked.connect(self.button_handlers.handle_plus_button)
            self.control_panel.record_button_clicked.connect(self.button_handlers.handle_record_button)
            self.control_panel.stop_button_clicked.connect(self.button_handlers.handle_stop_button)
            self.control_panel.capture_button_clicked.connect(self.button_handlers.handle_capture_button)
            self.control_panel.annotate_button_clicked.connect(self.button_handlers.handle_annotate_button)
            self.control_panel.reset_distance_clicked.connect(self.button_handlers.handle_reset_distance_button)
            self.control_panel.clear_screen_clicked.connect(self.button_handlers.handle_clear_screen_button)
            self.control_panel.settings_button_clicked.connect(self.button_handlers.handle_settings_button)
        
        logger.debug("Señales conectadas entre componentes")
    
    def _handle_disconnect_shortcut(self):
        """Manejar atajo de teclado para desconectar"""
        if self.app_controller:
            self.app_controller.handle_disconnect_request()
        else:
            # Fallback si no hay controller
            self.disconnect_stream()
    
    def disconnect_stream(self):
        """Método legacy para desconectar (mantener compatibilidad)"""
        if self.app_controller:
            self.app_controller.handle_disconnect_request()
        else:
            # Fallback manual
            if self.video_widget:
                self.video_widget.stop_stream()
            if self.stats_display:
                self.stats_display.stop_monitoring()
            if self.window_manager:
                self.window_manager.handle_disconnect()
            logger.info("Desconección manual ejecutada")
    
    def closeEvent(self, event):
        """Manejar cierre de aplicación"""
        # Usar controller si está disponible
        if self.app_controller:
            self.app_controller.force_disconnect()
        else:
            # Fallback manual
            if self.video_widget:
                self.video_widget.stop_stream()
            if self.stats_display:
                self.stats_display.stop_monitoring()
        
        logger.info("Aplicación cerrada correctamente")
        event.accept() 