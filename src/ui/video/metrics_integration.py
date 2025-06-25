# -*- coding: utf-8 -*-
"""
Integración con StreamMetrics
Maneja probes de buffers H.264 y cálculo de métricas
"""

import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst

from ...utils.constants import DEBUG_SHOW_FIRST_BUFFERS, DEBUG_BUFFER_INFO
from ...utils.logger import setup_logger
from ...metrics.stream_metrics import StreamMetrics

logger = setup_logger("MetricsIntegration")

class MetricsIntegration:
    """Integración especializada con métricas de stream"""
    
    def __init__(self):
        self.metrics = StreamMetrics()
        logger.info("MetricsIntegration inicializado")
    
    def reset(self):
        """Resetear métricas"""
        self.metrics.reset()
        logger.debug("Métricas reseteadas")
    
    def get_metrics(self):
        """Obtener objeto de métricas para acceso externo"""
        return self.metrics
    
    def on_frame_probe(self, pad, info):
        """Probe para capturar estadísticas de datos H.264 comprimidos"""
        buffer = info.get_buffer()
        if buffer:
            # Obtener tamaño del buffer H.264 comprimido
            buffer_size = buffer.get_size()
            
            # SIMPLE: Cada buffer = un "frame" (como funcionaba originalmente)
            # Esto daba FPS correctos (~20), mantenemos esa lógica
            self.metrics.add_frame(buffer_size)
            
            # Debug: mostrar primeros buffers para verificar tamaños
            if DEBUG_BUFFER_INFO and self.metrics.frame_count <= DEBUG_SHOW_FIRST_BUFFERS:
                logger.debug(f"Buffer #{self.metrics.frame_count}: {buffer_size} bytes")
        
        return Gst.PadProbeReturn.OK 