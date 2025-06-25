# -*- coding: utf-8 -*-
"""
Renderer especializado para anotaciones dinámicas
Permite escribir texto en tiempo real con cursor parpadeante
"""

import time
import datetime

try:
    import cairo
    CAIRO_AVAILABLE = True
except ImportError:
    CAIRO_AVAILABLE = False

from ....utils.logger import setup_logger

logger = setup_logger("AnnotationRenderer")

class AnnotationRenderer:
    """Renderer especializado para anotaciones dinámicas"""
    
    def __init__(self):
        self.is_active = False
        self.text = ""
        
        # Configuración base
        self.config = {
            'font_family': 'Arial',
            'font_size': 28,
            'font_weight': 'bold',
            'text_color': (1.0, 1.0, 1.0, 1.0),  # Blanco por defecto
            'bg_color': (1.0, 0.65, 0.15, 0.2),  # Naranja por defecto (igual que otros overlays)
            'padding': 20,
            'border_radius': 12,
            'position_y_offset': 160,  # Posición debajo de la línea roja (ajustado)
        }
        
        logger.debug("AnnotationRenderer inicializado")
    
    def draw(self, context, overlay_config):
        """Dibujar anotación con cursor parpadeante"""
        if not CAIRO_AVAILABLE:
            return False
            
        if not self.is_active:
            return False
            
        try:
            logger.debug(f"🎨 Dibujando anotación - activo: {self.is_active}, texto: '{self.text}'")
            
            # Configurar fuente
            context.select_font_face(
                self.config['font_family'], 
                cairo.FONT_SLANT_NORMAL, 
                cairo.FONT_WEIGHT_BOLD if self.config['font_weight'] == 'bold' else cairo.FONT_WEIGHT_NORMAL
            )
            context.set_font_size(overlay_config.get('font_size', self.config['font_size']))
            
            # Texto a mostrar (sin cursor)
            display_text = self.text
            
            # Si no hay texto, mostrar box vacío con texto placeholder
            if not self.text:
                display_text = ""  # Box vacío para escribir
            
            # Obtener dimensiones del texto
            text_extents = context.text_extents(display_text)
            text_width = text_extents.width
            text_height = text_extents.height
            
            # Obtener dimensiones del video
            surface = context.get_target()
            video_width = surface.get_width()
            video_height = surface.get_height()
            
            # Posición alineada a la izquierda, crece hacia la derecha
            padding = self.config['padding']
            
            # Ancho mínimo cuando no hay texto, crece con el texto
            min_width = 150  # Ancho mínimo del box
            if self.text:
                bg_width = text_width + (padding * 2)
            else:
                bg_width = min_width
                # Para box vacío, usar altura estándar
                empty_text_extents = context.text_extents("A")  # Usar una letra para calcular altura
                text_height = empty_text_extents.height
            
            bg_height = text_height + (padding * 1.5)
            
            # Usar la misma posición X que fecha y hora - FIJO, crece hacia la derecha
            DISTANCIA_FIJA_BORDE = 150  # 150px desde borde izquierdo (igual que datetime)
            box_left = DISTANCIA_FIJA_BORDE  # Inicio fijo del box (igual que datetime)
            
            # Centrar el texto dentro del box (solo si hay texto)
            if self.text:
                box_center_x = box_left + (bg_width / 2)  # Centro del box
                text_center_x = text_width / 2  # Centro del texto
                x = box_center_x - text_center_x  # Posición para centrar el texto
            else:
                # Para box vacío, centrar el área de escritura
                x = box_left + (bg_width / 2)
                
            y = self.config['position_y_offset'] + text_height
            
            # === DIBUJAR FONDO DINÁMICO ===
            # Usar color de fondo de la configuración global si está disponible
            if 'bg_color' in overlay_config and overlay_config['bg_color']:
                qcolor = overlay_config['bg_color']
                # Usar la misma transparencia que los otros overlays (0.2 por defecto)
                bg_opacity = overlay_config.get('bg_opacity', 0.2)
                bg_color = (qcolor.red()/255.0, qcolor.green()/255.0, qcolor.blue()/255.0, bg_opacity)
            else:
                bg_color = self.config['bg_color']
            
            context.set_source_rgba(bg_color[0], bg_color[1], bg_color[2], bg_color[3])
            
            # Rectángulo con esquinas redondeadas - alineado a la izquierda
            radius = self.config['border_radius']
            self._draw_rounded_rectangle(context, box_left, y - text_height - padding/2, bg_width, bg_height, radius)
            context.fill()
            
            # === DIBUJAR TEXTO DINÁMICO ===
            if 'text_color' in overlay_config and overlay_config['text_color']:
                qcolor = overlay_config['text_color']
                text_color = (qcolor.red()/255.0, qcolor.green()/255.0, qcolor.blue()/255.0, 1.0)
            else:
                text_color = self.config['text_color']
            
            context.set_source_rgba(text_color[0], text_color[1], text_color[2], text_color[3])
            
            # Solo mostrar texto si hay contenido
            if self.text:
                context.move_to(x, y)
                context.show_text(display_text)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error en Annotation renderer: {e}")
            return False
    
    def _draw_rounded_rectangle(self, context, x, y, width, height, radius):
        """Dibujar rectángulo con esquinas redondeadas"""
        context.new_path()
        context.arc(x + radius, y + radius, radius, 3.14159, 3*3.14159/2)
        context.arc(x + width - radius, y + radius, radius, 3*3.14159/2, 0)
        context.arc(x + width - radius, y + height - radius, radius, 0, 3.14159/2)
        context.arc(x + radius, y + height - radius, radius, 3.14159/2, 3.14159)
        context.close_path()
    
    def start_annotation(self):
        """Iniciar modo de anotación"""
        self.is_active = True
        self.text = ""
        logger.info("✅ Modo de anotación iniciado - renderer activo")
        logger.debug(f"Estado: is_active={self.is_active}, text='{self.text}'")
    
    def stop_annotation(self):
        """Detener modo de anotación"""
        self.is_active = False
        self.text = ""
        logger.info("Modo de anotación detenido")
    
    def add_character(self, char):
        """Agregar carácter al texto"""
        if self.is_active:
            self.text += char
            logger.debug(f"Carácter agregado: '{char}', texto actual: '{self.text}'")
    
    def remove_character(self):
        """Eliminar último carácter (backspace)"""
        if self.is_active and self.text:
            self.text = self.text[:-1]
            logger.debug(f"Carácter eliminado, texto actual: '{self.text}'")
    
    def get_text(self):
        """Obtener texto actual"""
        return self.text
    
    def is_annotation_active(self):
        """Verificar si la anotación está activa"""
        return self.is_active 