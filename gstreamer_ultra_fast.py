# -*- coding: utf-8 -*-
"""
🚀 ULTRA LOW LATENCY CAMERA VIEWER
Usando GStreamer para latencia <100ms
"""

import sys
import subprocess
import os
import time
from datetime import datetime

try:
    import gi
    gi.require_version('Gst', '1.0')
    gi.require_version('Gtk', '3.0')
    from gi.repository import Gst, GObject, Gtk
    GSTREAMER_AVAILABLE = True
except ImportError:
    GSTREAMER_AVAILABLE = False

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QFrame, QMessageBox, QTextEdit
)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal, QProcess

class FFmpegDirectPlayer(QThread):
    """Player directo usando FFmpeg subprocess - Ultra rápido"""
    
    status_update = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.process = None
        self.url = ""
        self.running = False
        
    def set_url(self, url):
        self.url = url
        
    def run(self):
        """Ejecutar FFmpeg con configuración ultra rápida"""
        if not self.url:
            self.error_occurred.emit("URL no configurada")
            return
            
        # ✅ COMANDO FFMPEG ULTRA OPTIMIZADO
        cmd = [
            'ffplay',
            '-fflags', 'nobuffer+fastseek+flush_packets',
            '-flags', 'low_delay',
            '-strict', 'experimental',
            '-rtsp_transport', 'tcp',
            '-buffer_size', '1024',
            '-max_delay', '0',
            '-analyzeduration', '100000',
            '-probesize', '100000',
            '-sync', 'ext',
            '-vf', 'setpts=0.5*PTS',  # Acelerar reproducción ligeramente
            '-framedrop',
            '-infbuf',
            '-an',  # Sin audio
            self.url
        ]
        
        self.status_update.emit(f"🚀 Iniciando FFmpeg ultra rápido...")
        print(f"📝 Comando: {' '.join(cmd)}")
        
        try:
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            self.running = True
            self.status_update.emit("⚡ Streaming con latencia ultra baja...")
            
            # Monitorear proceso
            while self.running and self.process.poll() is None:
                self.msleep(100)
            
            if self.process.returncode != 0:
                stderr_output = self.process.stderr.read()
                self.error_occurred.emit(f"FFmpeg error: {stderr_output}")
            
        except Exception as e:
            self.error_occurred.emit(f"Error ejecutando FFmpeg: {str(e)}")
        finally:
            self.running = False
            self.status_update.emit("⏹️ Streaming detenido")
    
    def stop(self):
        """Detener el proceso"""
        self.running = False
        if self.process:
            self.process.terminate()
            self.process.wait()

class GStreamerDirectPlayer:
    """Player directo GStreamer sin GUI - Máxima velocidad"""
    
    def __init__(self):
        if GSTREAMER_AVAILABLE:
            Gst.init(None)
            self.pipeline = None
        
    def create_ultra_fast_pipeline(self, rtsp_url):
        """Crear pipeline ultra rápido"""
        if not GSTREAMER_AVAILABLE:
            return False
            
        # ✅ PIPELINE MÍNIMO PARA LATENCIA EXTREMA
        pipeline_desc = f"""
        rtspsrc location={rtsp_url} latency=0 protocols=tcp drop-on-latency=true
        ! queue max-size-buffers=1 max-size-time=0 leaky=downstream
        ! rtph264depay
        ! avdec_h264 max-threads=0 skip-frame=1
        ! videoconvert
        ! autovideosink sync=false async=false
        """
        
        try:
            self.pipeline = Gst.parse_launch(pipeline_desc)
            
            # Configurar latencia del pipeline
            self.pipeline.set_latency(0)
            
            return True
        except Exception as e:
            print(f"❌ Error creando pipeline GStreamer: {e}")
            return False
    
    def play(self):
        """Iniciar reproducción"""
        if self.pipeline:
            ret = self.pipeline.set_state(Gst.State.PLAYING)
            return ret != Gst.StateChangeReturn.FAILURE
        return False
    
    def stop(self):
        """Detener reproducción"""
        if self.pipeline:
            self.pipeline.set_state(Gst.State.NULL)

