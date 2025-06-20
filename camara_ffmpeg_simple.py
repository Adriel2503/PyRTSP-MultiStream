#!/usr/bin/env python3
"""
Visor de Cámara IP Ultra Rápido usando solo FFmpeg
Versión simplificada sin dependencias complicadas para Windows
"""

import sys
import os
import subprocess
import threading
import time
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLineEdit, QLabel, 
                            QTextEdit, QGroupBox, QSpinBox, QComboBox)
from PyQt6.QtCore import QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QFont

class StreamingThread(QThread):
    """Thread para manejar el streaming de FFmpeg"""
    
    log_signal = pyqtSignal(str)
    
    def __init__(self, rtsp_url, output_format="display"):
        super().__init__()
        self.rtsp_url = rtsp_url
        self.output_format = output_format
        self.process = None
        self.running = False
        
    def run(self):
        """Ejecutar FFmpeg"""
        self.running = True
        
        if self.output_format == "display":
            # Solo mostrar video en ventana
            comando = self.generar_comando_display()
        elif self.output_format == "record":
            # Grabar a archivo
            comando = self.generar_comando_grabacion()
        else:
            # Mostrar y grabar simultáneamente
            comando = self.generar_comando_dual()
        
        self.log_signal.emit(f"🚀 Ejecutando: {comando}")
        
        try:
            self.process = subprocess.Popen(
                comando,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Leer stderr para obtener información de FFmpeg
            while self.running and self.process.poll() is None:
                if self.process.stderr:
                    linea = self.process.stderr.readline()
                    if linea:
                        self.log_signal.emit(linea.strip())
                
                time.sleep(0.1)
                
        except Exception as e:
            self.log_signal.emit(f"❌ Error: {e}")
    
    def generar_comando_display(self):
        """Comando para mostrar video únicamente"""
        return f'''ffmpeg -i "{self.rtsp_url}" -f sdl "Cámara IP - Ultra Baja Latencia" -fflags nobuffer -flags low_delay -framedrop -avioflags direct -probesize 32 -analyzeduration 0'''
    
    def generar_comando_grabacion(self):
        """Comando para grabar video"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archivo = f"videos_grabados/camara_ffmpeg_{timestamp}.mp4"
        
        # Crear directorio si no existe
        os.makedirs("videos_grabados", exist_ok=True)
        
        return f'''ffmpeg -i "{self.rtsp_url}" -c copy -f mp4 "{archivo}" -fflags nobuffer -flags low_delay -avioflags direct'''
    
    def generar_comando_dual(self):
        """Comando para mostrar y grabar simultáneamente"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archivo = f"videos_grabados/camara_ffmpeg_{timestamp}.mp4"
        
        os.makedirs("videos_grabados", exist_ok=True)
        
        return f'''ffmpeg -i "{self.rtsp_url}" -f sdl "Cámara IP" -c copy -f mp4 "{archivo}" -fflags nobuffer -flags low_delay -framedrop -avioflags direct -probesize 32'''
    
    def stop(self):
        """Detener el streaming"""
        self.running = False
        if self.process:
            self.process.terminate()
            self.process.wait()

class CamaraFFmpegViewer(QMainWindow):
    """Ventana principal del visor de cámara FFmpeg"""
    
    def __init__(self):
        super().__init__()
        self.streaming_thread = None
        self.init_ui()
        self.verificar_ffmpeg()
        
    def init_ui(self):
        """Inicializar interfaz de usuario"""
        self.setWindowTitle("Cámara IP - FFmpeg Ultra Rápido")
        self.setGeometry(100, 100, 800, 600)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Configuración de conexión
        config_group = QGroupBox("Configuración de Cámara")
        config_layout = QVBoxLayout(config_group)
        
        # URL RTSP
        url_layout = QHBoxLayout()
        url_layout.addWidget(QLabel("URL RTSP:"))
        self.url_input = QLineEdit("rtsp://192.168.1.100:554/stream")
        url_layout.addWidget(self.url_input)
        config_layout.addLayout(url_layout)
        
        # Modo de operación
        modo_layout = QHBoxLayout()
        modo_layout.addWidget(QLabel("Modo:"))
        self.modo_combo = QComboBox()
        self.modo_combo.addItems(["Solo Visualizar", "Solo Grabar", "Visualizar y Grabar"])
        modo_layout.addWidget(self.modo_combo)
        config_layout.addLayout(modo_layout)
        
        layout.addWidget(config_group)
        
        # Botones de control
        botones_layout = QHBoxLayout()
        
        self.btn_iniciar = QPushButton("🎥 Iniciar Stream")
        self.btn_iniciar.clicked.connect(self.iniciar_stream)
        botones_layout.addWidget(self.btn_iniciar)
        
        self.btn_parar = QPushButton("⏹️ Parar Stream")
        self.btn_parar.clicked.connect(self.parar_stream)
        self.btn_parar.setEnabled(False)
        botones_layout.addWidget(self.btn_parar)
        
        self.btn_comando = QPushButton("📋 Mostrar Comando")
        self.btn_comando.clicked.connect(self.mostrar_comando)
        botones_layout.addWidget(self.btn_comando)
        
        layout.addLayout(botones_layout)
        
        # Log de salida
        log_group = QGroupBox("Información y Log")
        log_layout = QVBoxLayout(log_group)
        
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(200)
        self.log_text.setFont(QFont("Consolas", 9))
        log_layout.addWidget(self.log_text)
        
        layout.addWidget(log_group)
        
        # Información útil
        info_group = QGroupBox("Información")
        info_layout = QVBoxLayout(info_group)
        
        info_text = QLabel("""
💡 CONSEJOS:
• FFmpeg debe estar instalado y en el PATH del sistema
• Latencia esperada: 80-150ms (muy buena para streaming RTSP)
• Si no tienes FFmpeg: descargar desde https://ffmpeg.org/download.html
• URLs típicas: rtsp://ip:554/stream, rtsp://admin:pass@ip:554/cam/realmonitor
• Para probar: usa "Solo Visualizar" primero
        """)
        info_text.setWordWrap(True)
        info_layout.addWidget(info_text)
        
        layout.addWidget(info_group)
    
    def verificar_ffmpeg(self):
        """Verificar si FFmpeg está disponible"""
        try:
            resultado = subprocess.run(
                ["ffmpeg", "-version"], 
                capture_output=True, 
                text=True,
                timeout=5
            )
            
            if resultado.returncode == 0:
                version_info = resultado.stdout.split('\n')[0]
                self.agregar_log(f"✅ {version_info}")
            else:
                self.mostrar_error_ffmpeg()
                
        except FileNotFoundError:
            self.mostrar_error_ffmpeg()
        except Exception as e:
            self.agregar_log(f"⚠️ Error verificando FFmpeg: {e}")
            self.mostrar_error_ffmpeg()
    
    def mostrar_error_ffmpeg(self):
        """Mostrar información sobre cómo instalar FFmpeg"""
        self.agregar_log("❌ FFmpeg no encontrado en el sistema")
        self.agregar_log("📥 Para instalar FFmpeg:")
        self.agregar_log("   1. Descargar desde: https://ffmpeg.org/download.html")
        self.agregar_log("   2. Extraer en C:\\ffmpeg")
        self.agregar_log("   3. Agregar C:\\ffmpeg\\bin al PATH de Windows")
        self.agregar_log("   4. Reiniciar la aplicación")
        self.agregar_log("")
        self.agregar_log("🔧 Alternativas de instalación:")
        self.agregar_log("   • Con Chocolatey: choco install ffmpeg")
        self.agregar_log("   • Con winget: winget install ffmpeg")
    
    def iniciar_stream(self):
        """Iniciar streaming"""
        if self.streaming_thread and self.streaming_thread.isRunning():
            return
        
        url = self.url_input.text().strip()
        if not url:
            self.agregar_log("❌ Ingresa una URL RTSP válida")
            return
        
        # Determinar modo
        modo_index = self.modo_combo.currentIndex()
        if modo_index == 0:
            output_format = "display"
        elif modo_index == 1:
            output_format = "record"
        else:
            output_format = "dual"
        
        self.agregar_log(f"🚀 Iniciando stream desde: {url}")
        self.agregar_log(f"📺 Modo: {self.modo_combo.currentText()}")
        
        # Crear y iniciar thread
        self.streaming_thread = StreamingThread(url, output_format)
        self.streaming_thread.log_signal.connect(self.agregar_log)
        self.streaming_thread.start()
        
        # Actualizar botones
        self.btn_iniciar.setEnabled(False)
        self.btn_parar.setEnabled(True)
    
    def parar_stream(self):
        """Parar streaming"""
        if self.streaming_thread:
            self.agregar_log("⏹️ Deteniendo stream...")
            self.streaming_thread.stop()
            self.streaming_thread.wait()
            self.streaming_thread = None
        
        # Actualizar botones
        self.btn_iniciar.setEnabled(True)
        self.btn_parar.setEnabled(False)
        self.agregar_log("✅ Stream detenido")
    
    def mostrar_comando(self):
        """Mostrar el comando FFmpeg que se ejecutaría"""
        url = self.url_input.text().strip()
        if not url:
            self.agregar_log("❌ Ingresa una URL RTSP primero")
            return
        
        # Crear thread temporal solo para generar comando
        temp_thread = StreamingThread(url, "display")
        comando_display = temp_thread.generar_comando_display()
        comando_record = temp_thread.generar_comando_grabacion()
        comando_dual = temp_thread.generar_comando_dual()
        
        self.agregar_log("📋 COMANDOS FFMPEG:")
        self.agregar_log("━" * 50)
        self.agregar_log("🖥️ Solo visualizar:")
        self.agregar_log(comando_display)
        self.agregar_log("")
        self.agregar_log("💾 Solo grabar:")
        self.agregar_log(comando_record)
        self.agregar_log("")
        self.agregar_log("🖥️💾 Visualizar y grabar:")
        self.agregar_log(comando_dual)
        self.agregar_log("━" * 50)
    
    def agregar_log(self, mensaje):
        """Agregar mensaje al log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {mensaje}")
        
        # Auto-scroll al final
        cursor = self.log_text.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.log_text.setTextCursor(cursor)
    
    def closeEvent(self, event):
        """Manejar cierre de aplicación"""
        if self.streaming_thread:
            self.parar_stream()
        event.accept()

def main():
    app = QApplication(sys.argv)
    
    # Configurar estilo
    app.setStyle('Fusion')
    
    ventana = CamaraFFmpegViewer()
    ventana.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 