# -*- coding: utf-8 -*-
"""
Visor de Cámara IP con GStreamer - Ultra Baja Latencia
Implementación profesional para latencia <100ms
"""

import sys
import os
import time
import threading
from datetime import datetime

# GStreamer imports
import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstVideo', '1.0')
gi.require_version('Gtk', '3.0')
gi.require_version('GdkPixbuf', '2.0')

from gi.repository import Gst, GObject, Gtk, GdkPixbuf, GLib, GstVideo
from gi.repository import Gdk

# PyQt6 para interfaz (opcional - puedes usar GTK puro)
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QFrame, QTextEdit, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QImage, QPixmap
import numpy as np

class GStreamerLatencyMonitor:
    """Monitor específico para latencia de GStreamer"""
    
    def __init__(self):
        self.frame_times = []
        self.start_time = time.time()
        
    def add_frame(self):
        current_time = time.time()
        self.frame_times.append(current_time)
        
        # Mantener solo los últimos 30 frames
        if len(self.frame_times) > 30:
            self.frame_times.pop(0)
    
    def get_fps(self):
        if len(self.frame_times) < 2:
            return 0
        
        time_diff = self.frame_times[-1] - self.frame_times[0]
        return len(self.frame_times) / time_diff if time_diff > 0 else 0
    
    def get_avg_frame_time_ms(self):
        if len(self.frame_times) < 2:
            return 0
        
        intervals = []
        for i in range(1, len(self.frame_times)):
            intervals.append(self.frame_times[i] - self.frame_times[i-1])
        
        avg_interval = sum(intervals) / len(intervals)
        return avg_interval * 1000  # Convertir a millisegundos

