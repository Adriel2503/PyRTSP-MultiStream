# -*- coding: utf-8 -*-
"""
Manager de GStreamer para pipeline, bus y configuración
Separado del widget principal para responsabilidad única
"""

import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstVideo', '1.0')
from gi.repository import Gst, GLib, GstVideo

from ...utils.constants import GSTREAMER_PIPELINE_TEMPLATE
from ...utils.logger import setup_logger

logger = setup_logger("GStreamerManager")

class GStreamerManager:
    """Manager especializado en GStreamer pipeline y bus"""
    
    def __init__(self, video_widget):
        self.video_widget = video_widget
        self.pipeline = None
        self.bus = None
        
        # Conectar con overlay_manager y metrics_integration
        self.overlay_manager = None
        self.metrics_integration = None
        
    def set_managers(self, overlay_manager, metrics_integration):
        """Conectar con otros managers"""
        self.overlay_manager = overlay_manager
        self.metrics_integration = metrics_integration
    
    def add_probe_to_element(self, element, pad_name):
        pad = element.get_static_pad(pad_name)
        if pad:
            pad.add_probe(Gst.PadProbeType.BUFFER, self.probe_callback)

    def probe_callback(self, pad, info):
        logger.info(f"Datos procesados en {pad.get_parent_element().get_name()}")
        return Gst.PadProbeReturn.OK

    def setup_recording_probes(self, pipeline):
        elements = ['queue', 'videoconvert', 'x264enc', 'mp4mux', 'filesink']
        for element_name in elements:
            element = pipeline.get_by_name(element_name)
            if element:
                self.add_probe_to_element(element, "src")

    def start_stream(self, rtsp_url):
        """Iniciar stream con pipeline optimizado"""
        pipeline_str = GSTREAMER_PIPELINE_TEMPLATE.format(url=rtsp_url)
        
        logger.info(f"🚀 Iniciando pipeline GStreamer:")
        logger.info(f"URL: {rtsp_url}")
        logger.debug(f"Pipeline: {pipeline_str}")
        
        # Resetear métricas si están disponibles
        if self.metrics_integration:
            self.metrics_integration.reset()
        
        try:
            # Crear pipeline
            self.pipeline = Gst.parse_launch(pipeline_str)
            
            # Configurar overlays nativos
            self._configure_native_overlays()
            
            # Configurar video sink
            self._configure_video_sink()
            
            # Configurar bus para mensajes
            self._configure_bus()
            
            # Configurar probes para métricas
            self._configure_metrics_probes()
            
            # Configurar probes para grabación
            self.setup_recording_probes(self.pipeline)
            
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
    
    def _configure_native_overlays(self):
        """Configurar overlays nativos de GStreamer"""
        if not self.overlay_manager:
            logger.warning("OverlayManager no disponible para configurar overlays")
            return
            
        try:
            # Obtener referencias a overlays del pipeline
            overlays = {
                'cairo_grid': self.pipeline.get_by_name("cairo_grid"),
                'cairo_datetime': self.pipeline.get_by_name("cairo_datetime"),
                'cairo_ref_tramo': self.pipeline.get_by_name("cairo_ref_tramo"),
                'cairo_pozo_inicio': self.pipeline.get_by_name("cairo_pozo_inicio"),
                'cairo_distancia': self.pipeline.get_by_name("cairo_distancia"),
                'cairo_pozo_fin': self.pipeline.get_by_name("cairo_pozo_fin"),
                'cairo_annotation': self.pipeline.get_by_name("cairo_annotation")
            }
            
            # Configurar overlays en el manager
            self.overlay_manager.configure_pipeline_overlays(overlays)
            
            logger.info("✅ Overlays nativos configurados")
            
        except Exception as e:
            logger.error(f"❌ Error configurando overlays nativos: {e}")
    
    def _configure_video_sink(self):
        """Configurar el video sink"""
        videosink = self.pipeline.get_by_name("videosink")
        
        if videosink:
            # Configurar propiedades del d3d11videosink
            videosink.set_property('force-aspect-ratio', True)
            videosink.set_property('sync', False)
            
            # Configurar overlay en el widget
            self._configure_video_overlay(videosink)
        else:
            logger.error("No se pudo obtener videosink del pipeline")
    
    def _configure_video_overlay(self, videosink):
        """Configurar overlay de video en el widget"""
        try:
            if hasattr(videosink, 'set_window_handle'):
                logger.debug("Configurando overlay D3D11 en widget PyQt6...")
                videosink.set_window_handle(self.video_widget.winId())
            elif hasattr(videosink, 'set_xwindow_id'):
                logger.debug("Configurando X11 overlay...")
                videosink.set_xwindow_id(self.video_widget.winId())
            else:
                logger.debug("Intentando configurar overlay con GstVideoOverlay...")
                if GstVideo.is_video_overlay_prepare_window_handle_message(videosink):
                    videosink.set_window_handle(self.video_widget.winId())
                else:
                    logger.warning("Overlay no soportado con d3d11videosink")
        except Exception as e:
            logger.error(f"Error configurando overlay: {e}")
    
    def _configure_bus(self):
        """Configurar bus para mensajes"""
        self.bus = self.pipeline.get_bus()
        self.bus.add_signal_watch()
        self.bus.connect("message", self.on_bus_message)
    
    def _configure_metrics_probes(self):
        """Configurar probes para métricas"""
        if not self.metrics_integration:
            logger.warning("MetricsIntegration no disponible")
            return
            
        # Agregar probe para capturar datos H.264 comprimidos
        depay = self.pipeline.get_by_name("depay")
        if depay:
            sinkpad = depay.get_static_pad("sink")
            if sinkpad:
                sinkpad.add_probe(Gst.PadProbeType.BUFFER, self.metrics_integration.on_frame_probe)
                logger.info("Probe agregado a rtph264depay sink (H.264 comprimido)")
            else:
                logger.error("No se pudo obtener sinkpad de rtph264depay")
        else:
            # Fallback: usar rtspsrc
            rtspsrc = self.pipeline.get_by_name("rtspsrc")
            if rtspsrc:
                rtspsrc.connect("pad-added", self._on_rtspsrc_pad_added)
                logger.info("Conectado a pad-added de rtspsrc")
            else:
                logger.error("No se encontraron elementos para agregar probe")
    
    def _on_rtspsrc_pad_added(self, element, pad):
        """Callback para cuando rtspsrc agrega pads dinámicamente"""
        if not self.metrics_integration:
            return
            
        pad_name = pad.get_name()
        logger.debug(f"Nuevo pad agregado: {pad_name}")
        
        # Agregar probe al nuevo pad
        pad.add_probe(Gst.PadProbeType.BUFFER, self.metrics_integration.on_frame_probe)
        logger.info(f"Probe agregado a pad dinámico: {pad_name}")
    
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