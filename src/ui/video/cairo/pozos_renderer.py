# -*- coding: utf-8 -*-
"""
Renderer especializado para overlays de pozos y distancia
Maneja pozo inicio, pozo fin y distancia con fondos naranjas
"""

try:
    import cairo
    CAIRO_AVAILABLE = True
except ImportError:
    CAIRO_AVAILABLE = False

from ....utils.constants import (
    CAIRO_POZO_INICIO_CONFIG,
    CAIRO_POZO_FIN_CONFIG,
    CAIRO_DISTANCIA_CONFIG
)
from ....utils.logger import setup_logger

logger = setup_logger("PozosRenderer")

class PozosRenderer:
    """Renderer especializado para pozos y distancia"""
    
    def __init__(self):
        self.pozo_inicio_config = CAIRO_POZO_INICIO_CONFIG
        self.pozo_fin_config = CAIRO_POZO_FIN_CONFIG
        self.distancia_config = CAIRO_DISTANCIA_CONFIG
        logger.debug("PozosRenderer inicializado")
    
    def draw_pozo_inicio(self, context, overlay_config, pozo_inicio_text):
        """Dibujar POZO INICIO - esquina inferior izquierda"""
        if not CAIRO_AVAILABLE or not pozo_inicio_text:
            return False
            
        if not overlay_config.get('pozo_inicial_enabled', True):
            return False
            
        try:
            return self._draw_pozo_base(
                context, pozo_inicio_text, self.pozo_inicio_config, 
                is_left_aligned=True, is_bottom=True, overlay_config=overlay_config
            )
        except Exception as e:
            logger.error(f"❌ Error en Pozo Inicio renderer: {e}")
            return False
    
    def draw_pozo_fin(self, context, overlay_config, pozo_fin_text):
        """Dibujar POZO FIN - esquina inferior derecha"""
        if not CAIRO_AVAILABLE or not pozo_fin_text:
            return False
            
        if not overlay_config.get('pozo_final_enabled', True):
            return False
            
        try:
            return self._draw_pozo_base(
                context, pozo_fin_text, self.pozo_fin_config,
                is_left_aligned=False, is_bottom=True, overlay_config=overlay_config
            )
        except Exception as e:
            logger.error(f"❌ Error en Pozo Fin renderer: {e}")
            return False
    
    def draw_distancia(self, context, overlay_config, distancia_text):
        """Dibujar DISTANCIA - lado derecho inferior, encima de pozo fin"""
        if not CAIRO_AVAILABLE:
            return False
            
        if not overlay_config.get('distancia_enabled', True):
            return False
            
        try:
            return self._draw_pozo_base(
                context, distancia_text, self.distancia_config,
                is_left_aligned=False, is_bottom=True, has_vertical_offset=True, overlay_config=overlay_config
            )
        except Exception as e:
            logger.error(f"❌ Error en Distancia renderer: {e}")
            return False
    
    def _draw_pozo_base(self, context, text, config, is_left_aligned=True, is_bottom=False, has_vertical_offset=False, overlay_config=None):
        """Método base para dibujar pozos con configuración flexible"""
        if overlay_config is None:
            overlay_config = {}
            
        # Configurar fuente
        context.select_font_face(
            config['font_family'], 
            cairo.FONT_SLANT_NORMAL, 
            cairo.FONT_WEIGHT_BOLD if config['font_weight'] == 'bold' else cairo.FONT_WEIGHT_NORMAL
        )
        context.set_font_size(overlay_config.get('font_size', config['font_size']))
        
        # Obtener dimensiones del texto
        text_extents = context.text_extents(text)
        text_width = text_extents.width
        text_height = text_extents.height
        
        # Obtener dimensiones reales del video
        surface = context.get_target()
        video_width = surface.get_width()
        video_height = surface.get_height()
        
        # Configuración de posición
        padding = config['padding']
        DISTANCIA_FIJA_BORDE = 150
        DISTANCIA_FIJA_INFERIOR = 97
        
        # Aplicar offset vertical si es necesario (para distancia)
        if has_vertical_offset:
            DISTANCIA_FIJA_INFERIOR += config.get('vertical_offset', 0)
        
        # Dimensiones del fondo
        bg_width = text_width + (padding * 2)
        bg_height = text_height + (padding * 1.5)
        
        # Calcular posición según alineación
        if is_left_aligned:
            # Crece hacia la derecha (pozo inicio)
            box_left = DISTANCIA_FIJA_BORDE
            x = box_left + padding
        else:
            # Crece hacia la izquierda (pozo fin, distancia)
            box_right = video_width - DISTANCIA_FIJA_BORDE
            box_left = box_right - bg_width
            x = box_left + padding
        
        # Calcular posición vertical
        if is_bottom:
            y = video_height - DISTANCIA_FIJA_INFERIOR + text_height
        else:
            y = padding + text_height + 40  # Posición superior
        
        # === DIBUJAR FONDO DINÁMICO TRANSPARENTE ===
        # Usar color de fondo de la configuración global si está disponible
        if 'bg_color' in overlay_config and overlay_config['bg_color']:
            # Convertir QColor a RGBA normalizado
            qcolor = overlay_config['bg_color']
            bg_opacity = overlay_config.get('bg_opacity', 0.6)
            bg_color = (qcolor.red()/255.0, qcolor.green()/255.0, qcolor.blue()/255.0, bg_opacity)
        else:
            # Usar color por defecto
            bg_color = config['bg_color']
        
        context.set_source_rgba(bg_color[0], bg_color[1], bg_color[2], bg_color[3])
        
        # Rectángulo con esquinas redondeadas
        radius = config['border_radius']
        self._draw_rounded_rectangle(
            context, box_left, y - text_height - padding/2, 
            bg_width, bg_height, radius
        )
        context.fill()
        
        # === DIBUJAR TEXTO DINÁMICO ===
        # Usar color de texto de la configuración global si está disponible
        if 'text_color' in overlay_config and overlay_config['text_color']:
            qcolor = overlay_config['text_color']
            text_color = (qcolor.red()/255.0, qcolor.green()/255.0, qcolor.blue()/255.0, 1.0)
        else:
            text_color = config['text_color']
        
        context.set_source_rgba(text_color[0], text_color[1], text_color[2], text_color[3])
        context.move_to(x, y)
        context.show_text(text)
        
        return True
    
    def _draw_rounded_rectangle(self, context, x, y, width, height, radius):
        """Dibujar rectángulo con esquinas redondeadas"""
        context.new_path()
        context.arc(x + radius, y + radius, radius, 3.14159, 3*3.14159/2)
        context.arc(x + width - radius, y + radius, radius, 3*3.14159/2, 0)
        context.arc(x + width - radius, y + height - radius, radius, 0, 3.14159/2)
        context.arc(x + radius, y + height - radius, radius, 3.14159/2, 3.14159)
        context.close_path() 