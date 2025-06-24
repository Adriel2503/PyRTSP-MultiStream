# -*- coding: utf-8 -*-
"""
Widget de video para streaming GStreamer
Extrae la funcionalidad de SimpleGStreamerWidget del código original
"""

import sys
import datetime
import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstVideo', '1.0')
from gi.repository import Gst, GLib, GstVideo

# Importar Cairo si está disponible
try:
    import cairo
    CAIRO_AVAILABLE = True
except ImportError:
    CAIRO_AVAILABLE = False

from PyQt6.QtWidgets import QFrame, QSizePolicy, QLabel
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from ..utils.constants import (
    GSTREAMER_PIPELINE_TEMPLATE,
    VIDEO_WIDGET_STYLE,
    DEFAULT_VIDEO_SIZE,
    VIDEO_SCALE_OPTIONS,
    PREFERRED_VIDEO_SCALE,
    DEBUG_SHOW_FIRST_BUFFERS,
    DEBUG_BUFFER_INFO,
    CAIRO_GRID_CONFIG,
    CAIRO_OVERLAY_CONFIG,
    CAIRO_REF_TRAMO_CONFIG,
    CAIRO_POZO_INICIO_CONFIG,
    CAIRO_POZO_FIN_CONFIG,
    TIMEOVERLAY_CONFIG
)
from ..utils.logger import setup_logger
from ..metrics.stream_metrics import StreamMetrics

logger = setup_logger("VideoWidget")

