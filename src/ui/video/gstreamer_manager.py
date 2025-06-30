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
from .pyav_recorder import PyAVRecorder
from .gpu_recorder import GPURecorder

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
        
        # Inicializar recorders
        self.pyav_recorder = PyAVRecorder()
        self.gpu_recorder = GPURecorder()
        self.recording_sink = None  # appsink para PyAV
        
        # Cache para capturas de pantalla
        self.latest_frame_cache = None  # (frame_data, width, height, timestamp)
        
        # Seleccionar recorder por defecto - FORZAR CPU por confiabilidad
        self.use_gpu_recorder = False  # Forzar CPU por defecto
        logger.info("🎮 Usando recorder: CPU (PyAV) - Configuración por defecto para máxima confiabilidad")
        logger.info("💡 GPU recording disponible pero deshabilitado por defecto")
        
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
            
            # Configurar appsink para PyAV
            self._configure_recording_sink()
            
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

    def _configure_recording_sink(self):
        """Configurar appsink para PyAV y capturas"""
        self.recording_sink = self.pipeline.get_by_name("recording_sink")
        if self.recording_sink:
            # Configurar appsink para grabación Y capturas ocasionales
            self.recording_sink.set_property('emit-signals', True)
            self.recording_sink.set_property('sync', False)
            self.recording_sink.set_property('drop', False)  # No descartar frames para capturas
            self.recording_sink.set_property('max-buffers', 5)  # Más buffers para capturas
            
            # Conectar callback para nuevos frames
            self.recording_sink.connect('new-sample', self._on_new_frame)
            
            logger.info("✅ appsink para PyAV configurado")
        else:
            logger.error("No se pudo obtener recording_sink del pipeline")
    
    def _on_new_frame(self, sink):
        """Callback para nuevos frames del appsink"""
        try:
            # Obtener sample del appsink
            sample = sink.emit('pull-sample')
            if not sample:
                return Gst.FlowReturn.ERROR
            
            # Obtener buffer y caps
            buffer = sample.get_buffer()
            caps = sample.get_caps()
            
            # Extraer información del frame
            structure = caps.get_structure(0)
            width = structure.get_int('width')[1]
            height = structure.get_int('height')[1]
            
            # Mapear buffer para leer datos
            success, map_info = buffer.map(Gst.MapFlags.READ)
            if not success:
                return Gst.FlowReturn.ERROR
            
            # Enviar frame al recorder activo
            frame_data = map_info.data
            if self.use_gpu_recorder:
                self.gpu_recorder.add_frame(frame_data, width, height)
            else:
                self.pyav_recorder.add_frame(frame_data, width, height)
            
            # CACHE para capturas: Guardar copia del último frame
            import time
            frame_copy = bytes(frame_data)  # Crear copia independiente
            self.latest_frame_cache = (frame_copy, width, height, time.time())
            
            # Limpiar
            buffer.unmap(map_info)
            
            return Gst.FlowReturn.OK
            
        except Exception as e:
            logger.error(f"❌ Error procesando frame: {e}")
            return Gst.FlowReturn.ERROR
    
    def _check_gpu_support(self):
        """Verificar soporte para grabación GPU"""
        try:
            # Verificar si el encoder seleccionado es de GPU
            encoder_info = self.gpu_recorder.get_encoder_info()
            is_gpu_encoder = encoder_info['is_gpu']
            
            logger.info(f"🔍 Encoder detectado: {encoder_info['encoder']} ({'GPU' if is_gpu_encoder else 'CPU'})")
            return is_gpu_encoder
        except Exception as e:
            logger.warning(f"⚠️ Error verificando soporte GPU: {e}")
            return False
    
    def set_recorder_type(self, use_gpu=None):
        """Cambiar tipo de recorder"""
        if use_gpu is None:
            use_gpu = self._check_gpu_support()
        
        self.use_gpu_recorder = use_gpu
        
        if use_gpu:
            encoder_info = self.gpu_recorder.get_encoder_info()
            recorder_type = f"GPU (FFmpeg+{encoder_info['encoder']})"
            logger.info(f"🔄 Cambiando a recorder: {recorder_type}")
            logger.warning("⚠️ GPU recording habilitado manualmente - monitorear estabilidad")
        else:
            logger.info("🔄 Cambiando a recorder: CPU (PyAV)")
            logger.info("✅ CPU recording - máxima confiabilidad garantizada")
    
    def enable_gpu_recording(self):
        """Habilitar GPU recording manualmente (para pruebas)"""
        logger.info("🧪 Habilitando GPU recording para pruebas...")
        gpu_available = self._check_gpu_support()
        
        if gpu_available:
            self.use_gpu_recorder = True
            encoder_info = self.gpu_recorder.get_encoder_info()
            logger.info(f"✅ GPU recording habilitado: {encoder_info['encoder']}")
            logger.warning("⚠️ Monitorear archivos de video por posible corrupción")
            return True
        else:
            logger.error("❌ No hay encoders GPU funcionales disponibles")
            return False
    
    def disable_gpu_recording(self):
        """Deshabilitar GPU recording y volver a CPU"""
        logger.info("🔄 Deshabilitando GPU recording...")
        self.use_gpu_recorder = False
        logger.info("✅ Volviendo a CPU recording - máxima confiabilidad")
    
    def start_recording(self, filename):
        """Iniciar grabación con el recorder seleccionado"""
        if self.use_gpu_recorder:
            encoder_info = self.gpu_recorder.get_encoder_info()
            logger.info(f"🎮 Iniciando grabación con GPU (FFmpeg+{encoder_info['encoder']})")
            return self.gpu_recorder.start_recording(filename)
        else:
            logger.info("💻 Iniciando grabación con CPU (PyAV)")
            return self.pyav_recorder.start_recording(filename)
    
    def stop_recording(self):
        """Detener grabación"""
        if self.use_gpu_recorder:
            return self.gpu_recorder.stop_recording()
        else:
            return self.pyav_recorder.stop_recording()
    
    def is_recording(self):
        """Verificar si está grabando"""
        if self.use_gpu_recorder:
            return self.gpu_recorder.is_recording
        else:
            return self.pyav_recorder.is_recording
    
    def get_recorder_status(self):
        """Obtener información completa del recorder actual"""
        if self.use_gpu_recorder:
            encoder_info = self.gpu_recorder.get_encoder_info()
            return {
                'type': 'GPU',
                'recorder': 'FFmpeg',
                'encoder': encoder_info['encoder'],
                'is_gpu': encoder_info['is_gpu'],
                'bitrate': encoder_info['bitrate'],
                'resolution': encoder_info['resolution'],
                'fps': encoder_info['fps'],
                'status': 'Experimental - Monitorear estabilidad'
            }
        else:
            return {
                'type': 'CPU',
                'recorder': 'PyAV',
                'encoder': 'libx264',
                'is_gpu': False,
                'bitrate': '2M',  # Default PyAV bitrate
                'resolution': 'Auto',
                'fps': 'Auto',
                'status': 'Confiable - Producción'
            }

    def get_latest_frame_for_capture(self):
        """Captura INSTANTÁNEA desde cache - Sin competencia con grabación"""
        try:
            # Verificar si hay frame en cache
            if not self.latest_frame_cache:
                logger.warning("⚠️ No hay frames en cache para captura")
                return None
            
            frame_data, width, height, timestamp = self.latest_frame_cache
            
            # Verificar que el frame no sea muy antiguo (máximo 5 segundos)
            import time
            age = time.time() - timestamp
            if age > 5.0:
                logger.warning(f"⚠️ Frame en cache muy antiguo ({age:.1f}s) - puede estar desactualizado")
                # Pero lo usamos de todas formas
            
            logger.info(f"✅ Frame capturado desde cache: {width}x{height}, {len(frame_data)} bytes (edad: {age:.2f}s)")
            
            # Retornar copia del frame cacheado
            return (frame_data, width, height)
            
        except Exception as e:
            logger.error(f"❌ Error capturando frame desde cache: {e}")
            return None
    
