import sys
import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstVideo', '1.0')
from gi.repository import Gst, GLib, GstVideo

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QFrame, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPalette
import time
import threading

class StreamMetrics:
    """Monitor de métricas de streaming en tiempo real con ventanas deslizantes"""
    
    def __init__(self, window_seconds=5):
        self.window_seconds = window_seconds  # Ventana de cálculo en segundos
        self.reset()
        
    def reset(self):
        self.start_time = time.time()
        self.frame_count = 0
        self.total_bytes_received = 0  # Total acumulado (para estadística)
        
        # Ventanas deslizantes para cálculos instantáneos
        self.frame_history = []  # [(timestamp, frame_size_bytes), ...]
        self.frame_times = []    # [frame_interval, ...] para latencia
        self.last_frame_time = None
        
        # Para FPS más preciso
        self.fps_timestamps = []  # Solo timestamps para FPS
        self.last_fps_time = None
        
    def add_frame(self, frame_size_bytes=0):
        """Agregar frame con filtrado para FPS más realista"""
        current_time = time.time()
        self.frame_count += 1
        self.total_bytes_received += frame_size_bytes
        
        # Agregar frame a historial con timestamp
        self.frame_history.append((current_time, frame_size_bytes))
        
        # Limpiar frames antiguos (fuera de la ventana)
        cutoff_time = current_time - self.window_seconds
        self.frame_history = [(t, size) for t, size in self.frame_history if t >= cutoff_time]
        
        # Para FPS: Solo contar frames con intervalo mínimo realista
        # Una cámara IP típica no supera 30-60 FPS
        min_frame_interval = 1.0 / 120.0  # Máximo 120 FPS teórico
        
        if self.last_fps_time is None or (current_time - self.last_fps_time) >= min_frame_interval:
            self.fps_timestamps.append(current_time)
            self.last_fps_time = current_time
            
            # Limpiar timestamps antiguos
            self.fps_timestamps = [t for t in self.fps_timestamps if t >= cutoff_time]
        
        # Calcular intervalos entre frames para latencia
        if self.last_frame_time:
            frame_interval = current_time - self.last_frame_time
            self.frame_times.append(frame_interval)
            
            # Mantener solo últimos 30 intervalos
            if len(self.frame_times) > 30:
                self.frame_times.pop(0)
        
        self.last_frame_time = current_time
    
    def get_fps(self):
        """FPS más realista basado en timestamps filtrados"""
        if len(self.fps_timestamps) < 2:
            return 0
        
        # Contar frames válidos en la ventana actual
        current_time = time.time()
        cutoff_time = current_time - self.window_seconds
        
        valid_frames = [t for t in self.fps_timestamps if t >= cutoff_time]
        
        if len(valid_frames) < 2:
            return 0
            
        # Calcular FPS basado en el tiempo transcurrido entre primer y último frame
        time_span = valid_frames[-1] - valid_frames[0]
        if time_span > 0:
            return (len(valid_frames) - 1) / time_span
        else:
            return len(valid_frames) / self.window_seconds
    
    def get_fps_simple(self):
        """FPS simple basado en conteo de frames (método original como respaldo)"""
        if len(self.frame_history) < 2:
            return 0
        
        current_time = time.time()
        cutoff_time = current_time - self.window_seconds
        
        frames_in_window = len([t for t, _ in self.frame_history if t >= cutoff_time])
        return frames_in_window / self.window_seconds if self.window_seconds > 0 else 0
    
    def get_bitrate_kbps(self):
        """Bitrate instantáneo en Kbps basado en ventana deslizante"""
        if len(self.frame_history) < 2:
            return 0
        
        current_time = time.time()
        cutoff_time = current_time - self.window_seconds
        
        # Sumar bytes en la ventana actual
        bytes_in_window = sum(size for t, size in self.frame_history if t >= cutoff_time)
        
        if bytes_in_window > 0 and self.window_seconds > 0:
            # Convertir a bits por segundo y luego a Kbps
            bits_per_second = (bytes_in_window * 8) / self.window_seconds
            return bits_per_second / 1000  # Kbps estándar
        return 0
    
    def get_bitrate_mbps(self):
        """Bitrate instantáneo en Mbps"""
        kbps = self.get_bitrate_kbps()
        return kbps / 1000  # 1 Mbps = 1000 Kbps
    
    def get_data_rate_kbps(self):
        """Tasa de datos instantánea en KBps basada en ventana deslizante"""
        if len(self.frame_history) < 2:
            return 0
        
        current_time = time.time()
        cutoff_time = current_time - self.window_seconds
        
        # Sumar bytes en la ventana actual
        bytes_in_window = sum(size for t, size in self.frame_history if t >= cutoff_time)
        
        if bytes_in_window > 0 and self.window_seconds > 0:
            bytes_per_second = bytes_in_window / self.window_seconds
            return bytes_per_second / 1024  # KBps binario
        return 0
    
    def get_avg_frame_time_ms(self):
        """Tiempo promedio entre frames en ms"""
        if len(self.frame_times) > 0:
            avg_interval = sum(self.frame_times) / len(self.frame_times)
            return avg_interval * 1000  # Convertir a ms
        return 0
    
    def get_estimated_latency_ms(self):
        """Latencia estimada total"""
        frame_time = self.get_avg_frame_time_ms()
        network_overhead = 30  # Estimado 30ms de overhead
        return frame_time + network_overhead
    
    def get_total_mb_received(self):
        """Total acumulado en MB (desde el inicio)"""
        return self.total_bytes_received / (1024 * 1024)
    
    def get_window_info(self):
        """Información de la ventana deslizante para debug"""
        current_time = time.time()
        cutoff_time = current_time - self.window_seconds
        buffers_in_window = len([t for t, _ in self.frame_history if t >= cutoff_time])
        return {
            'window_seconds': self.window_seconds,
            'packets_in_window': buffers_in_window,
            'total_frames': self.frame_count
        }