class VideoWidget(QFrame):
    """Widget optimizado para mostrar video de GStreamer con métricas integradas"""
    
    # Señal emitida cuando se hace clic en el botón "+"
    plus_button_clicked = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.pipeline = None
        self.bus = None
        self.metrics = StreamMetrics()
        
        # Referencias a overlays nativos de GStreamer
        self.cairo_grid = None
        self.cairo_datetime = None
        self.cairo_ref_tramo = None
        self.cairo_pozo_inicio = None
        self.cairo_pozo_fin = None
        
        # Variables para almacenar textos de overlays
        self.ref_tramo_text = ""
        self.pozo_inicio_text = ""
        self.pozo_fin_text = ""
        
        # Control de visibilidad de overlays (por defecto todos activos)
        self.overlay_config = {
            'grid_enabled': True,
            'fecha_enabled': True,
            'tramo_enabled': True,
            'pozo_inicial_enabled': True,
            'pozo_final_enabled': True
        }
        
        self.setup_widget()
        # Eliminamos create_overlay_labels() ya que usaremos overlays nativos
        logger.info("VideoWidget inicializado con overlays nativos")
        
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
    
    def _configure_native_overlays(self):
        """Configurar overlays nativos de GStreamer"""
        try:
            # === CAIRO OVERLAY MALLA/GRILLA - Se dibuja primero (debajo de los textos) ===
            self.cairo_grid = self.pipeline.get_by_name("cairo_grid")
            if self.cairo_grid and CAIRO_AVAILABLE:
                # Conectar callback para dibujar la malla
                self.cairo_grid.connect("draw", self._on_cairo_draw_grid)
                logger.info("✅ Cairo overlay MALLA configurado - líneas blancas de fondo")
            elif self.cairo_grid:
                logger.warning("⚠️ Cairo no disponible para MALLA")
            else:
                logger.error("❌ No se encontró cairo_grid en el pipeline")
            
            # === CAIRO OVERLAY - Fecha y hora con fondo naranja transparente ===
            self.cairo_datetime = self.pipeline.get_by_name("cairo_datetime")
            if self.cairo_datetime and CAIRO_AVAILABLE:
                # Conectar callback para dibujar la fecha/hora
                self.cairo_datetime.connect("draw", self._on_cairo_draw_datetime)
                logger.info("✅ Cairo overlay configurado - fecha/hora con fondo naranja")
            elif self.cairo_datetime:
                logger.warning("⚠️ Cairo no disponible, usando textoverlay simple")
                # Fallback a textoverlay simple si Cairo no está disponible
                # (implementar fallback si es necesario)
            else:
                logger.error("❌ No se encontró cairo_datetime en el pipeline")
            
            # === CAIRO OVERLAY REF. TRAMO - Esquina superior derecha ===
            self.cairo_ref_tramo = self.pipeline.get_by_name("cairo_ref_tramo")
            if self.cairo_ref_tramo and CAIRO_AVAILABLE:
                # Conectar callback para dibujar REF. TRAMO
                self.cairo_ref_tramo.connect("draw", self._on_cairo_draw_ref_tramo)
                logger.info("✅ Cairo overlay REF. TRAMO configurado - esquina superior derecha")
            elif self.cairo_ref_tramo:
                logger.warning("⚠️ Cairo no disponible para REF. TRAMO")
            else:
                logger.error("❌ No se encontró cairo_ref_tramo en el pipeline")
            
            # === CAIRO OVERLAY POZO INICIO - Esquina inferior izquierda ===
            self.cairo_pozo_inicio = self.pipeline.get_by_name("cairo_pozo_inicio")
            if self.cairo_pozo_inicio and CAIRO_AVAILABLE:
                # Conectar callback para dibujar POZO INICIO
                self.cairo_pozo_inicio.connect("draw", self._on_cairo_draw_pozo_inicio)
                logger.info("✅ Cairo overlay POZO INICIO configurado - esquina inferior izquierda")
            elif self.cairo_pozo_inicio:
                logger.warning("⚠️ Cairo no disponible para POZO INICIO")
            else:
                logger.error("❌ No se encontró cairo_pozo_inicio en el pipeline")
            
            # === CAIRO OVERLAY POZO FIN - Esquina inferior derecha ===
            self.cairo_pozo_fin = self.pipeline.get_by_name("cairo_pozo_fin")
            if self.cairo_pozo_fin and CAIRO_AVAILABLE:
                # Conectar callback para dibujar POZO FIN
                self.cairo_pozo_fin.connect("draw", self._on_cairo_draw_pozo_fin)
                logger.info("✅ Cairo overlay POZO FIN configurado - esquina inferior derecha")
            elif self.cairo_pozo_fin:
                logger.warning("⚠️ Cairo no disponible para POZO FIN")
            else:
                logger.error("❌ No se encontró cairo_pozo_fin en el pipeline")

                
        except Exception as e:
            logger.error(f"❌ Error configurando overlays nativos: {e}")
    
    def _on_cairo_draw_datetime(self, element, context, timestamp, duration, user_data=None):
        """Callback para dibujar fecha/hora con fondo naranja transparente usando Cairo"""
        if not CAIRO_AVAILABLE:
            return False
            
        # Verificar si la fecha está habilitada en la configuración
        if not self.overlay_config.get('fecha_enabled', True):
            return False
            
        try:
            config = CAIRO_OVERLAY_CONFIG
            
            # Obtener fecha/hora actual
            now = datetime.datetime.now()
            datetime_text = now.strftime(config['datetime_format'])
            
            # Configurar fuente
            context.select_font_face(
                config['font_family'], 
                cairo.FONT_SLANT_NORMAL, 
                cairo.FONT_WEIGHT_BOLD if config['font_weight'] == 'bold' else cairo.FONT_WEIGHT_NORMAL
            )
            context.set_font_size(config['font_size'])
            
            # Obtener dimensiones del texto
            text_extents = context.text_extents(datetime_text)
            text_width = text_extents.width
            text_height = text_extents.height
            
            # SISTEMA SIMÉTRICO: Box fijo izquierda, crece hacia la derecha
            padding = config['padding']
            DISTANCIA_FIJA_BORDE = 150  # 150px desde borde izquierdo
            
            box_left = DISTANCIA_FIJA_BORDE  # Inicio fijo del box
            x = box_left + padding  # Posición del texto (dentro del box)
            y = padding + text_height + 40  # Altura estándar
            
            # Dimensiones del fondo
            bg_width = text_width + (padding * 2)
            bg_height = text_height + (padding * 1.5)
            
            # === DIBUJAR FONDO NARANJA TRANSPARENTE ===
            bg_color = config['bg_color']
            context.set_source_rgba(bg_color[0], bg_color[1], bg_color[2], bg_color[3])
            
            # Rectángulo con esquinas redondeadas - FECHA crece hacia DERECHA
            radius = config['border_radius']
            context.new_path()
            context.arc(box_left + radius, y - text_height - padding/2 + radius, radius, 3.14159, 3*3.14159/2)
            context.arc(box_left + bg_width - radius, y - text_height - padding/2 + radius, radius, 3*3.14159/2, 0)
            context.arc(box_left + bg_width - radius, y - padding/2 + text_height - radius, radius, 0, 3.14159/2)
            context.arc(box_left + radius, y - padding/2 + text_height - radius, radius, 3.14159/2, 3.14159)
            context.close_path()
            context.fill()
            
            # === DIBUJAR TEXTO BLANCO ===
            text_color = config['text_color']
            context.set_source_rgba(text_color[0], text_color[1], text_color[2], text_color[3])
            context.move_to(x, y)
            context.show_text(datetime_text)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error en Cairo overlay: {e}")
            return False
    
    def _on_cairo_draw_ref_tramo(self, element, context, timestamp, duration, user_data=None):
        """Callback para dibujar REF. TRAMO con fondo naranja transparente usando Cairo"""
        if not CAIRO_AVAILABLE or not self.ref_tramo_text:
            return False
            
        # Verificar si el tramo está habilitado en la configuración
        if not self.overlay_config.get('tramo_enabled', True):
            return False
            
        try:
            config = CAIRO_REF_TRAMO_CONFIG
            
            # Usar el texto almacenado de REF. TRAMO
            ref_tramo_text = self.ref_tramo_text
            
            # Configurar fuente
            context.select_font_face(
                config['font_family'], 
                cairo.FONT_SLANT_NORMAL, 
                cairo.FONT_WEIGHT_BOLD if config['font_weight'] == 'bold' else cairo.FONT_WEIGHT_NORMAL
            )
            context.set_font_size(config['font_size'])
            
            # Obtener dimensiones del texto
            text_extents = context.text_extents(ref_tramo_text)
            text_width = text_extents.width
            text_height = text_extents.height
            
            # Obtener dimensiones reales del video desde el contexto de Cairo
            surface = context.get_target()
            video_width = surface.get_width()
            video_height = surface.get_height()
            
            # SISTEMA SIMÉTRICO: Box fijo derecha, crece hacia la izquierda
            padding = config['padding']
            DISTANCIA_FIJA_BORDE = 150  # 150px desde borde derecho (simétrico)
            
            # Dimensiones del fondo
            bg_width = text_width + (padding * 2)
            bg_height = text_height + (padding * 1.5)
            
            # Posición: box fijo desde borde derecho, crece hacia izquierda
            box_right = video_width - DISTANCIA_FIJA_BORDE  # Final fijo del box (1130px)
            box_left = box_right - bg_width  # Inicio variable del box (crece hacia izquierda)
            x = box_left + padding  # Posición del texto (dentro del box)
            y = padding + text_height + 40  # Misma altura que datetime
            
            # === DIBUJAR FONDO NARANJA TRANSPARENTE ===
            bg_color = config['bg_color']
            context.set_source_rgba(bg_color[0], bg_color[1], bg_color[2], bg_color[3])
            
            # Rectángulo con esquinas redondeadas - TRAMO crece hacia IZQUIERDA
            radius = config['border_radius']
            context.new_path()
            context.arc(box_left + radius, y - text_height - padding/2 + radius, radius, 3.14159, 3*3.14159/2)
            context.arc(box_right - radius, y - text_height - padding/2 + radius, radius, 3*3.14159/2, 0)
            context.arc(box_right - radius, y - padding/2 + text_height - radius, radius, 0, 3.14159/2)
            context.arc(box_left + radius, y - padding/2 + text_height - radius, radius, 3.14159/2, 3.14159)
            context.close_path()
            context.fill()
            
            # === DIBUJAR TEXTO BLANCO ===
            text_color = config['text_color']
            context.set_source_rgba(text_color[0], text_color[1], text_color[2], text_color[3])
            context.move_to(x, y)
            context.show_text(ref_tramo_text)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error en Cairo overlay REF. TRAMO: {e}")
            return False
    
    def update_ref_tramo(self, ref_tramo):
        """Actualizar texto de REF. TRAMO"""
        self.ref_tramo_text = ref_tramo if ref_tramo else ""
        logger.info(f"✅ REF. TRAMO actualizado: '{self.ref_tramo_text}'")
    
    def _on_cairo_draw_grid(self, element, context, timestamp, duration, user_data=None):
        """Callback para dibujar malla/grilla de líneas blancas sobre el video"""
        if not CAIRO_AVAILABLE:
            return False
            
        # Verificar si las cuadrículas están habilitadas en la configuración
        if not self.overlay_config.get('grid_enabled', True):
            return False
            
        try:
            config = CAIRO_GRID_CONFIG
            
            # Verificar si la malla está habilitada en las constantes
            if not config.get('enabled', True):
                return False
            
            # Obtener dimensiones reales del video desde el contexto de Cairo
            surface = context.get_target()
            video_width = surface.get_width()
            video_height = surface.get_height()
            
            # Configurar estilo de líneas
            line_color = config['line_color']
            context.set_source_rgba(line_color[0], line_color[1], line_color[2], line_color[3])
            context.set_line_width(config['line_width'])
            
            # Obtener configuración de espaciado
            spacing_x = config['grid_spacing_x']  # 80px entre líneas verticales
            spacing_y = config['grid_spacing_y']  # 60px entre líneas horizontales
            offset_x = config['start_offset_x']   # 40px desde borde izquierdo
            offset_y = config['start_offset_y']   # 30px desde borde superior
            
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
            logger.error(f"❌ Error en Cairo overlay MALLA: {e}")
            return False
    
    def _on_cairo_draw_pozo_inicio(self, element, context, timestamp, duration, user_data=None):
        """Callback para dibujar POZO INICIO con fondo naranja transparente usando Cairo - ESQUINA INFERIOR IZQUIERDA"""
        if not CAIRO_AVAILABLE or not self.pozo_inicio_text:
            return False
            
        # Verificar si el pozo inicial está habilitado en la configuración
        if not self.overlay_config.get('pozo_inicial_enabled', True):
            return False
            
        try:
            config = CAIRO_POZO_INICIO_CONFIG
            
            # Usar el texto almacenado de POZO INICIO
            pozo_inicio_text = self.pozo_inicio_text
            
            # Configurar fuente
            context.select_font_face(
                config['font_family'], 
                cairo.FONT_SLANT_NORMAL, 
                cairo.FONT_WEIGHT_BOLD if config['font_weight'] == 'bold' else cairo.FONT_WEIGHT_NORMAL
            )
            context.set_font_size(config['font_size'])
            
            # Obtener dimensiones del texto
            text_extents = context.text_extents(pozo_inicio_text)
            text_width = text_extents.width
            text_height = text_extents.height
            
            # Obtener dimensiones reales del video desde el contexto de Cairo
            surface = context.get_target()
            video_width = surface.get_width()
            video_height = surface.get_height()
            
            # SISTEMA SIMÉTRICO INFERIOR: Box fijo izquierda, crece hacia la derecha
            padding = config['padding']
            DISTANCIA_FIJA_BORDE = 150  # 150px desde borde izquierdo (simétrico con fecha/hora)
            DISTANCIA_FIJA_INFERIOR = 97  # 150px desde borde inferior (simétrico con overlays superiores)
            
            # Dimensiones del fondo
            bg_width = text_width + (padding * 2)
            bg_height = text_height + (padding * 1.5)
            
            # Posición: box fijo desde borde izquierdo, crece hacia derecha
            box_left = DISTANCIA_FIJA_BORDE  # Inicio fijo del box
            x = box_left + padding  # Posición del texto (dentro del box)
            y = video_height - DISTANCIA_FIJA_INFERIOR + text_height  # Posición vertical desde abajo
            
            # === DIBUJAR FONDO NARANJA TRANSPARENTE ===
            bg_color = config['bg_color']
            context.set_source_rgba(bg_color[0], bg_color[1], bg_color[2], bg_color[3])
            
            # Rectángulo con esquinas redondeadas - POZO INICIO crece hacia DERECHA
            radius = config['border_radius']
            context.new_path()
            context.arc(box_left + radius, y - text_height - padding/2 + radius, radius, 3.14159, 3*3.14159/2)
            context.arc(box_left + bg_width - radius, y - text_height - padding/2 + radius, radius, 3*3.14159/2, 0)
            context.arc(box_left + bg_width - radius, y - padding/2 + text_height - radius, radius, 0, 3.14159/2)
            context.arc(box_left + radius, y - padding/2 + text_height - radius, radius, 3.14159/2, 3.14159)
            context.close_path()
            context.fill()
            
            # === DIBUJAR TEXTO BLANCO ===
            text_color = config['text_color']
            context.set_source_rgba(text_color[0], text_color[1], text_color[2], text_color[3])
            context.move_to(x, y)
            context.show_text(pozo_inicio_text)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error en Cairo overlay POZO INICIO: {e}")
            return False
    
    def _on_cairo_draw_pozo_fin(self, element, context, timestamp, duration, user_data=None):
        """Callback para dibujar POZO FIN con fondo naranja transparente usando Cairo - ESQUINA INFERIOR DERECHA"""
        if not CAIRO_AVAILABLE or not self.pozo_fin_text:
            return False
            
        # Verificar si el pozo final está habilitado en la configuración
        if not self.overlay_config.get('pozo_final_enabled', True):
            return False
            
        try:
            config = CAIRO_POZO_FIN_CONFIG
            
            # Usar el texto almacenado de POZO FIN
            pozo_fin_text = self.pozo_fin_text
            
            # Configurar fuente
            context.select_font_face(
                config['font_family'], 
                cairo.FONT_SLANT_NORMAL, 
                cairo.FONT_WEIGHT_BOLD if config['font_weight'] == 'bold' else cairo.FONT_WEIGHT_NORMAL
            )
            context.set_font_size(config['font_size'])
            
            # Obtener dimensiones del texto
            text_extents = context.text_extents(pozo_fin_text)
            text_width = text_extents.width
            text_height = text_extents.height
            
            # Obtener dimensiones reales del video desde el contexto de Cairo
            surface = context.get_target()
            video_width = surface.get_width()
            video_height = surface.get_height()
            
            # SISTEMA SIMÉTRICO INFERIOR: Box fijo derecha, crece hacia la izquierda
            padding = config['padding']
            DISTANCIA_FIJA_BORDE = 150  # 150px desde borde derecho (simétrico con REF. TRAMO)
            DISTANCIA_FIJA_INFERIOR = 97  # 150px desde borde inferior (simétrico con overlays superiores)
            
            # Dimensiones del fondo
            bg_width = text_width + (padding * 2)
            bg_height = text_height + (padding * 1.5)
            
            # Posición: box fijo desde borde derecho, crece hacia izquierda
            box_right = video_width - DISTANCIA_FIJA_BORDE  # Final fijo del box
            box_left = box_right - bg_width  # Inicio variable del box (crece hacia izquierda)
            x = box_left + padding  # Posición del texto (dentro del box)
            y = video_height - DISTANCIA_FIJA_INFERIOR + text_height  # Posición vertical desde abajo
            
            # === DIBUJAR FONDO NARANJA TRANSPARENTE ===
            bg_color = config['bg_color']
            context.set_source_rgba(bg_color[0], bg_color[1], bg_color[2], bg_color[3])
            
            # Rectángulo con esquinas redondeadas - POZO FIN crece hacia IZQUIERDA
            radius = config['border_radius']
            context.new_path()
            context.arc(box_left + radius, y - text_height - padding/2 + radius, radius, 3.14159, 3*3.14159/2)
            context.arc(box_right - radius, y - text_height - padding/2 + radius, radius, 3*3.14159/2, 0)
            context.arc(box_right - radius, y - padding/2 + text_height - radius, radius, 0, 3.14159/2)
            context.arc(box_left + radius, y - padding/2 + text_height - radius, radius, 3.14159/2, 3.14159)
            context.close_path()
            context.fill()
            
            # === DIBUJAR TEXTO BLANCO ===
            text_color = config['text_color']
            context.set_source_rgba(text_color[0], text_color[1], text_color[2], text_color[3])
            context.move_to(x, y)
            context.show_text(pozo_fin_text)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error en Cairo overlay POZO FIN: {e}")
            return False
    
    def update_pozo_inicio(self, pozo_inicio):
        """Actualizar texto de POZO INICIO"""
        self.pozo_inicio_text = pozo_inicio if pozo_inicio else ""
        logger.info(f"✅ POZO INICIO actualizado: '{self.pozo_inicio_text}'")
    
    def update_pozo_fin(self, pozo_fin):
        """Actualizar texto de POZO FIN"""
        self.pozo_fin_text = pozo_fin if pozo_fin else ""
        logger.info(f"✅ POZO FIN actualizado: '{self.pozo_fin_text}'")
    
    def update_overlay_config(self, config):
        """Actualizar configuración de visibilidad de overlays"""
        self.overlay_config.update(config)
        logger.info(f"Configuración de overlays actualizada: {self.overlay_config}")
    
    def resizeEvent(self, event):
        """Manejar redimensionamiento del widget"""
        super().resizeEvent(event)
        # Los overlays nativos se redimensionan automáticamente con el video
        logger.debug(f"Widget redimensionado a: {event.size().width()}x{event.size().height()}")
    

    
    def start_stream(self, rtsp_url):
        """Iniciar stream con pipeline optimizado y overlays nativos"""
        
        # Pipeline con nombres específicos para fácil localización
        pipeline_str = GSTREAMER_PIPELINE_TEMPLATE.format(url=rtsp_url)
        
        logger.info(f"🚀 Iniciando pipeline con overlays nativos:")
        logger.info(f"URL: {rtsp_url}")
        logger.debug(f"Pipeline: {pipeline_str}")
        
        # Resetear métricas
        self.metrics.reset()
        
        try:
            # Crear pipeline
            self.pipeline = Gst.parse_launch(pipeline_str)
            
            # === CONFIGURAR OVERLAYS NATIVOS ===
            self._configure_native_overlays()
            
            # Obtener el video sink
            videosink = self.pipeline.get_by_name("videosink")
            
            if videosink:
                # Configurar propiedades del d3d11videosink
                videosink.set_property('force-aspect-ratio', True)
                videosink.set_property('sync', False)
                
                # Intentar configurar overlay en el widget
                try:
                    if hasattr(videosink, 'set_window_handle'):
                        logger.debug("Configurando overlay D3D11 en widget PyQt6...")
                        videosink.set_window_handle(self.winId())
                    elif hasattr(videosink, 'set_xwindow_id'):
                        logger.debug("Configurando X11 overlay...")
                        videosink.set_xwindow_id(self.winId())
                    else:
                        logger.debug("Intentando configurar overlay con GstVideoOverlay...")
                        # Intentar con interfaz GstVideoOverlay
                        if GstVideo.is_video_overlay_prepare_window_handle_message(videosink):
                            videosink.set_window_handle(self.winId())
                        else:
                            logger.warning("Overlay no soportado con d3d11videosink")
                except Exception as e:
                    logger.error(f"Error configurando overlay: {e}")
            
            # Configurar bus para mensajes
            self.bus = self.pipeline.get_bus()
            self.bus.add_signal_watch()
            self.bus.connect("message", self.on_bus_message)
            
            # Agregar probe para capturar datos H.264 comprimidos
            # Intentar primero con rtph264depay (datos comprimidos)
            depay = self.pipeline.get_by_name("depay")
            if depay:
                # Probe en el pad de ENTRADA (datos H.264 comprimidos desde RTSP)  
                sinkpad = depay.get_static_pad("sink")
                if sinkpad:
                    sinkpad.add_probe(Gst.PadProbeType.BUFFER, self.on_frame_probe)
                    logger.info("Probe agregado a rtph264depay sink (H.264 comprimido)")
                else:
                    logger.error("No se pudo obtener sinkpad de rtph264depay")
            else:
                # Fallback: usar rtspsrc (puede tener pads dinámicos)
                rtspsrc = self.pipeline.get_by_name("rtspsrc")
                if rtspsrc:
                    # rtspsrc generalmente tiene pads dinámicos
                    rtspsrc.connect("pad-added", self.on_rtspsrc_pad_added)
                    logger.info("Conectado a pad-added de rtspsrc")
                else:
                    logger.error("No se encontraron elementos para agregar probe")
            
            # Iniciar reproducción
            ret = self.pipeline.set_state(Gst.State.PLAYING)
            
            if ret == Gst.StateChangeReturn.FAILURE:
                logger.error("No se pudo iniciar pipeline")
                return False
            
            logger.info("Pipeline iniciado exitosamente")
            return True
            
        except Exception as e:
            logger.error(f"Error creando pipeline: {e}")
            return False
    
    def stop_stream(self):
        """Detener stream"""
        if self.pipeline:
            self.pipeline.set_state(Gst.State.NULL)
            logger.info("Pipeline detenido")
            
        if self.bus:
            self.bus.remove_signal_watch()
    
    def on_rtspsrc_pad_added(self, element, pad):
        """Callback para cuando rtspsrc agrega pads dinámicamente"""
        pad_name = pad.get_name()
        logger.debug(f"Nuevo pad agregado: {pad_name}")
        
        # Agregar probe al nuevo pad
        pad.add_probe(Gst.PadProbeType.BUFFER, self.on_frame_probe)
        logger.info(f"Probe agregado a pad dinámico: {pad_name}")
    
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
    
    def on_bus_message(self, bus, message):
        """Manejar mensajes del bus"""
        msg_type = message.type
        
        if msg_type == Gst.MessageType.ERROR:
            error, debug = message.parse_error()
            logger.error(f"GStreamer Error: {error}")
            logger.debug(f"Debug: {debug}")
            
        elif msg_type == Gst.MessageType.EOS:
            logger.info("Fin del stream")
            
        elif msg_type == Gst.MessageType.STATE_CHANGED:
            if message.src == self.pipeline:
                old_state, new_state, pending = message.parse_state_changed()
                logger.debug(f"Estado: {old_state.value_nick} → {new_state.value_nick}")
                
        elif msg_type == Gst.MessageType.STREAM_START:
            logger.info("Stream iniciado!")
            
        elif msg_type == Gst.MessageType.ASYNC_DONE:
            logger.info("Pipeline listo!")
    
    def get_metrics(self):
        """Obtener objeto de métricas para acceso externo"""
        return self.metrics 