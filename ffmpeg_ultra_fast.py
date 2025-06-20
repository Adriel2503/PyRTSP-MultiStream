# -*- coding: utf-8 -*-
"""
🚀 FFmpeg Ultra Fast Camera Viewer
Latencia mínima usando FFmpeg directo
"""

import sys
import subprocess
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QMessageBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QProcess

class FFmpegUltraPlayer(QThread):
    """Player ultra rápido usando FFmpeg subprocess"""
    
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
        """Ejecutar FFmpeg con configuración ultra optimizada"""
        # ✅ COMANDO FFMPEG ULTRA OPTIMIZADO PARA BAJA LATENCIA
        cmd = [
            'ffplay',
            # === CONFIGURACIONES DE BUFFER ===
            '-fflags', 'nobuffer+fastseek+flush_packets',
            '-flags', 'low_delay',
            '-strict', 'experimental',
            
            # === CONFIGURACIONES RTSP ===
            '-rtsp_transport', 'tcp',
            '-buffer_size', '1024',
            '-max_delay', '0',
            
            # === ANÁLISIS MÍNIMO ===
            '-analyzeduration', '100000',  # 0.1 segundo
            '-probesize', '100000',        # 100KB
            
            # === SINCRONIZACIÓN ===
            '-sync', 'ext',
            '-framedrop',
            '-infbuf',
            
            # === SIN AUDIO PARA VELOCIDAD ===
            '-an',
            
            # === VENTANA ===
            '-window_title', '⚡ Ultra Fast Stream',
            '-noborder',
            
            self.url
        ]
        
        print(f"🚀 Comando FFmpeg: {' '.join(cmd)}")
        self.status_update.emit("⚡ Iniciando stream ultra rápido...")
        
        try:
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            self.running = True
            self.status_update.emit("🔥 Stream activo - Latencia ultra baja")
            
            # Esperar a que termine el proceso
            self.process.wait()
            
        except FileNotFoundError:
            self.error_occurred.emit("❌ FFmpeg no encontrado. Instala FFmpeg primero.")
        except Exception as e:
            self.error_occurred.emit(f"❌ Error: {str(e)}")
        finally:
            self.running = False
            self.status_update.emit("⏹️ Stream detenido")
    
    def stop(self):
        """Detener el proceso"""
        self.running = False
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self.process.kill()

