# -*- coding: utf-8 -*-
"""
Renderer especializado para overlay de fecha/hora
Fondo naranja transparente, posición fija izquierda
"""

import datetime

try:
    import cairo
    CAIRO_AVAILABLE = True
except ImportError:
    CAIRO_AVAILABLE = False

from ....utils.constants import CAIRO_OVERLAY_CONFIG
from ....utils.logger import setup_logger

logger = setup_logger("DateTimeRenderer")

class DateTimeRenderer:
    """Renderer especializado para fecha/hora"""
    
    def __init__(self):
        self.config = CAIRO_OVERLAY_CONFIG
        logger.debug("DateTimeRenderer inicializado")
    
    def draw(self, context, overlay_config):
        """Dibujar fecha/hora con fondo dinámico transparente"""
        if not CAIRO_AVAILABLE:
            return False
            
        # Verificar si la fecha está habilitada
        if not overlay_config.get('fecha_enabled', True):
            return False
            
        try:
            # Obtener fecha/hora actual
            now = datetime.datetime.now()
            datetime_text = now.strftime(self.config['datetime_format'])
            
            # Configurar fuente
            context.select_font_face(
                self.config['font_family'], 
                cairo.FONT_SLANT_NORMAL, 
                cairo.FONT_WEIGHT_BOLD if self.config['font_weight'] == 'bold' else cairo.FONT_WEIGHT_NORMAL
            )
            context.set_font_size(overlay_config.get('font_size', self.config['font_size']))
            
            # Obtener dimensiones del texto
            text_extents = context.text_extents(datetime_text)
            text_width = text_extents.width
            text_height = text_extents.height
            
            # SISTEMA SIMÉTRICO: Box fijo izquierda, crece hacia la derecha
            padding = self.config['padding']
            DISTANCIA_FIJA_BORDE = 150  # 150px desde borde izquierdo
            
            box_left = DISTANCIA_FIJA_BORDE  # Inicio fijo del box
            x = box_left + padding  # Posición del texto (dentro del box)
            y = padding + text_height + 40  # Altura estándar
            
            # Dimensiones del fondo
            bg_width = text_width + (padding * 2)
            bg_height = text_height + (padding * 1.5)
            
            # === DIBUJAR FONDO DINÁMICO TRANSPARENTE ===
            # Usar color de fondo de la configuración global si está disponible
            if 'bg_color' in overlay_config and overlay_config['bg_color']:
                # Convertir QColor a RGBA normalizado
                qcolor = overlay_config['bg_color']
                bg_opacity = overlay_config.get('bg_opacity', 0.6)
                bg_color = (qcolor.red()/255.0, qcolor.green()/255.0, qcolor.blue()/255.0, bg_opacity)
            else:
                # Usar color por defecto
                bg_color = self.config['bg_color']
            
            context.set_source_rgba(bg_color[0], bg_color[1], bg_color[2], bg_color[3])
            
            # Rectángulo con esquinas redondeadas - FECHA crece hacia DERECHA
            radius = self.config['border_radius']
            self._draw_rounded_rectangle(context, box_left, y - text_height - padding/2, bg_width, bg_height, radius)
            context.fill()
            
            # === DIBUJAR TEXTO DINÁMICO ===
            # Usar color de texto de la configuración global si está disponible
            if 'text_color' in overlay_config and overlay_config['text_color']:
                qcolor = overlay_config['text_color']
                text_color = (qcolor.red()/255.0, qcolor.green()/255.0, qcolor.blue()/255.0, 1.0)
            else:
                text_color = self.config['text_color']
            
            context.set_source_rgba(text_color[0], text_color[1], text_color[2], text_color[3])
            context.move_to(x, y)
            context.show_text(datetime_text)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error en DateTime renderer: {e}")
            return False
    
    def _draw_rounded_rectangle(self, context, x, y, width, height, radius):
        """Dibujar rectángulo con esquinas redondeadas"""
        context.new_path()
        context.arc(x + radius, y + radius, radius, 3.14159, 3*3.14159/2)
        context.arc(x + width - radius, y + radius, radius, 3*3.14159/2, 0)
        context.arc(x + width - radius, y + height - radius, radius, 0, 3.14159/2)
        context.arc(x + radius, y + height - radius, radius, 3.14159/2, 3.14159)
        context.close_path() 