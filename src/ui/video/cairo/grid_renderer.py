# -*- coding: utf-8 -*-
"""
Renderer especializado para overlay de malla/grilla
Líneas blancas paralelas sobre el video
"""

try:
    import cairo
    CAIRO_AVAILABLE = True
except ImportError:
    CAIRO_AVAILABLE = False

from ....utils.constants import CAIRO_GRID_CONFIG
from ....utils.logger import setup_logger

logger = setup_logger("GridRenderer")

class GridRenderer:
    """Renderer especializado para malla/grilla"""
    
    def __init__(self):
        self.config = CAIRO_GRID_CONFIG
        logger.debug("GridRenderer inicializado")
    
    def draw(self, context, overlay_config):
        """Dibujar malla/grilla de líneas blancas sobre el video"""
        if not CAIRO_AVAILABLE:
            return False
            
        # Verificar si las cuadrículas están habilitadas
        if not overlay_config.get('grid_enabled', True):
            return False
            
        try:
            # Verificar si la malla está habilitada en las constantes
            if not self.config.get('enabled', True):
                return False
            
            # Obtener dimensiones reales del video desde el contexto de Cairo
            surface = context.get_target()
            video_width = surface.get_width()
            video_height = surface.get_height()
            
            # Configurar estilo de líneas
            line_color = self.config['line_color']
            context.set_source_rgba(line_color[0], line_color[1], line_color[2], line_color[3])
            context.set_line_width(self.config['line_width'])
            
            # Obtener configuración de espaciado
            spacing_x = self.config['grid_spacing_x']  # 80px entre líneas verticales
            spacing_y = self.config['grid_spacing_y']  # 60px entre líneas horizontales
            offset_x = self.config['start_offset_x']   # 40px desde borde izquierdo
            offset_y = self.config['start_offset_y']   # 30px desde borde superior
            
            # === DIBUJAR LÍNEAS VERTICALES PARALELAS ===
            x = offset_x
            while x < video_width:
                context.move_to(x, 0)                    # Desde arriba
                context.line_to(x, video_height)        # Hasta abajo
                context.stroke()
                x += spacing_x
            
            # === DIBUJAR LÍNEAS HORIZONTALES PARALELAS ===
            y = offset_y
            while y < video_height:
                context.move_to(0, y)                    # Desde izquierda
                context.line_to(video_width, y)         # Hasta derecha
                context.stroke()
                y += spacing_y
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error en Grid renderer: {e}")
            return False 