class UltraLowLatencyGStreamerPipeline:
    """Pipeline GStreamer optimizado para ultra baja latencia"""
    
    def __init__(self):
        # Inicializar GStreamer
        Gst.init(None)
        
        self.pipeline = None
        self.bus = None
        self.sink = None
        self.latency_monitor = GStreamerLatencyMonitor()
        self.is_playing = False
        
        # Callbacks
        self.on_frame_callback = None
        self.on_error_callback = None
        self.on_eos_callback = None
        
    def create_ultra_low_latency_pipeline(self, rtsp_url):
        """
        Crear pipeline GStreamer optimizado para latencia mínima
        """
        
        # ✅ PIPELINE ULTRA OPTIMIZADO CON APPSINK PARA PYQT6
        pipeline_str = f"""
        rtspsrc location={rtsp_url} 
            protocols=tcp 
            latency=0 
            buffer-mode=auto 
            drop-on-latency=true
        ! queue max-size-buffers=1 max-size-time=0 max-size-bytes=0 leaky=downstream
        ! rtph264depay
        ! queue max-size-buffers=1 max-size-time=0 max-size-bytes=0 leaky=downstream
        ! avdec_h264 
            max-threads=4 
            output-corrupt=false
        ! queue max-size-buffers=1 max-size-time=0 max-size-bytes=0 leaky=downstream
        ! videoconvert
        ! video/x-raw,format=RGB
        ! queue max-size-buffers=1 max-size-time=0 max-size-bytes=0 leaky=downstream
        ! appsink name=sink emit-signals=true max-buffers=1 drop=true sync=false
        """
        
        print(f"🚀 Creando pipeline GStreamer ultra optimizado:")
        print(f"📊 URL: {rtsp_url}")
        print(f"⚡ Configuración: TCP, sin sync, buffers mínimos")
        
        try:
            self.pipeline = Gst.parse_launch(pipeline_str)
            
            # Configurar bus para mensajes
            self.bus = self.pipeline.get_bus()
            self.bus.add_signal_watch()
            self.bus.connect("message", self.on_bus_message)
            
            # Configurar appsink para recibir frames
            self.sink = self.pipeline.get_by_name("sink")
            if self.sink:
                print("✅ AppSink encontrado, conectando callback...")
                
                # Configurar propiedades del appsink
                self.sink.set_property("emit-signals", True)
                self.sink.set_property("max-buffers", 1)
                self.sink.set_property("drop", True)
                self.sink.set_property("sync", False)
                
                self.sink.connect("new-sample", self.on_new_sample)
                print("✅ AppSink configurado completamente")
            else:
                print("❌ Error: No se encontró el appsink 'sink'")
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ Error creando pipeline: {e}")
            return False
    
    def create_recording_pipeline(self, rtsp_url, output_file):
        """
        Pipeline para grabación directa con latencia mínima
        """
        
        pipeline_str = f"""
        rtspsrc location={rtsp_url} 
            protocols=tcp 
            latency=0 
            buffer-mode=auto
        ! queue max-size-buffers=1 leaky=downstream
        ! rtph264depay
        ! queue max-size-buffers=1 leaky=downstream
        ! h264parse
        ! queue max-size-buffers=1 leaky=downstream
        ! mp4mux
        ! filesink location={output_file}
        """
        
        try:
            self.pipeline = Gst.parse_launch(pipeline_str)
            self.bus = self.pipeline.get_bus()
            self.bus.add_signal_watch()
            self.bus.connect("message", self.on_bus_message)
            
            print(f"🎬 Pipeline de grabación creado: {output_file}")
            return True
            
        except Exception as e:
            print(f"❌ Error creando pipeline de grabación: {e}")
            return False
    
    def create_frame_callback_pipeline(self, rtsp_url):
        """
        Pipeline para procesar frames individuales (para anotaciones)
        """
        
        pipeline_str = f"""
        rtspsrc location={rtsp_url} 
            protocols=tcp 
            latency=0
        ! queue max-size-buffers=1 leaky=downstream
        ! rtph264depay
        ! avdec_h264 max-threads=4
        ! videoconvert
        ! video/x-raw,format=RGB
        ! appsink name=sink 
            emit-signals=true 
            max-buffers=1 
            drop=true 
            sync=false
        """
        
        try:
            self.pipeline = Gst.parse_launch(pipeline_str)
            
            # Configurar appsink para callbacks
            self.sink = self.pipeline.get_by_name("sink")
            self.sink.connect("new-sample", self.on_new_sample)
            
            self.bus = self.pipeline.get_bus()
            self.bus.add_signal_watch()
            self.bus.connect("message", self.on_bus_message)
            
            return True
            
        except Exception as e:
            print(f"❌ Error creando pipeline de callbacks: {e}")
            return False
    
    def on_new_sample(self, sink):
        """Callback para procesar frames individuales"""
        print("🎬 Frame recibido!")  # Debug
        
        sample = sink.emit("pull-sample")
        if sample:
            print("✅ Sample obtenido")  # Debug
            self.latency_monitor.add_frame()
            
            if self.on_frame_callback:
                # Convertir sample a formato utilizable
                buffer = sample.get_buffer()
                caps = sample.get_caps()
                
                # Obtener información del frame
                structure = caps.get_structure(0)
                width = structure.get_int("width")[1]
                height = structure.get_int("height")[1]
                
                print(f"📐 Frame: {width}x{height}")  # Debug
                
                # Mapear buffer para acceso a datos
                success, map_info = buffer.map(Gst.MapFlags.READ)
                if success:
                    print(f"💾 Buffer mapeado: {len(map_info.data)} bytes")  # Debug
                    
                    # Datos del frame en formato RGB
                    frame_data = map_info.data
                    
                    # Llamar callback personalizado
                    self.on_frame_callback(frame_data, width, height)
                    
                    buffer.unmap(map_info)
                else:
                    print("❌ Error mapeando buffer")  # Debug
            else:
                print("❌ No hay callback configurado")  # Debug
        else:
            print("❌ No se pudo obtener sample")  # Debug
        
        return Gst.FlowReturn.OK
    
    def on_bus_message(self, bus, message):
        """Manejar mensajes del bus de GStreamer"""
        
        msg_type = message.type
        
        if msg_type == Gst.MessageType.ERROR:
            error, debug = message.parse_error()
            print(f"❌ GStreamer Error: {error}")
            print(f"🔧 Debug: {debug}")
            
            if self.on_error_callback:
                self.on_error_callback(error, debug)
                
        elif msg_type == Gst.MessageType.EOS:
            print("🎬 End of Stream")
            if self.on_eos_callback:
                self.on_eos_callback()
                
        elif msg_type == Gst.MessageType.STATE_CHANGED:
            if message.src == self.pipeline:
                old_state, new_state, pending = message.parse_state_changed()
                print(f"🔄 Pipeline state: {old_state.value_nick} → {new_state.value_nick}")
                
        elif msg_type == Gst.MessageType.LATENCY:
            print("⚡ Latencia reconfigurada por GStreamer")
            self.pipeline.recalculate_latency()
            
        elif msg_type == Gst.MessageType.WARNING:
            warning, debug = message.parse_warning()
            print(f"⚠️ GStreamer Warning: {warning}")
            
        elif msg_type == Gst.MessageType.INFO:
            info, debug = message.parse_info()
            print(f"ℹ️ GStreamer Info: {info}")
            
        elif msg_type == Gst.MessageType.STREAM_START:
            print("🎬 Stream iniciado - esperando frames...")
            
        elif msg_type == Gst.MessageType.ASYNC_DONE:
            print("✅ Pipeline listo para reproducir")
    
    def play(self):
        """Iniciar reproducción"""
        if self.pipeline:
            ret = self.pipeline.set_state(Gst.State.PLAYING)
            if ret == Gst.StateChangeReturn.FAILURE:
                print("❌ Error: No se pudo iniciar pipeline")
                return False
            
            self.is_playing = True
            print("▶️ Pipeline iniciado")
            return True
        
        return False
    
    def pause(self):
        """Pausar reproducción"""
        if self.pipeline:
            self.pipeline.set_state(Gst.State.PAUSED)
            self.is_playing = False
            print("⏸️ Pipeline pausado")
    
    def stop(self):
        """Detener pipeline"""
        if self.pipeline:
            self.pipeline.set_state(Gst.State.NULL)
            self.is_playing = False
            print("⏹️ Pipeline detenido")
    
    def get_stats(self):
        """Obtener estadísticas de rendimiento"""
        if not self.latency_monitor:
            return {}
        
        return {
            'fps': round(self.latency_monitor.get_fps(), 2),
            'avg_frame_time_ms': round(self.latency_monitor.get_avg_frame_time_ms(), 2),
            'total_frames': len(self.latency_monitor.frame_times)
        }