class UltraFastViewer(QMainWindow):
    """Interfaz minimalista para máximo rendimiento"""
    
    def __init__(self):
        super().__init__()
        self.player = FFmpegUltraPlayer()
        self.setup_ui()
        self.setup_connections()
        
    def setup_ui(self):
        """Interfaz ultra simple"""
        self.setWindowTitle("⚡ Ultra Fast Camera Viewer - FFmpeg")
        self.setGeometry(100, 100, 800, 400)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # === TÍTULO ===
        title = QLabel("🚀 ULTRA FAST STREAMING")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #4CAF50; margin: 10px;")
        
        # === URL INPUT ===
        url_layout = QHBoxLayout()
        url_layout.addWidget(QLabel("📹 RTSP URL:"))
        
        self.url_input = QLineEdit("rtsp://admin:Prototipo@192.168.18.25:554/Streaming/Channels/101")
        self.url_input.setStyleSheet("padding: 8px; font-size: 12px;")
        url_layout.addWidget(self.url_input)
        
        # === BOTONES ===
        buttons_layout = QHBoxLayout()
        
        self.connect_btn = QPushButton("🚀 CONECTAR ULTRA RÁPIDO")
        self.connect_btn.setStyleSheet("""
            QPushButton {
                background: #4CAF50; color: white; padding: 15px;
                font-size: 16px; font-weight: bold; border-radius: 8px;
            }
            QPushButton:hover { background: #45a049; }
        """)
        
        self.stop_btn = QPushButton("⏹️ DETENER")
        self.stop_btn.setEnabled(False)
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background: #F44336; color: white; padding: 15px;
                font-size: 16px; font-weight: bold; border-radius: 8px;
            }
            QPushButton:hover { background: #da190b; }
        """)
        
        buttons_layout.addWidget(self.connect_btn)
        buttons_layout.addWidget(self.stop_btn)
        
        # === STATUS ===
        self.status_label = QLabel("⚡ Listo para streaming ultra rápido")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("font-size: 14px; font-weight: bold; padding: 10px; color: #4CAF50;")
        
        # === INFORMACIÓN ===
        info_text = QTextEdit()
        info_text.setMaximumHeight(120)
        info_text.setReadOnly(True)
        info_text.setHtml("""
        <div style="font-family: Arial; font-size: 12px;">
        <b>🎯 Optimizaciones activas:</b><br>
        • Sin buffers (nobuffer + flush_packets)<br>
        • TCP para RTSP (más estable)<br>
        • Análisis mínimo (0.1s, 100KB)<br>
        • Sin audio (solo video)<br>
        • Frame dropping habilitado<br><br>
        
        <b>⚡ Latencia esperada: 80-150ms</b>
        </div>
        """)
        
        # === COMANDO MANUAL ===
        cmd_layout = QHBoxLayout()
        self.show_cmd_btn = QPushButton("💻 Mostrar Comando")
        self.show_cmd_btn.setStyleSheet("QPushButton { background: #607D8B; color: white; padding: 8px; }")
        cmd_layout.addWidget(self.show_cmd_btn)
        cmd_layout.addStretch()
        
        # Agregar todo
        layout.addWidget(title)
        layout.addLayout(url_layout)
        layout.addLayout(buttons_layout)
        layout.addWidget(self.status_label)
        layout.addWidget(info_text)
        layout.addLayout(cmd_layout)
        
    def setup_connections(self):
        """Conectar señales"""
        self.connect_btn.clicked.connect(self.start_streaming)
        self.stop_btn.clicked.connect(self.stop_streaming)
        self.show_cmd_btn.clicked.connect(self.show_command)
        
        self.player.status_update.connect(self.update_status)
        self.player.error_occurred.connect(self.show_error)
        
    def start_streaming(self):
        """Iniciar streaming ultra rápido"""
        url = self.url_input.text().strip()
        
        if not url:
            QMessageBox.warning(self, "Error", "Por favor ingresa una URL RTSP")
            return
        
        # Configurar y iniciar player
        self.player.set_url(url)
        self.player.start()
        
        # Actualizar UI
        self.connect_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.url_input.setEnabled(False)
        
    def stop_streaming(self):
        """Detener streaming"""
        self.player.stop()
        
        # Restaurar UI
        self.connect_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.url_input.setEnabled(True)
        
    def update_status(self, message):
        """Actualizar estado"""
        self.status_label.setText(message)
        
        # Color según mensaje
        if "❌" in message or "error" in message.lower():
            color = "#F44336"
        elif "🔥" in message or "activo" in message:
            color = "#4CAF50"
        elif "⚡" in message:
            color = "#FF9800"
        else:
            color = "#9E9E9E"
            
        self.status_label.setStyleSheet(f"font-size: 14px; font-weight: bold; padding: 10px; color: {color};")
    
    def show_error(self, error):
        """Mostrar error"""
        QMessageBox.critical(self, "Error", error)
        self.stop_streaming()
        
    def show_command(self):
        """Mostrar comando FFmpeg optimizado"""
        url = self.url_input.text().strip()
        
        if not url:
            url = "rtsp://tu_camara_ip"
        
        command = f'''ffplay -fflags nobuffer+fastseek+flush_packets -flags low_delay -rtsp_transport tcp -buffer_size 1024 -max_delay 0 -analyzeduration 100000 -probesize 100000 -sync ext -framedrop -infbuf -an "{url}"'''
        
        msg = QMessageBox(self)
        msg.setWindowTitle("💻 Comando FFmpeg Ultra Optimizado")
        msg.setText("Copia este comando para usar directamente en terminal:")
        msg.setDetailedText(command)
        msg.exec()

def check_ffmpeg():
    """Verificar si FFmpeg está instalado"""
    try:
        result = subprocess.run(['ffplay', '-version'], 
                              capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except Exception:
        return False

def main():
    """Función principal"""
    print("⚡ Ultra Fast Camera Viewer - FFmpeg")
    print("=" * 40)
    
    # Verificar FFmpeg
    if not check_ffmpeg():
        print("❌ FFmpeg no encontrado")
        print("\n💡 INSTALACIÓN:")
        print("Windows: Descargar desde https://ffmpeg.org/")
        print("Ubuntu: sudo apt install ffmpeg")
        print("macOS: brew install ffmpeg")
        
        # Mostrar error en GUI también
        app = QApplication(sys.argv)
        QMessageBox.critical(None, "FFmpeg No Encontrado", 
                           "FFmpeg no está instalado.\n\n"
                           "Windows: Descargar desde https://ffmpeg.org/\n"
                           "Ubuntu: sudo apt install ffmpeg\n"
                           "macOS: brew install ffmpeg")
        return
    
    print("✅ FFmpeg encontrado")
    
    app = QApplication(sys.argv)
    
    window = UltraFastViewer()
    window.show()
    
    print("🚀 Aplicación iniciada")
    print("⚡ Latencia objetivo: 80-150ms")
    print("🔥 Optimizado para máxima velocidad")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 