class UltraFastCameraViewer(QMainWindow):
    """Visor ultra rápido con múltiples métodos de reproducción"""
    
    def __init__(self):
        super().__init__()
        self.ffmpeg_player = FFmpegDirectPlayer()
        self.gstreamer_player = GStreamerDirectPlayer() if GSTREAMER_AVAILABLE else None
        self.current_method = "ffmpeg"
        
        self.setup_ui()
        self.setup_connections()
        
    def setup_ui(self):
        """Interfaz minimalista para máximo rendimiento"""
        self.setWindowTitle("⚡ ULTRA FAST CAMERA VIEWER")
        self.setGeometry(100, 100, 1000, 700)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # === MÉTODO DE REPRODUCCIÓN ===
        method_layout = QHBoxLayout()
        
        self.ffmpeg_btn = QPushButton("🚀 FFmpeg Ultra")
        self.ffmpeg_btn.setCheckable(True)
        self.ffmpeg_btn.setChecked(True)
        self.ffmpeg_btn.setStyleSheet("""
            QPushButton {
                background: #4CAF50; color: white; padding: 8px;
                border-radius: 4px; font-weight: bold;
            }
            QPushButton:checked { background: #2E7D32; }
            QPushButton:hover { background: #45a049; }
        """)
        
        self.gstreamer_btn = QPushButton("⚡ GStreamer Ultra")
        self.gstreamer_btn.setCheckable(True)
        self.gstreamer_btn.setEnabled(GSTREAMER_AVAILABLE)
        
        method_layout.addWidget(QLabel("🎯 Método:"))
        method_layout.addWidget(self.ffmpeg_btn)
        method_layout.addWidget(self.gstreamer_btn)
        method_layout.addStretch()
        
        if not GSTREAMER_AVAILABLE:
            gst_warning = QLabel("⚠️ GStreamer no disponible - usando FFmpeg")
            gst_warning.setStyleSheet("color: orange; font-weight: bold;")
            method_layout.addWidget(gst_warning)
        
        # === CONEXIÓN ===
        conn_layout = QHBoxLayout()
        
        self.url_input = QLineEdit("rtsp://admin:Prototipo@192.168.18.25:554/Streaming/Channels/101")
        self.url_input.setPlaceholderText("RTSP URL")
        
        self.connect_btn = QPushButton("🚀 CONECTAR ULTRA RÁPIDO")
        self.connect_btn.setStyleSheet("""
            QPushButton {
                background: #FF5722; color: white; padding: 12px;
                border-radius: 6px; font-weight: bold; font-size: 14px;
            }
            QPushButton:hover { background: #E64A19; }
        """)
        
        self.stop_btn = QPushButton("⏹️ DETENER")
        self.stop_btn.setEnabled(False)
        
        conn_layout.addWidget(QLabel("📹"))
        conn_layout.addWidget(self.url_input)
        conn_layout.addWidget(self.connect_btn)
        conn_layout.addWidget(self.stop_btn)
        
        # === STATUS ===
        self.status_label = QLabel("⚡ Listo para streaming ultra rápido")
        self.status_label.setStyleSheet("color: #4CAF50; font-weight: bold; padding: 10px;")
        
        # === INFORMACIÓN ===
        info_text = QTextEdit()
        info_text.setMaximumHeight(150)
        info_text.setReadOnly(True)
        info_text.setHtml("""
        <h3>🚀 Ultra Low Latency Streaming</h3>
        <b>Latencia esperada:</b><br>
        • FFmpeg: ~80-150ms<br>
        • GStreamer: ~50-100ms<br><br>
        
        <b>🎯 Para mejor rendimiento:</b><br>
        • Conexión Ethernet (no WiFi)<br>
        • Cámara con GOP=1, CBR<br>
        • Reducir resolución si es necesario<br>
        • Cerrar otras aplicaciones
        """)
        
        # === COMANDOS DIRECTOS ===
        cmd_layout = QHBoxLayout()
        
        self.terminal_btn = QPushButton("💻 Abrir en Terminal")
        self.terminal_btn.setStyleSheet("QPushButton { background: #607D8B; color: white; padding: 8px; }")
        
        cmd_layout.addWidget(self.terminal_btn)
        cmd_layout.addStretch()
        
        # Agregar todo al layout
        layout.addLayout(method_layout)
        layout.addLayout(conn_layout)
        layout.addWidget(self.status_label)
        layout.addWidget(info_text)
        layout.addLayout(cmd_layout)
        
    def setup_connections(self):
        """Configurar conexiones de botones"""
        self.connect_btn.clicked.connect(self.connect_ultra_fast)
        self.stop_btn.clicked.connect(self.stop_streaming)
        self.terminal_btn.clicked.connect(self.open_in_terminal)
        
        self.ffmpeg_btn.clicked.connect(lambda: self.set_method("ffmpeg"))
        self.gstreamer_btn.clicked.connect(lambda: self.set_method("gstreamer"))
        
        # Conexiones FFmpeg
        self.ffmpeg_player.status_update.connect(self.update_status)
        self.ffmpeg_player.error_occurred.connect(self.show_error)
        
    def set_method(self, method):
        """Cambiar método de reproducción"""
        self.current_method = method
        
        if method == "ffmpeg":
            self.ffmpeg_btn.setChecked(True)
            self.gstreamer_btn.setChecked(False)
        else:
            self.ffmpeg_btn.setChecked(False)
            self.gstreamer_btn.setChecked(True)
        
        self.update_status(f"🎯 Método seleccionado: {method.upper()}")
    
    def connect_ultra_fast(self):
        """Conectar con el método seleccionado"""
        url = self.url_input.text().strip()
        
        if not url:
            QMessageBox.warning(self, "Error", "Por favor ingresa una URL RTSP")
            return
        
        if self.current_method == "ffmpeg":
            # Usar FFmpeg
            self.ffmpeg_player.set_url(url)
            self.ffmpeg_player.start()
            
        elif self.current_method == "gstreamer" and self.gstreamer_player:
            # Usar GStreamer
            if self.gstreamer_player.create_ultra_fast_pipeline(url):
                if self.gstreamer_player.play():
                    self.update_status("⚡ GStreamer ultra rápido iniciado")
                else:
                    self.show_error("No se pudo iniciar GStreamer")
            else:
                self.show_error("No se pudo crear pipeline GStreamer")
        
        # Actualizar UI
        self.connect_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.url_input.setEnabled(False)
    
    def stop_streaming(self):
        """Detener streaming"""
        if self.current_method == "ffmpeg":
            self.ffmpeg_player.stop()
            
        elif self.current_method == "gstreamer" and self.gstreamer_player:
            self.gstreamer_player.stop()
        
        # Restaurar UI
        self.connect_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.url_input.setEnabled(True)
        self.update_status("⏹️ Streaming detenido")
    
    def update_status(self, message):
        """Actualizar estado"""
        self.status_label.setText(message)
        
        # Color según mensaje
        if "error" in message.lower() or "❌" in message:
            color = "#F44336"
        elif "ultra" in message.lower() or "⚡" in message:
            color = "#4CAF50"
        else:
            color = "#FF9800"
        
        self.status_label.setStyleSheet(f"color: {color}; font-weight: bold; padding: 10px;")
    
    def show_error(self, error):
        """Mostrar error"""
        self.update_status(f"❌ Error: {error}")
        QMessageBox.critical(self, "Error", error)
        self.stop_streaming()
    
    def open_in_terminal(self):
        """Abrir comando optimizado en terminal"""
        url = self.url_input.text().strip()
        
        if not url:
            QMessageBox.warning(self, "Error", "Primero ingresa una URL")
            return
        
        # Comando FFmpeg ultra optimizado
        ffmpeg_cmd = f'''ffplay -fflags nobuffer+fastseek+flush_packets -flags low_delay -rtsp_transport tcp -buffer_size 1024 -max_delay 0 -analyzeduration 100000 -probesize 100000 -sync ext -vf "setpts=0.5*PTS" -framedrop -infbuf -an "{url}"'''
        
        # Comando GStreamer ultra optimizado
        gst_cmd = f'''gst-launch-1.0 rtspsrc location="{url}" latency=0 protocols=tcp drop-on-latency=true ! queue max-size-buffers=1 leaky=downstream ! rtph264depay ! avdec_h264 max-threads=0 skip-frame=1 ! videoconvert ! autovideosink sync=false async=false'''
        
        commands_text = f"""
🚀 COMANDOS ULTRA OPTIMIZADOS:

=== FFmpeg Ultra ===
{ffmpeg_cmd}

=== GStreamer Ultra ===
{gst_cmd}

💡 Copia y pega en tu terminal para latencia mínima
        """
        
        # Crear ventana de comandos
        cmd_window = QMessageBox(self)
        cmd_window.setWindowTitle("💻 Comandos Optimizados")
        cmd_window.setText(commands_text)
        cmd_window.setTextFormat(Qt.TextFormat.PlainText)
        cmd_window.exec()