class UltraLowLatencyViewer(QMainWindow):
    """Visor principal con GStreamer ultra optimizado"""
    
    # Signal para actualizar frame
    frame_ready = pyqtSignal(np.ndarray, int, int)
    
    def __init__(self):
        super().__init__()
        self.gst_pipeline = UltraLowLatencyGStreamerPipeline()
        self.stats_timer = None
        
        self.setup_ui()
        self.setup_callbacks()
        
    def setup_ui(self):
        """Configurar interfaz minimalista para máximo rendimiento"""
        self.setWindowTitle("🚀 Ultra Low Latency Camera Viewer (GStreamer)")
        self.setGeometry(100, 100, 1200, 800)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # === CONTROLES MÍNIMOS ===
        controls_layout = QHBoxLayout()
        
        self.url_input = QLineEdit("rtsp://admin:Prototipo@192.168.18.25:554/Streaming/Channels/101")
        self.url_input.setPlaceholderText("RTSP URL de la cámara")
        
        self.connect_btn = QPushButton("🚀 CONECTAR ULTRA RÁPIDO")
        self.connect_btn.setStyleSheet("""
            QPushButton {
                background: #4CAF50; color: white; padding: 10px;
                border-radius: 5px; font-weight: bold;
            }
            QPushButton:hover { background: #45a049; }
        """)
        
        self.disconnect_btn = QPushButton("⏹️ DETENER")
        self.disconnect_btn.setEnabled(False)
        
        controls_layout.addWidget(QLabel("📹 URL:"))
        controls_layout.addWidget(self.url_input)
        controls_layout.addWidget(self.connect_btn)
        controls_layout.addWidget(self.disconnect_btn)
        
        # === ESTADÍSTICAS EN TIEMPO REAL ===
        self.stats_label = QLabel("📊 Esperando conexión...")
        self.stats_label.setStyleSheet("color: #FFA726; font-weight: bold; padding: 5px;")
        
        # === ÁREA DE VIDEO ===
        self.video_label = QLabel()
        self.video_label.setMinimumSize(800, 600)
        self.video_label.setStyleSheet("QLabel { background: black; border: 2px solid #4CAF50; }")
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setText("🎥 Esperando video...")
        self.video_label.setScaledContents(True)
        
        layout.addLayout(controls_layout)
        layout.addWidget(self.stats_label)
        layout.addWidget(self.video_label)
        
    def setup_callbacks(self):
        """Configurar callbacks"""
        self.connect_btn.clicked.connect(self.connect_ultra_fast)
        self.disconnect_btn.clicked.connect(self.disconnect)
        
        # Callbacks de GStreamer
        self.gst_pipeline.on_error_callback = self.on_gst_error
        self.gst_pipeline.on_eos_callback = self.on_gst_eos
        self.gst_pipeline.on_frame_callback = self.on_frame_received
        
        print("✅ Callbacks de GStreamer configurados")
        
        # Conectar signal para actualizar UI
        self.frame_ready.connect(self.update_video_frame)
        print("✅ Signal de frames conectado")
        
    def connect_ultra_fast(self):
        """Conectar con configuración ultra rápida"""
        url = self.url_input.text().strip()
        
        if not url:
            QMessageBox.warning(self, "Error", "Por favor ingresa una URL RTSP")
            return
        
        # Crear pipeline ultra optimizado
        success = self.gst_pipeline.create_ultra_low_latency_pipeline(url)
        
        if success:
            # Iniciar reproducción
            if self.gst_pipeline.play():
                self.connect_btn.setEnabled(False)
                self.disconnect_btn.setEnabled(True)
                self.stats_label.setText("⚡ Conectando con latencia ultra baja...")
                
                # Iniciar monitor de estadísticas
                self.start_stats_monitoring()
            else:
                QMessageBox.critical(self, "Error", "No se pudo iniciar la reproducción")
        else:
            QMessageBox.critical(self, "Error", "No se pudo crear el pipeline GStreamer")
    
    def disconnect(self):
        """Desconectar"""
        self.gst_pipeline.stop()
        
        if self.stats_timer:
            self.stats_timer.stop()
            self.stats_timer = None
        
        self.connect_btn.setEnabled(True)
        self.disconnect_btn.setEnabled(False)
        self.stats_label.setText("📊 Desconectado")
    
    def start_stats_monitoring(self):
        """Iniciar monitoreo de estadísticas"""
        self.stats_timer = QTimer()
        self.stats_timer.timeout.connect(self.update_stats)
        self.stats_timer.start(1000)  # Actualizar cada segundo
    
    def update_stats(self):
        """Actualizar estadísticas en tiempo real"""
        stats = self.gst_pipeline.get_stats()
        
        if stats:
            fps = stats.get('fps', 0)
            frame_time = stats.get('avg_frame_time_ms', 0)
            total_frames = stats.get('total_frames', 0)
            
            # Estimar latencia (frame time + overhead estimado)
            estimated_latency = frame_time + 30  # +30ms overhead estimado
            
            status = f"⚡ FPS: {fps} | 🕐 Latencia: ~{estimated_latency:.1f}ms | 📊 Frames: {total_frames}"
            
            # Color según latencia
            if estimated_latency < 100:
                color = "#4CAF50"  # Verde - Excelente
            elif estimated_latency < 200:
                color = "#FF9800"  # Naranja - Bueno
            else:
                color = "#F44336"  # Rojo - Mejorable
            
            self.stats_label.setText(status)
            self.stats_label.setStyleSheet(f"color: {color}; font-weight: bold; padding: 5px;")
    
    def on_gst_error(self, error, debug):
        """Manejar errores de GStreamer"""
        QMessageBox.critical(self, "Error GStreamer", f"Error: {error}\n\nDebug: {debug}")
        self.disconnect()
    
    def on_gst_eos(self):
        """Manejar fin de stream"""
        self.stats_label.setText("🔚 Stream terminado")
        self.disconnect()
    
    def on_frame_received(self, frame_data, width, height):
        """Callback cuando se recibe un frame de GStreamer"""
        try:
            # Convertir datos de frame a numpy array
            frame_array = np.frombuffer(frame_data, dtype=np.uint8)
            frame_array = frame_array.reshape((height, width, 3))
            
            # Emitir signal para actualizar UI (thread-safe)
            self.frame_ready.emit(frame_array, width, height)
            
        except Exception as e:
            print(f"❌ Error procesando frame: {e}")
    
    def update_video_frame(self, frame_array, width, height):
        """Actualizar frame en la UI (se ejecuta en el thread principal)"""
        try:
            # Convertir numpy array a QImage
            h, w, ch = frame_array.shape
            bytes_per_line = ch * w
            
            qt_image = QImage(
                frame_array.data, 
                w, h, 
                bytes_per_line, 
                QImage.Format.Format_RGB888
            )
            
            # Convertir a QPixmap y mostrar
            pixmap = QPixmap.fromImage(qt_image)
            
            # Escalar manteniendo aspecto
            scaled_pixmap = pixmap.scaled(
                self.video_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            
            self.video_label.setPixmap(scaled_pixmap)
            
        except Exception as e:
            print(f"❌ Error actualizando frame en UI: {e}")

def test_gstreamer_installation():
    """Verificar que GStreamer esté instalado correctamente"""
    try:
        Gst.init(None)
        version = Gst.version()
        print(f"✅ GStreamer {version.major}.{version.minor}.{version.micro} instalado correctamente")
        return True
    except Exception as e:
        print(f"❌ Error: GStreamer no instalado o configurado incorrectamente: {e}")
        print("\n💡 Para instalar GStreamer:")
        print("Ubuntu/Debian: sudo apt install python3-gst-1.0 gstreamer1.0-plugins-*")
        print("Windows: Instalar GStreamer SDK desde https://gstreamer.freedesktop.org/")
        print("macOS: brew install gstreamer")
        return False

def main():
    """Función principal"""
    # Verificar GStreamer
    if not test_gstreamer_installation():
        return
    
    app = QApplication(sys.argv)
    
    # Crear ventana
    window = UltraLowLatencyViewer()
    window.show()
    
    print("🚀 Ultra Low Latency Camera Viewer iniciado")
    print("⚡ Latencia esperada: 50-100ms")
    print("🎯 Para mejores resultados:")
    print("   • Usa conexión Ethernet")
    print("   • Configura cámara con GOP=1")
    print("   • Usa bitrate constante (CBR)")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 