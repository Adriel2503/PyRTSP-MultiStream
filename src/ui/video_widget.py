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
    CAIRO_OVERLAY_CONFIG,
    TIMEOVERLAY_CONFIG,
    TEXTOVERLAY_DESDE_CONFIG,
    TEXTOVERLAY_HASTA_CONFIG
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
        self.cairo_datetime = None
        self.textoverlay_desde = None
        self.textoverlay_hasta = None
        
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
            # === CAIRO OVERLAY - Fecha y hora con fondo naranja transparente ===
            self.cairo_datetime = self.pipeline.get_by_name("cairo_datetime")
            if self.cairo_datetime and CAIRO_AVAILABLE:
                # Conectar callback para dibujar la fecha/hora
                self.cairo_datetime.connect("draw", self._on_cairo_draw)
                logger.info("✅ Cairo overlay configurado - fecha/hora con fondo naranja")
            elif self.cairo_datetime:
                logger.warning("⚠️ Cairo no disponible, usando textoverlay simple")
                # Fallback a textoverlay simple si Cairo no está disponible
                # (implementar fallback si es necesario)
            else:
                logger.error("❌ No se encontró cairo_datetime en el pipeline")
            
            # === TEXTOVERLAY DESDE - Pozo desde (inferior izquierda) ===
            self.textoverlay_desde = self.pipeline.get_by_name("textoverlay_desde")
            if self.textoverlay_desde:
                for prop, value in TEXTOVERLAY_DESDE_CONFIG.items():
                    prop_name = prop.replace('_', '-')
                    try:
                        self.textoverlay_desde.set_property(prop_name, value)
                        logger.debug(f"📍 Overlay DESDE: {prop_name} = {value}")
                    except Exception as e:
                        logger.warning(f"No se pudo configurar DESDE {prop_name}: {e}")
                logger.info("✅ Overlay POZO DESDE configurado")
            
            # === TEXTOVERLAY HASTA - Pozo hasta (inferior derecha) ===
            self.textoverlay_hasta = self.pipeline.get_by_name("textoverlay_hasta")
            if self.textoverlay_hasta:
                for prop, value in TEXTOVERLAY_HASTA_CONFIG.items():
                    prop_name = prop.replace('_', '-')
                    try:
                        self.textoverlay_hasta.set_property(prop_name, value)
                        logger.debug(f"📍 Overlay HASTA: {prop_name} = {value}")
                    except Exception as e:
                        logger.warning(f"No se pudo configurar HASTA {prop_name}: {e}")
                logger.info("✅ Overlay POZO HASTA configurado")
                
        except Exception as e:
            logger.error(f"❌ Error configurando overlays nativos: {e}")
    
    def _on_cairo_draw(self, element, context, timestamp, duration, user_data=None):
        """Callback para dibujar fecha/hora con fondo naranja transparente usando Cairo"""
        if not CAIRO_AVAILABLE:
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
            
            # Calcular posición (más a la derecha y más abajo)
            padding = config['padding']
            x = padding + 80  # Desplazar 80 píxeles más a la derecha
            y = padding + text_height + 40  # Desplazar 40 píxeles más abajo
            
            # Dimensiones del fondo
            bg_width = text_width + (padding * 2)
            bg_height = text_height + (padding * 1.5)
            
            # === DIBUJAR FONDO NARANJA TRANSPARENTE ===
            bg_color = config['bg_color']
            context.set_source_rgba(bg_color[0], bg_color[1], bg_color[2], bg_color[3])
            
            # Rectángulo con esquinas redondeadas
            radius = config['border_radius']
            context.new_path()
            context.arc(x - padding + radius, y - text_height - padding/2 + radius, radius, 3.14159, 3*3.14159/2)
            context.arc(x - padding + bg_width - radius, y - text_height - padding/2 + radius, radius, 3*3.14159/2, 0)
            context.arc(x - padding + bg_width - radius, y - padding/2 + text_height - radius, radius, 0, 3.14159/2)
            context.arc(x - padding + radius, y - padding/2 + text_height - radius, radius, 3.14159/2, 3.14159)
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
    
    def resizeEvent(self, event):
        """Manejar redimensionamiento del widget"""
        super().resizeEvent(event)
        # Los overlays nativos se redimensionan automáticamente con el video
        logger.debug(f"Widget redimensionado a: {event.size().width()}x{event.size().height()}")
    
    def update_pozo_overlays(self, pozo_desde, pozo_hasta):
        """Actualizar texto de los overlays nativos de pozos"""
        try:
            # Actualizar POZO DESDE (overlay nativo)
            if self.textoverlay_desde:
                if pozo_desde:
                    texto_desde = f"DESDE: {pozo_desde}"
                    self.textoverlay_desde.set_property('text', texto_desde)
                    logger.debug(f"📍 Overlay DESDE actualizado: {texto_desde}")
                else:
                    self.textoverlay_desde.set_property('text', '')
                    logger.debug("📍 Overlay DESDE ocultado")
            
            # Actualizar POZO HASTA (overlay nativo)
            if self.textoverlay_hasta:
                if pozo_hasta:
                    texto_hasta = f"HASTA: {pozo_hasta}"
                    self.textoverlay_hasta.set_property('text', texto_hasta)
                    logger.debug(f"📍 Overlay HASTA actualizado: {texto_hasta}")
                else:
                    self.textoverlay_hasta.set_property('text', '')
                    logger.debug("📍 Overlay HASTA ocultado")
            
            logger.info(f"✅ Overlays nativos actualizados: DESDE={pozo_desde}, HASTA={pozo_hasta}")
            
        except Exception as e:
            logger.error(f"❌ Error actualizando overlays nativos: {e}")
    
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