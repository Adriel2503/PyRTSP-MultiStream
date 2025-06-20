# -*- coding: utf-8 -*-
"""
Clase principal de la aplicación PyRTSP-FastStream
Encapsula la inicialización y lógica central de la aplicación
"""

import sys
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst

from PyQt6.QtWidgets import QApplication

from ..utils.constants import APP_NAME, APP_VERSION
from ..utils.logger import setup_logger
from ..ui.main_window import MainWindow

logger = setup_logger("Application")

class Application:
    """Clase principal que gestiona la aplicación completa"""
    
    def __init__(self):
        self.app = None
        self.main_window = None
        self._initialize_gstreamer()
        logger.info(f"Aplicación {APP_NAME} v{APP_VERSION} inicializada")
    
    def _initialize_gstreamer(self):
        """Inicializar GStreamer"""
        try:
            Gst.init(None)
            logger.info("GStreamer inicializado exitosamente")
        except Exception as e:
            logger.error(f"Error inicializando GStreamer: {e}")
            raise RuntimeError("No se pudo inicializar GStreamer")
    
    def create_app(self, argv=None):
        """Crear aplicación PyQt6"""
        if argv is None:
            argv = sys.argv
        
        self.app = QApplication(argv)
        self.app.setApplicationName(APP_NAME)
        self.app.setApplicationVersion(APP_VERSION)
        
        logger.info("Aplicación PyQt6 creada")
        return self.app
    
    def create_main_window(self):
        """Crear ventana principal"""
        self.main_window = MainWindow()
        logger.info("Ventana principal creada")
        return self.main_window
    
    def run(self):
        """Ejecutar la aplicación"""
        if not self.app:
            self.create_app()
        
        if not self.main_window:
            self.create_main_window()
        
        logger.info("Mostrando ventana principal en pantalla completa...")
        self.main_window.showMaximized()
        
        logger.info("Iniciando loop principal de la aplicación")
        return self.app.exec()
    
    def shutdown(self):
        """Cerrar aplicación limpiamente"""
        if self.main_window:
            self.main_window.close()
        
        if self.app:
            self.app.quit()
        
        logger.info("Aplicación cerrada correctamente")

# Función de conveniencia para ejecutar la aplicación
def run_application():
    """Función principal para ejecutar la aplicación"""
    logger.info(f"=== Iniciando {APP_NAME} v{APP_VERSION} ===")
    logger.info("🚀 Visor GStreamer + PyQt6 con Métricas en Tiempo Real")
    logger.info("📺 D3D11 Hardware Accelerated + Estadísticas Avanzadas")
    logger.info("📊 Métricas INSTANTÁNEAS (ventana deslizante de 5 segundos)")
    logger.info("📡 Bitrate/Datos: Valores actuales, NO acumulativos")
    logger.info("=" * 60)
    
    try:
        app = Application()
        return app.run()
    except Exception as e:
        logger.error(f"Error ejecutando aplicación: {e}")
        return 1 