def check_dependencies():
    """Verificar dependencias necesarias"""
    print("🔍 Verificando dependencias...")
    
    # Verificar FFmpeg
    try:
        result = subprocess.run(['ffplay', '-version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✅ FFmpeg/FFplay disponible")
            ffmpeg_ok = True
        else:
            print("❌ FFplay no encontrado")
            ffmpeg_ok = False
    except Exception as e:
        print(f"❌ Error verificando FFmpeg: {e}")
        ffmpeg_ok = False
    
    # Verificar GStreamer
    gst_ok = GSTREAMER_AVAILABLE
    if gst_ok:
        print("✅ GStreamer disponible")
    else:
        print("❌ GStreamer no disponible")
    
    if not ffmpeg_ok and not gst_ok:
        print("\n💡 INSTALACIÓN REQUERIDA:")
        print("Windows: Descargar FFmpeg desde https://ffmpeg.org/")
        print("Ubuntu: sudo apt install ffmpeg gstreamer1.0-tools")
        print("macOS: brew install ffmpeg gstreamer")
        
    return ffmpeg_ok or gst_ok

def main():
    """Función principal"""
    print("⚡ ULTRA FAST CAMERA VIEWER")
    print("=" * 40)
    
    if not check_dependencies():
        print("❌ No se encontraron las dependencias necesarias")
        return
    
    app = QApplication(sys.argv)
    
    # Configurar GObject si está disponible
    if GSTREAMER_AVAILABLE:
        GObject.threads_init()
    
    window = UltraFastCameraViewer()
    window.show()
    
    print("\n🚀 Aplicación iniciada")
    print("⚡ Latencia objetivo: <150ms")
    print("🎯 Usa FFmpeg para máxima compatibilidad")
    print("🔥 Usa GStreamer para mínima latencia")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 