# -*- coding: utf-8 -*-
"""
Controlador principal de la aplicación
Maneja la lógica de negocio y coordinación entre componentes
"""

from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import QObject, pyqtSignal

from ...utils.logger import setup_logger

logger = setup_logger("ApplicationController")

class ApplicationController(QObject):
    """Controlador principal que coordina la lógica de la aplicación"""
    
    # Señales para comunicación con otros componentes
    connection_requested = pyqtSignal(str, str, str, str)  # ip, user, password, rtsp_url
    stream_started = pyqtSignal(str)  # rtsp_url
    stream_stopped = pyqtSignal()
    statistics_updated = pyqtSignal(dict)  # métricas
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.video_widget = None
        self.stats_display = None
        self.window_manager = None
        self.is_connected = False
        self.current_rtsp_url = None
        logger.info("ApplicationController inicializado")
    
    def set_components(self, video_widget, stats_display, window_manager):
        """Establecer referencias a componentes principales"""
        self.video_widget = video_widget
        self.stats_display = stats_display
        self.window_manager = window_manager
        logger.debug("Componentes establecidos en ApplicationController")
    
    def handle_connection_request(self, ip, user, password, rtsp_url):
        """Manejar solicitud de conexión RTSP"""
        logger.info(f"Procesando solicitud de conexión: {rtsp_url}")
        
        if not self.video_widget:
            logger.error("Video widget no disponible para conexión")
            self._show_connection_error("Error interno: Video widget no disponible")
            return
        
        # Intentar conectar
        success = self.video_widget.start_stream(rtsp_url)
        
        if success:
            self._handle_connection_success(ip, rtsp_url)
        else:
            self._handle_connection_failure()
    
    def _handle_connection_success(self, ip, rtsp_url):
        """Manejar conexión exitosa"""
        self.is_connected = True
        self.current_rtsp_url = rtsp_url
        
        # Notificar al window manager
        if self.window_manager:
            self.window_manager.handle_connection_success(ip)
        
        # Iniciar monitoreo de estadísticas
        if self.stats_display:
            self.stats_display.set_video_widget(self.video_widget)
            self.stats_display.start_monitoring()
        
        # Emitir señal
        self.stream_started.emit(rtsp_url)
        logger.info(f"Conexión exitosa establecida - {ip}")
    
    def _handle_connection_failure(self):
        """Manejar fallo de conexión"""
        self.is_connected = False
        self.current_rtsp_url = None
        
        # Notificar al window manager
        if self.window_manager:
            self.window_manager.handle_connection_failure()
        
        # Mostrar error al usuario
        self._show_connection_error()
        logger.error("Fallo al establecer conexión")
    
    def handle_disconnect_request(self):
        """Manejar solicitud de desconexión"""
        logger.info("Procesando solicitud de desconexión")
        
        # Detener stream
        if self.video_widget:
            self.video_widget.stop_stream()
        
        # Detener estadísticas
        if self.stats_display:
            self.stats_display.stop_monitoring()
        
        # Actualizar estado
        self.is_connected = False
        self.current_rtsp_url = None
        
        # Notificar al window manager
        if self.window_manager:
            self.window_manager.handle_disconnect()
        
        # Emitir señal
        self.stream_stopped.emit()
        logger.info("Desconexión procesada exitosamente")
    
    def _show_connection_error(self, custom_message=None):
        """Mostrar mensaje de error de conexión"""
        message = custom_message or (
            "No se pudo conectar a la cámara IP.\n\n"
            "Verifique:\n"
            "• Dirección IP correcta\n"
            "• Credenciales válidas\n"
            "• Conexión de red\n"
            "• Cámara accesible"
        )
        
        QMessageBox.critical(
            self.main_window, 
            "Error de Conexión", 
            message
        )
    
    def get_connection_status(self):
        """Obtener estado de conexión actual"""
        return {
            'connected': self.is_connected,
            'rtsp_url': self.current_rtsp_url,
            'has_video_widget': self.video_widget is not None,
            'stats_monitoring': (self.stats_display.is_monitoring() 
                               if self.stats_display else False)
        }
    
    def force_disconnect(self):
        """Forzar desconexión (para casos de emergencia)"""
        logger.warning("Forzando desconexión de emergencia")
        try:
            if self.video_widget:
                self.video_widget.stop_stream()
            if self.stats_display:
                self.stats_display.stop_monitoring()
        except Exception as e:
            logger.error(f"Error durante desconexión forzada: {e}")
        finally:
            self.is_connected = False
            self.current_rtsp_url = None 