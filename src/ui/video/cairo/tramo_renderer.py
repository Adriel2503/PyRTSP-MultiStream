# -*- coding: utf-8 -*-
"""
Renderer especializado para overlay de REF. TRAMO
Fondo naranja transparente, esquina superior derecha
"""

try:
    import cairo
    CAIRO_AVAILABLE = True
except ImportError:
    CAIRO_AVAILABLE = False

from ....utils.constants import CAIRO_REF_TRAMO_CONFIG
from ....utils.logger import setup_logger

logger = setup_logger("TramoRenderer")

class TramoRenderer:
    """Renderer especializado para REF. TRAMO"""
    
    def __init__(self):
        self.config = CAIRO_REF_TRAMO_CONFIG
        logger.debug("TramoRenderer inicializado")
    
    def draw(self, context, overlay_config, ref_tramo_text):
        """Dibujar REF. TRAMO con fondo dinámico transparente"""
        if not CAIRO_AVAILABLE or not ref_tramo_text:
            return False
            
        # Verificar si el tramo está habilitado
        if not overlay_config.get('tramo_enabled', True):
            return False
            
        try:
            # Configurar fuente
            context.select_font_face(
                self.config['font_family'], 
                cairo.FONT_SLANT_NORMAL, 
                cairo.FONT_WEIGHT_BOLD if self.config['font_weight'] == 'bold' else cairo.FONT_WEIGHT_NORMAL
            )
            context.set_font_size(overlay_config.get('font_size', self.config['font_size']))
            
            # Obtener dimensiones del texto
            text_extents = context.text_extents(ref_tramo_text)
            text_width = text_extents.width
            text_height = text_extents.height
            
            # Obtener dimensiones reales del video
            surface = context.get_target()
            video_width = surface.get_width()
            video_height = surface.get_height()
            
            # SISTEMA SIMÉTRICO Y CONSISTENTE: Posiciones fijas X e Y
            padding = self.config['padding']
            DISTANCIA_FIJA_BORDE_X = 150  # 150px desde borde derecho (simétrico)
            DISTANCIA_FIJA_BORDE_Y = 50   # 50px desde borde superior (igual que datetime)
            
            # Dimensiones del fondo
            bg_width = text_width + (padding * 2)
            bg_height = text_height + (padding * 1.5)
            
            # Posiciones fijas del rectángulo (box)
            box_right = video_width - DISTANCIA_FIJA_BORDE_X  # X final del box: 2560 - 150 = 2410px
            box_left = box_right - bg_width  # X inicial del box (crece hacia izquierda)
            box_top = DISTANCIA_FIJA_BORDE_Y   # Y del rectángulo: 50px (fijo, igual que datetime)
            
            # Posiciones del texto (dentro del box)
            x = box_left + padding  # X del texto: box_left + 25px
            y = box_top + padding + text_height  # Y del texto: 50 + 25 + 32 = 107px (igual que datetime)
            
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
            
            # Rectángulo con esquinas redondeadas - TRAMO crece hacia IZQUIERDA
            radius = self.config['border_radius']
            self._draw_rounded_rectangle(context, box_left, box_top, bg_width, bg_height, radius)
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
            context.show_text(ref_tramo_text)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error en Tramo renderer: {e}")
            return False
    
    def _draw_rounded_rectangle(self, context, x, y, width, height, radius):
        """Dibujar rectángulo con esquinas redondeadas"""
        context.new_path()
        context.arc(x + radius, y + radius, radius, 3.14159, 3*3.14159/2)
        context.arc(x + width - radius, y + radius, radius, 3*3.14159/2, 0)
        context.arc(x + width - radius, y + height - radius, radius, 0, 3.14159/2)
        context.arc(x + radius, y + height - radius, radius, 3.14159/2, 3.14159)
        context.close_path() 