class SimpleGStreamerWidget(QFrame):
    """Widget simple para mostrar video de GStreamer"""
    
    def __init__(self):
        super().__init__()
        self.pipeline = None
        self.bus = None
        self.metrics = StreamMetrics()
        self.setup_widget()
        
    def setup_widget(self):
        """Configurar el widget para video"""
        self.setMinimumSize(800, 600)
        self.setStyleSheet("""
            QFrame {
                background-color: black;
                border: 2px solid #4CAF50;
            }
        """)
        
        # Expandir para usar todo el espacio disponible
        from PyQt6.QtWidgets import QSizePolicy
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # Asegurar que el widget sea nativo para overlay
        self.setAttribute(Qt.WidgetAttribute.WA_NativeWindow, True)
        self.setAttribute(Qt.WidgetAttribute.WA_PaintOnScreen, True)
    
    def start_stream(self, rtsp_url):
        """Iniciar stream con pipeline simple"""
        
        # Pipeline con nombres específicos para fácil localización
        pipeline_str = f"""
        rtspsrc location={rtsp_url} protocols=tcp latency=0 name=rtspsrc
        ! rtph264depay name=depay
        ! avdec_h264 name=decoder
        ! videoconvert name=convert
        ! d3d11videosink name=videosink
        """
        
        print(f"🚀 Iniciando pipeline simple:")
        print(f"📹 URL: {rtsp_url}")
        print(f"🔧 Pipeline: {pipeline_str}")
        
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
                        print("✅ Configurando overlay D3D11 en widget PyQt6...")
                        videosink.set_window_handle(self.winId())
                    elif hasattr(videosink, 'set_xwindow_id'):
                        print("✅ Configurando X11 overlay...")
                        videosink.set_xwindow_id(self.winId())
                    else:
                        print("⚠️ Intentando configurar overlay con GstVideoOverlay...")
                        # Intentar con interfaz GstVideoOverlay
                        if GstVideo.is_video_overlay_prepare_window_handle_message(videosink):
                            videosink.set_window_handle(self.winId())
                        else:
                            print("❌ Overlay no soportado con d3d11videosink")
                except Exception as e:
                    print(f"❌ Error configurando overlay: {e}")
            
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
                    print("✅ Probe agregado a rtph264depay sink (H.264 comprimido)")
                else:
                    print("❌ No se pudo obtener sinkpad de rtph264depay")
            else:
                # Fallback: usar rtspsrc (puede tener pads dinámicos)
                rtspsrc = self.pipeline.get_by_name("rtspsrc")
                if rtspsrc:
                    # rtspsrc generalmente tiene pads dinámicos
                    rtspsrc.connect("pad-added", self.on_rtspsrc_pad_added)
                    print("✅ Conectado a pad-added de rtspsrc")
                else:
                    print("❌ No se encontraron elementos para agregar probe")
            
            # Iniciar reproducción
            ret = self.pipeline.set_state(Gst.State.PLAYING)
            
            if ret == Gst.StateChangeReturn.FAILURE:
                print("❌ Error: No se pudo iniciar pipeline")
                return False
            
            print("▶️ Pipeline iniciado")
            return True
            
        except Exception as e:
            print(f"❌ Error creando pipeline: {e}")
            return False
    
    def stop_stream(self):
        """Detener stream"""
        if self.pipeline:
            self.pipeline.set_state(Gst.State.NULL)
            print("⏹️ Pipeline detenido")
            
        if self.bus:
            self.bus.remove_signal_watch()
    
    def on_rtspsrc_pad_added(self, element, pad):
        """Callback para cuando rtspsrc agrega pads dinámicamente"""
        pad_name = pad.get_name()
        print(f"🔗 Nuevo pad agregado: {pad_name}")
        
        # Agregar probe al nuevo pad
        pad.add_probe(Gst.PadProbeType.BUFFER, self.on_frame_probe)
        print(f"✅ Probe agregado a pad dinámico: {pad_name}")
    
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
            if self.metrics.frame_count <= 5:
                print(f"🔍 Buffer #{self.metrics.frame_count}: {buffer_size} bytes")
        
        return Gst.PadProbeReturn.OK
    
    def on_bus_message(self, bus, message):
        """Manejar mensajes del bus"""
        msg_type = message.type
        
        if msg_type == Gst.MessageType.ERROR:
            error, debug = message.parse_error()
            print(f"❌ GStreamer Error: {error}")
            print(f"🔧 Debug: {debug}")
            
        elif msg_type == Gst.MessageType.EOS:
            print("🔚 Fin del stream")
            
        elif msg_type == Gst.MessageType.STATE_CHANGED:
            if message.src == self.pipeline:
                old_state, new_state, pending = message.parse_state_changed()
                print(f"🔄 Estado: {old_state.value_nick} → {new_state.value_nick}")
                
        elif msg_type == Gst.MessageType.STREAM_START:
            print("🎬 ¡Stream iniciado!")
            
        elif msg_type == Gst.MessageType.ASYNC_DONE:
            print("✅ ¡Pipeline listo!")

