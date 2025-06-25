# -*- coding: utf-8 -*-
"""
Widget de video principal simplificado
Coordina GStreamerManager, OverlayManager y MetricsIntegration
"""

from PyQt6.QtWidgets import QFrame, QSizePolicy
from PyQt6.QtCore import Qt, pyqtSignal

from ...utils.constants import (
    VIDEO_WIDGET_STYLE,
    DEFAULT_VIDEO_SIZE,
    VIDEO_SCALE_OPTIONS,
    PREFERRED_VIDEO_SCALE
)
from ...utils.logger import setup_logger

from .gstreamer_manager import GStreamerManager
from .overlay_manager import OverlayManager
from .metrics_integration import MetricsIntegration

logger = setup_logger("VideoWidget")

class VideoWidget(QFrame):
    """Widget principal de video - coordinador modular"""
    
    # Señal emitida cuando se hace clic en el botón "+"
    plus_button_clicked = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        
        # Managers especializados
        self.gstreamer_manager = GStreamerManager(self)
        self.overlay_manager = OverlayManager()
        self.metrics_integration = MetricsIntegration()
        
        # Conectar managers entre sí
        self.gstreamer_manager.set_managers(self.overlay_manager, self.metrics_integration)
        
        self.setup_widget()
        logger.info("VideoWidget inicializado con arquitectura modular")
        
    def setup_widget(self):
        """Configurar el widget para video"""
        # Obtener tamaño según preferencia
        video_size = VIDEO_SCALE_OPTIONS.get(PREFERRED_VIDEO_SCALE, DEFAULT_VIDEO_SIZE)
        
        logger.info(f"🎯 CONFIGURACIÓN DE VIDEO: {PREFERRED_VIDEO_SCALE}")
        logger.info(f"📐 Tamaño del widget: {video_size[0]}x{video_size[1]}")
        
        if PREFERRED_VIDEO_SCALE in ['full', 'half', 'quarter']:
            # Usar tamaño fijo para submúltiplos exactos
            self.setFixedSize(*video_size)
            logger.info(f"📏 Tamaño FIJO: {video_size[0]}x{video_size[1]} (sin bandas negras)")
        else:
            # Escalado automático para 'auto'
            self.setMinimumSize(*video_size)
            self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            logger.info(f"📈 Tamaño EXPANDIBLE: mínimo {video_size[0]}x{video_size[1]}")
        
        self.setStyleSheet(VIDEO_WIDGET_STYLE)
        
        # Asegurar que el widget sea nativo para overlay
        self.setAttribute(Qt.WidgetAttribute.WA_NativeWindow, True)
        self.setAttribute(Qt.WidgetAttribute.WA_PaintOnScreen, True)
        
        logger.debug("Widget configurado para overlay nativo")
    
    def start_stream(self, rtsp_url):
        """Iniciar stream delegando a GStreamerManager"""
        return self.gstreamer_manager.start_stream(rtsp_url)
    
    def stop_stream(self):
        """Detener stream delegando a GStreamerManager"""
        self.gstreamer_manager.stop_stream()
    
    def update_overlay_config(self, config):
        """Actualizar configuración de overlays"""
        self.overlay_manager.update_config(config)
    
    def update_ref_tramo(self, ref_tramo):
        """Actualizar texto de REF. TRAMO"""
        self.overlay_manager.update_ref_tramo(ref_tramo)
    
    def update_pozo_inicio(self, pozo_inicio):
        """Actualizar texto de POZO INICIO"""
        self.overlay_manager.update_pozo_inicio(pozo_inicio)
    
    def update_pozo_fin(self, pozo_fin):
        """Actualizar texto de POZO FIN"""
        self.overlay_manager.update_pozo_fin(pozo_fin)
    
    def update_distancia(self, distancia):
        """Actualizar texto de DISTANCIA"""
        self.overlay_manager.update_distancia(distancia)
    
    def get_metrics(self):
        """Obtener métricas del stream"""
        return self.metrics_integration.get_metrics()
    
    def get_overlay_config(self):
        """Obtener configuración actual de overlays"""
        config = self.overlay_manager.overlay_config.copy()
        # Incluir estado del formulario
        config['form_filled'] = self.overlay_manager.is_form_filled()
        return config
    
    def enable_form_elements(self):
        """Habilitar elementos dependientes del formulario"""
        self.overlay_manager.enable_form_elements()
    
    def resizeEvent(self, event):
        """Manejar redimensionamiento del widget"""
        super().resizeEvent(event)
        # Los overlays nativos se redimensionan automáticamente
        logger.debug(f"Widget redimensionado a: {event.size().width()}x{event.size().height()}") 