# -*- coding: utf-8 -*-
"""
Gestor de ventanas y navegación entre pantallas
Maneja el estado de la aplicación y transiciones
"""

from PyQt6.QtWidgets import QStackedWidget
from PyQt6.QtCore import QObject, pyqtSignal

from ...utils.logger import setup_logger

logger = setup_logger("WindowManager")

class WindowManager(QObject):
    """Gestor centralizado de ventanas y navegación"""
    
    # Señales para notificar cambios de estado
    screen_changed = pyqtSignal(str)  # 'login' o 'stream'
    connection_established = pyqtSignal(str)  # IP conectada
    connection_lost = pyqtSignal()
    
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.login_screen = None
        self.stream_widget = None
        self.current_screen = "login"
        self.connected_ip = None
        logger.info("WindowManager inicializado")
    
    def register_screens(self, login_screen, stream_widget):
        """Registrar las pantallas disponibles"""
        self.login_screen = login_screen
        self.stream_widget = stream_widget
        
        # Agregar al stacked widget
        self.stacked_widget.addWidget(login_screen)
        self.stacked_widget.addWidget(stream_widget)
        
        # Mostrar login por defecto
        self.show_login_screen()
        logger.debug("Pantallas registradas en WindowManager")
    
    def show_login_screen(self):
        """Mostrar pantalla de login"""
        if self.login_screen:
            self.stacked_widget.setCurrentWidget(self.login_screen)
            self.current_screen = "login"
            self.connected_ip = None
            self.screen_changed.emit("login")
            logger.info("Navegación a pantalla de login")
    
    def show_stream_screen(self, ip=None):
        """Mostrar pantalla de streaming"""
        if self.stream_widget:
            self.stacked_widget.setCurrentWidget(self.stream_widget)
            self.current_screen = "stream"
            
            if ip:
                self.connected_ip = ip
                self.connection_established.emit(ip)
            
            self.screen_changed.emit("stream")
            logger.info(f"Navegación a pantalla de stream{f' - IP: {ip}' if ip else ''}")
    
    def handle_connection_success(self, ip):
        """Manejar conexión exitosa"""
        self.show_stream_screen(ip)
        logger.info(f"Conexión exitosa establecida a {ip}")
    
    def handle_connection_failure(self):
        """Manejar fallo de conexión"""
        self.show_login_screen()
        self.connection_lost.emit()
        logger.warning("Fallo de conexión - volviendo a login")
    
    def handle_disconnect(self):
        """Manejar desconexión"""
        self.show_login_screen()
        self.connection_lost.emit()
        logger.info("Desconexión manejada - volviendo a login")
    
    def get_current_screen(self):
        """Obtener pantalla actual"""
        return self.current_screen
    
    def is_connected(self):
        """Verificar si hay conexión activa"""
        return self.current_screen == "stream" and self.connected_ip is not None
    
    def get_connected_ip(self):
        """Obtener IP conectada actual"""
        return self.connected_ip 