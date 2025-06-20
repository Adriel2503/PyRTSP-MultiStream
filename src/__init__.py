# -*- coding: utf-8 -*-
"""
PyRTSP-FastStream - Sistema Profesional de Streaming RTSP
Paquete principal del proyecto
"""

__version__ = "1.0.0"
__author__ = "PyRTSP-FastStream Team"
__description__ = "Sistema de streaming RTSP de ultra baja latencia"

# Importaciones principales del paquete
from .core.application import Application
from .ui.main_window import MainWindow
from .ui.video_widget import VideoWidget
from .metrics.stream_metrics import StreamMetrics

__all__ = [
    "Application",
    "MainWindow", 
    "VideoWidget",
    "StreamMetrics"
] 