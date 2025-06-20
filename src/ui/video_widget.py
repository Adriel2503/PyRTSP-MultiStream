# -*- coding: utf-8 -*-
"""
Widget de video para streaming GStreamer
Extrae la funcionalidad de SimpleGStreamerWidget del código original
"""

import sys
import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstVideo', '1.0')
from gi.repository import Gst, GLib, GstVideo

from PyQt6.QtWidgets import QFrame, QSizePolicy
from PyQt6.QtCore import Qt

from ..utils.constants import (
    GSTREAMER_PIPELINE_TEMPLATE,
    VIDEO_WIDGET_STYLE,
    DEFAULT_VIDEO_SIZE,
    DEBUG_SHOW_FIRST_BUFFERS,
    DEBUG_BUFFER_INFO
)
from ..utils.logger import setup_logger
from ..metrics.stream_metrics import StreamMetrics

logger = setup_logger("VideoWidget")

class VideoWidget(QFrame):
    """Widget optimizado para mostrar video de GStreamer con métricas integradas"""
    
    def __init__(self):
        super().__init__()
        self.pipeline = None
        self.bus = None
        self.metrics = StreamMetrics()
        self.setup_widget()
        logger.info("VideoWidget inicializado")
        
    def setup_widget(self):
        """Configurar el widget para video"""
        self.setMinimumSize(*DEFAULT_VIDEO_SIZE)
        self.setStyleSheet(VIDEO_WIDGET_STYLE)
        
        # Expandir para usar todo el espacio disponible
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # Asegurar que el widget sea nativo para overlay
        self.setAttribute(Qt.WidgetAttribute.WA_NativeWindow, True)
        self.setAttribute(Qt.WidgetAttribute.WA_PaintOnScreen, True)
        
        logger.debug("Widget configurado para overlay nativo")
    
    def start_stream(self, rtsp_url):
        """Iniciar stream con pipeline optimizado"""
        
        # Pipeline con nombres específicos para fácil localización
        pipeline_str = GSTREAMER_PIPELINE_TEMPLATE.format(url=rtsp_url)
        
        logger.info(f"Iniciando pipeline:")
        logger.info(f"URL: {rtsp_url}")
        logger.debug(f"Pipeline: {pipeline_str}")
        
        # Resetear métricas
        self.metrics.reset()
        
        try:
            # Crear pipeline
            self.pipeline = Gst.parse_launch(pipeline_str)
            
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