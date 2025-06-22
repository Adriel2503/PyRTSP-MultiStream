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

from PyQt6.QtWidgets import QFrame, QSizePolicy, QPushButton, QLabel
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

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
    
    # Señal emitida cuando se hace clic en el botón "+"
    plus_button_clicked = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.pipeline = None
        self.bus = None
        self.metrics = StreamMetrics()
        self.setup_widget()
        self.create_floating_button()
        self.create_overlay_labels()
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
    
    def create_floating_button(self):
        """Crear botón flotante circular con símbolo '+' en esquina superior derecha"""
        self.plus_button = QPushButton("+", self)
        
        # Configurar tamaño y posición inicial
        button_size = 50
        self.plus_button.setFixedSize(button_size, button_size)
        
        # Estilo circular moderno
        self.plus_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 183, 77, 200), 
                    stop:1 rgba(255, 167, 38, 200));
                color: white;
                border: 3px solid rgba(255, 255, 255, 100);
                border-radius: 25px;
                font-size: 24px;
                font-weight: bold;
                font-family: Arial, sans-serif;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 167, 38, 230), 
                    stop:1 rgba(255, 152, 0, 230));
                border: 3px solid rgba(255, 255, 255, 150);
                transform: scale(1.05);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 152, 0, 200), 
                    stop:1 rgba(245, 124, 0, 200));
                border: 3px solid rgba(255, 255, 255, 200);
            }
        """)
        
        # Conectar señal
        self.plus_button.clicked.connect(self.plus_button_clicked.emit)
        
        # Posicionar en esquina superior derecha
        self.position_floating_button()
        
        # Asegurar que esté encima del video
        self.plus_button.raise_()
        
        logger.debug("Botón flotante '+' creado en esquina superior derecha")
    
    def position_floating_button(self):
        """Posicionar botón flotante en esquina superior derecha"""
        if hasattr(self, 'plus_button'):
            margin = 15  # Margen desde el borde
            button_size = self.plus_button.width()
            
            # Calcular posición
            x = self.width() - button_size - margin
            y = margin
            
            self.plus_button.move(x, y)
    
    def resizeEvent(self, event):
        """Reposicionar botón flotante cuando el widget se redimensiona"""
        super().resizeEvent(event)
        if hasattr(self, 'plus_button'):
            self.position_floating_button()
        if hasattr(self, 'pozo_desde_label') and hasattr(self, 'pozo_hasta_label'):
            self.position_overlay_labels()
    
    def create_overlay_labels(self):
        """Crear labels de overlay para mostrar POZO DESDE y POZO HASTA"""
        # Label para POZO DESDE (izquierda)
        self.pozo_desde_label = QLabel("", self)
        self.pozo_desde_label.setObjectName("pozoDesdeLabel")
        self.pozo_desde_label.setVisible(False)  # Oculto inicialmente
        
        # Label para POZO HASTA (derecha)
        self.pozo_hasta_label = QLabel("", self)
        self.pozo_hasta_label.setObjectName("pozoHastaLabel")
        self.pozo_hasta_label.setVisible(False)  # Oculto inicialmente
        
        # Estilo para ambos labels - más visible
        overlay_style = """
            QLabel {
                background: rgba(255, 167, 38, 200);
                color: white;
                border: 3px solid white;
                border-radius: 10px;
                padding: 10px 15px;
                font-size: 16px;
                font-weight: bold;
                font-family: Arial, sans-serif;
            }
        """
        
        self.pozo_desde_label.setStyleSheet(overlay_style)
        self.pozo_hasta_label.setStyleSheet(overlay_style)
        
        # Posicionar labels
        self.position_overlay_labels()
        
        # Asegurar que estén encima del video
        self.pozo_desde_label.raise_()
        self.pozo_hasta_label.raise_()
        
        logger.debug("Labels de overlay creados")
    
    def position_overlay_labels(self):
        """Posicionar labels de overlay en el video"""
        if hasattr(self, 'pozo_desde_label') and hasattr(self, 'pozo_hasta_label'):
            margin = 20
            
            # POZO DESDE - Esquina inferior izquierda
            self.pozo_desde_label.adjustSize()
            x_desde = margin
            y_desde = self.height() - self.pozo_desde_label.height() - margin
            self.pozo_desde_label.move(x_desde, y_desde)
            
            # POZO HASTA - Esquina inferior derecha
            self.pozo_hasta_label.adjustSize()
            x_hasta = self.width() - self.pozo_hasta_label.width() - margin
            y_hasta = self.height() - self.pozo_hasta_label.height() - margin
            self.pozo_hasta_label.move(x_hasta, y_hasta)
    
    def update_pozo_overlays(self, pozo_desde, pozo_hasta):
        """Actualizar texto de los overlays de pozos"""
        if hasattr(self, 'pozo_desde_label') and hasattr(self, 'pozo_hasta_label'):
            # Actualizar POZO DESDE
            if pozo_desde:
                self.pozo_desde_label.setText(f"DESDE: {pozo_desde}")
                self.pozo_desde_label.setVisible(True)
            else:
                self.pozo_desde_label.setVisible(False)
            
            # Actualizar POZO HASTA
            if pozo_hasta:
                self.pozo_hasta_label.setText(f"HASTA: {pozo_hasta}")
                self.pozo_hasta_label.setVisible(True)
            else:
                self.pozo_hasta_label.setVisible(False)
            
            # Reposicionar después de cambiar texto
            self.position_overlay_labels()
            
            logger.info(f"Overlays actualizados: DESDE={pozo_desde}, HASTA={pozo_hasta}")
    
    def start_stream(self, rtsp_url):
        """Iniciar stream con pipeline optimizado"""
        
        # Asegurar que los overlays estén siempre encima cuando inicia el stream
        if hasattr(self, 'pozo_desde_label') and hasattr(self, 'pozo_hasta_label'):
            self.pozo_desde_label.raise_()
            self.pozo_hasta_label.raise_()
        if hasattr(self, 'plus_button'):
            self.plus_button.raise_()
        
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