class SimpleStreamViewer(QMainWindow):
    """Ventana principal simple"""
    
    def __init__(self):
        super().__init__()
        self.gst_widget = None
        self.stats_timer = None
        self.setup_ui()
        
    def setup_ui(self):
        """Configurar interfaz simple"""
        self.setWindowTitle("Cámara IP - GStreamer + PyQt6 (D3D11 Overlay)")
        self.setGeometry(100, 100, 1200, 800)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # === CONTROLES ===
        controls_layout = QHBoxLayout()
        
        self.url_input = QLineEdit("rtsp://admin:Prototipo@192.168.18.5:554/Streaming/Channels/101")
        self.url_input.setPlaceholderText("URL RTSP de la cámara")
        
        self.connect_btn = QPushButton("🚀 CONECTAR")
        self.connect_btn.setStyleSheet("""
            QPushButton {
                background: #4CAF50; color: white; padding: 8px 16px;
                border-radius: 4px; font-weight: bold;
            }
            QPushButton:hover { background: #45a049; }
        """)
        self.connect_btn.clicked.connect(self.connect_stream)
        
        self.disconnect_btn = QPushButton("⏹️ DETENER")
        self.disconnect_btn.setStyleSheet("""
            QPushButton {
                background: #f44336; color: white; padding: 8px 16px;
                border-radius: 4px; font-weight: bold;
            }
            QPushButton:hover { background: #da190b; }
        """)
        self.disconnect_btn.clicked.connect(self.disconnect_stream)
        self.disconnect_btn.setEnabled(False)
        
        controls_layout.addWidget(QLabel("📹 URL:"))
        controls_layout.addWidget(self.url_input)
        controls_layout.addWidget(self.connect_btn)
        controls_layout.addWidget(self.disconnect_btn)
        
        # === ESTADÍSTICAS EN TIEMPO REAL ===
        self.stats_label = QLabel("📊 Esperando conexión...")
        self.stats_label.setStyleSheet("""
            QLabel {
                background: #2c3e50; color: #ecf0f1; padding: 8px;
                border-radius: 4px; font-family: 'Courier New', monospace;
                font-size: 11px; font-weight: bold;
            }
        """)
        self.stats_label.setMaximumHeight(40)
        
        # === ÁREA DE VIDEO (EXPANDIDA) ===
        self.gst_widget = SimpleGStreamerWidget()
        
        layout.addLayout(controls_layout)
        layout.addWidget(self.stats_label)
        layout.addWidget(self.gst_widget)
    
    def connect_stream(self):
        """Conectar al stream"""
        url = self.url_input.text().strip()
        
        if not url:
            QMessageBox.warning(self, "Error", "Por favor ingresa una URL RTSP")
            return
        
        print(f"🚀 Conectando a: {url}")
        
        if self.gst_widget.start_stream(url):
            self.connect_btn.setEnabled(False)
            self.disconnect_btn.setEnabled(True)
            self.start_stats_monitoring()
            print("✅ Conexión iniciada")
        else:
            QMessageBox.critical(self, "Error", "No se pudo iniciar el stream")
    
    def disconnect_stream(self):
        """Desconectar stream"""
        self.gst_widget.stop_stream()
        self.stop_stats_monitoring()
        self.connect_btn.setEnabled(True)
        self.disconnect_btn.setEnabled(False)
        if hasattr(self, 'stats_label'):
            self.stats_label.setText("📊 Desconectado")
        print("✅ Desconectado")
    
    def start_stats_monitoring(self):
        """Iniciar monitoreo de estadísticas en tiempo real"""
        self.stats_timer = QTimer()
        self.stats_timer.timeout.connect(self.update_stats)
        self.stats_timer.start(1000)  # Actualizar cada segundo
    
    def stop_stats_monitoring(self):
        """Detener monitoreo de estadísticas"""
        if self.stats_timer:
            self.stats_timer.stop()
            self.stats_timer = None
    
    def update_stats(self):
        """Actualizar estadísticas en tiempo real"""
        if not self.gst_widget or not self.gst_widget.metrics or not hasattr(self, 'stats_label'):
            return
        
        metrics = self.gst_widget.metrics
        
        # Obtener métricas
        fps = metrics.get_fps()  # Método filtrado
        bitrate_kbps = metrics.get_bitrate_kbps()
        bitrate_mbps = metrics.get_bitrate_mbps()
        data_rate_kbps = metrics.get_data_rate_kbps()
        latency = metrics.get_estimated_latency_ms()
        frames = metrics.frame_count
        data_mb = metrics.get_total_mb_received()
        frame_time = metrics.get_avg_frame_time_ms()
        
        # Formatear estadísticas con valores instantáneos (últimos 5 segundos)
        if bitrate_mbps >= 1.0:
            bitrate_display = f"{bitrate_mbps:.2f} Mbps"
        else:
            bitrate_display = f"{bitrate_kbps:.0f} Kbps"
        
        # Obtener info de ventana para debug
        window_info = metrics.get_window_info()
        
        stats_text = (
            f"📊 FPS: {fps:.1f} | "
            f"📡 {bitrate_display} | "
            f"💾 {data_rate_kbps:.0f} KBps | "
            f"⚡ ~{latency:.0f}ms | "
            f"🎬 {frames} frames | "
            f"📦 {data_mb:.1f} MB | "
            f"🔄 {window_info['packets_in_window']}buf/5s"
        )
        
        # Color según latencia
        if latency < 100:
            color = "#27ae60"  # Verde - Excelente
        elif latency < 200:
            color = "#f39c12"  # Naranja - Bueno  
        else:
            color = "#e74c3c"  # Rojo - Mejorable
        
        # Actualizar estilo con color dinámico
        self.stats_label.setStyleSheet(f"""
            QLabel {{
                background: #2c3e50; color: {color}; padding: 8px;
                border-radius: 4px; font-family: 'Courier New', monospace;
                font-size: 11px; font-weight: bold;
            }}
        """)
        
        self.stats_label.setText(stats_text)
    
    def closeEvent(self, event):
        """Manejar cierre de aplicación"""
        if self.gst_widget:
            self.gst_widget.stop_stream()
        self.stop_stats_monitoring()
        event.accept()

def main():
    """Función principal"""
    
    # Inicializar GStreamer
    Gst.init(None)
    
    # Crear aplicación PyQt6
    app = QApplication(sys.argv)
    
    print("🚀 Visor GStreamer + PyQt6 con Métricas en Tiempo Real")
    print("📺 D3D11 Hardware Accelerated + Estadísticas Avanzadas")
    print("📊 Métricas INSTANTÁNEAS (ventana deslizante de 5 segundos)")
    print("📡 Bitrate/Datos: Valores actuales, NO acumulativos")
    print("=" * 60)
    
    # Crear ventana
    window = SimpleStreamViewer()
    window.show()
    
    # Ejecutar aplicación
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 