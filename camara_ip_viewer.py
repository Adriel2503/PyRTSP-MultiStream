import sys
import os
import time
from datetime import datetime
import vlc
import cv2
import numpy as np
import threading
from PIL import ImageGrab
import subprocess

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QGridLayout, QLabel, QLineEdit, QPushButton, QFrame, QTextEdit,
    QSplitter, QGroupBox, QListWidget, QMessageBox, QProgressBar,
    QSlider, QCheckBox, QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal, QPoint, QRect
from PyQt6.QtGui import QFont, QPixmap, QIcon, QPainter, QPen, QColor

import qdarkstyle
import qtawesome as qta

# ✅ IMPORTAR CONFIGURACIONES DE BAJA LATENCIA
from low_latency_config import (
    VLC_ULTRA_LOW_LATENCY_ARGS,
    apply_opencv_ultra_low_latency,
    LatencyMonitor,
    get_optimized_config
)


class ConnectionTestThread(QThread):
    """Hilo para probar conexiones a cámaras IP sin bloquear la UI"""
    
    progress_update = pyqtSignal(str)  # Mensaje de progreso general
    url_test_start = pyqtSignal(int, str, str)  # índice, url_display, tipo
    url_test_result = pyqtSignal(int, bool, str, float)  # índice, success, error_msg, tiempo
    connection_result = pyqtSignal(bool, str, int, int)  # success, url, width, height
    
    def __init__(self, possible_urls):
        super().__init__()
        self.possible_urls = possible_urls
        self.should_stop = False
        self.url_types = [
            "RTSP Stream",
            "RTSP Live", 
            "RTSP Stream1",
            "RTSP Monitor",
            "HTTP Video",
            "MJPEG Stream"
        ]
    
    def run(self):
        """Probar la URL específica de la cámara"""
        self.progress_update.emit(f"🔍 Conectando a cámara IP específica...")
        
        for i, url in enumerate(self.possible_urls):
            if self.should_stop:
                return
                
            # Mostrar qué URL está probando
            url_display = url.split('@')[1] if '@' in url else url
            url_type = "RTSP Stream - Canal 101"
            
            self.url_test_start.emit(i, url_display, url_type)
            start_time = time.time()
            
            try:
                # ✅ CONFIGURACIÓN ULTRA OPTIMIZADA DE OPENCV
                cap = cv2.VideoCapture(url, cv2.CAP_FFMPEG)
                
                # Aplicar configuraciones ultra optimizadas
                cap = apply_opencv_ultra_low_latency(cap)
                
                print(f"🚀 OpenCV configurado con optimizaciones ultra de baja latencia")
                
                if cap.isOpened():
                    ret, frame = cap.read()
                    if ret and frame is not None:
                        # ✅ Conexión exitosa
                        elapsed_time = time.time() - start_time
                        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                        cap.release()
                        
                        self.url_test_result.emit(i, True, f"Conectado - {width}x{height}", elapsed_time)
                        self.connection_result.emit(True, url, width, height)
                        return
                    else:
                        elapsed_time = time.time() - start_time
                        self.url_test_result.emit(i, False, "No se pudo leer frame", elapsed_time)
                else:
                    elapsed_time = time.time() - start_time
                    self.url_test_result.emit(i, False, "No se pudo abrir stream", elapsed_time)
                    
                cap.release()
                
            except Exception as e:
                elapsed_time = time.time() - start_time
                error_msg = str(e)[:40] + "..." if len(str(e)) > 40 else str(e)
                self.url_test_result.emit(i, False, f"Error: {error_msg}", elapsed_time)
                continue
        
        # Si llega aquí, la URL específica no funcionó
        self.progress_update.emit("❌ No se pudo conectar a la cámara")
        self.connection_result.emit(False, "", 0, 0)
    
    def stop(self):
        """Detener la prueba de conexiones"""
        self.should_stop = True


class MovableAnnotationWidget(QWidget):
    """Widget de anotación movible sobre el video con diseño moderno"""
    
    annotation_saved = pyqtSignal(str, int, int, float)  # texto, x, y, tiempo_inicial
    text_changed = pyqtSignal(int, str)        # widget_id, texto
    position_changed = pyqtSignal(int, int, int)  # widget_id, x, y
    annotation_cancelled = pyqtSignal(int)     # widget_id
    finished = pyqtSignal()                    # cuando se cierra el widget
    
    def __init__(self, parent=None, video_start_time=0):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.video_start_time = video_start_time  # Tiempo del video cuando se hizo clic en anotar
        self.creation_time = time.time()  # Tiempo real cuando se creó el widget
        self.widget_id = 0  # Se asignará desde el main window
        self.setup_ui()
        self.dragging = False
        self.drag_position = QPoint()
        
    def setup_ui(self):
        self.setFixedSize(340, 160)
        
        # Container principal con sombra y bordes redondeados
        main_widget = QWidget()
        main_widget.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 rgba(45, 45, 45, 240), 
                    stop:1 rgba(25, 25, 25, 240));
                border: 2px solid rgba(76, 175, 80, 180);
                border-radius: 15px;
                box-shadow: 0px 10px 30px rgba(0, 0, 0, 100);
            }
        """)
        
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(8)
        
        # Header con solo timer
        header_layout = QHBoxLayout()
        
        # Mostrar tiempo fijo del momento del clic
        self.timer_label = QLabel(self.format_video_time(self.video_start_time))
        self.timer_label.setStyleSheet("""
            QLabel {
                color: #FFA726;
                font-weight: bold;
                font-size: 12px;
                background: rgba(255, 167, 38, 30);
                padding: 3px 8px;
                border-radius: 10px;
            }
        """)
        
        header_layout.addStretch()
        header_layout.addWidget(self.timer_label)
        
        # Campo de texto mejorado y funcional
        self.text_edit = QTextEdit()
        self.text_edit.setMinimumHeight(70)
        self.text_edit.setMaximumHeight(85)
        self.text_edit.setPlaceholderText("Escribe tu observación aquí...")
        self.text_edit.setTabChangesFocus(True)  # Permitir navegación con Tab
        self.text_edit.setAcceptRichText(False)  # Solo texto plano
        self.text_edit.setStyleSheet("""
            QTextEdit {
                background: white;
                border: 2px solid #4CAF50;
                border-radius: 8px;
                padding: 10px;
                font-size: 13px;
                font-family: Arial, sans-serif;
                color: black;
            }
            QTextEdit:focus {
                border: 3px solid #4CAF50;
                background: white;
            }
        """)
        
        # ✅ CONECTAR cambios de texto en tiempo real
        self.text_edit.textChanged.connect(self.on_text_changed)
        
        # Botones centrados con mejor espaciado
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        self.cancel_btn = QPushButton("❌ Cancelar")
        self.save_btn = QPushButton("✅ Guardar")
        
        # Estilos de botones modernos y centrados
        button_style_base = """
            QPushButton {
                border: none;
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 12px;
                min-width: 90px;
                max-width: 120px;
            }
        """
        
        self.cancel_btn.setStyleSheet(button_style_base + """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #EF5350, stop:1 #F44336);
                color: white;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #F44336, stop:1 #D32F2F);
                transform: scale(1.03);
            }
            QPushButton:pressed {
                background: #D32F2F;
            }
        """)
        
        self.save_btn.setStyleSheet(button_style_base + """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #66BB6A, stop:1 #4CAF50);
                color: white;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4CAF50, stop:1 #388E3C);
                transform: scale(1.03);
            }
            QPushButton:pressed {
                background: #388E3C;
            }
        """)
        
        # Centrar botones perfectamente
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_btn)
        button_layout.addWidget(self.save_btn)
        button_layout.addStretch()
        
        # Agregar todo al layout
        layout.addLayout(header_layout)
        layout.addWidget(self.text_edit)
        layout.addLayout(button_layout)
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(main_widget)
        
        # Conectar señales
        self.save_btn.clicked.connect(self.save_annotation)
        self.cancel_btn.clicked.connect(self.cancel_annotation)
        
        # Atajos de teclado
        self.save_btn.setShortcut("Ctrl+Return")
        self.cancel_btn.setShortcut("Escape")
        
    def on_text_changed(self):
        """Cuando cambia el texto - emitir señal para tiempo real"""
        text = self.text_edit.toPlainText()
        self.text_changed.emit(self.widget_id, text)
        
    def showEvent(self, event):
        """Cuando se muestra el widget, dar focus al texto"""
        super().showEvent(event)
        # Usar QTimer para asegurar que el focus se aplique después de que la ventana esté completamente mostrada
        QTimer.singleShot(100, self.set_text_focus)
        
    def set_text_focus(self):
        """Establecer focus en el campo de texto"""
        self.text_edit.setFocus()
        self.text_edit.activateWindow()
        
    def format_video_time(self, seconds):
        """Formatear tiempo del video en formato legible"""
        total_seconds = int(seconds)
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        if hours > 0:
            return f"⏱️ {hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"⏱️ {minutes:02d}:{seconds:02d}"
        
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            
    def mouseMoveEvent(self, event):
        if self.dragging and event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            
            # ✅ EMITIR posición para actualizar en video
            pos = self.pos()
            self.position_changed.emit(self.widget_id, pos.x(), pos.y())
            
    def mouseReleaseEvent(self, event):
        self.dragging = False
        
    def save_annotation(self):
        text = self.text_edit.toPlainText().strip()
        if text:
            duration = int(time.time() - self.creation_time)
            pos = self.pos()
            # Emitir el tiempo inicial (cuando se hizo clic en anotar), no el tiempo actual
            self.annotation_saved.emit(text, pos.x(), pos.y(), self.video_start_time)
        self.finished.emit()
        self.close()
        
    def cancel_annotation(self):
        """Cancelar anotación → emitir señal para remover del video"""
        self.annotation_cancelled.emit(self.widget_id)
        self.finished.emit()
        self.close()


class VideoRecorder(QThread):
    """Hilo para grabación de video con overlays en tiempo real"""
    
    recording_status = pyqtSignal(str)
    
    def __init__(self, video_source, output_file, main_window):
        super().__init__()
        self.video_source = video_source
        self.output_file = output_file
        self.main_window = main_window
        self.recording = True
        self.annotations = []
        self.active_annotations = []  # Anotaciones que están actualmente visibles
        self.start_time = time.time()
        self.use_direct_capture = hasattr(main_window, 'stream_url') and main_window.stream_url is not None
        
        # ✅ NUEVOS: Sistemas de anotaciones en tiempo real
        self.live_annotations = []    # 📝 Textos en tiempo real (mientras escribe)
        self.saved_annotations = []   # 💾 Textos persistentes (después de guardar)
        
    def add_annotation(self, text, x, y, annotation_time):
        """Agregar anotación que aparecerá en el video"""
        self.annotations.append({
            'text': text,
            'x': x, 'y': y,
            'annotation_time': annotation_time,
            'creation_time': time.time()  # Tiempo real cuando se creó
        })
        
    def annotation_start(self, annotation_time):
        """Marcar que una anotación comenzó a mostrarse"""
        self.active_annotations.append({
            'start_time': time.time(),
            'video_time': annotation_time
        })
        
    def annotation_end(self, text, x, y, annotation_time):
        """Marcar que una anotación terminó y guardar sus datos completos"""
        if self.active_annotations:
            active = self.active_annotations.pop()
            self.annotations.append({
                'text': text,
                'x': x, 'y': y,
                'start_time': active['start_time'],
                'end_time': time.time(),
                'video_time': annotation_time
            })
    
    def add_live_annotation(self, widget_id, start_time, initial_x, initial_y):
        """Agregar anotación en tiempo real"""
        # Convertir coordenadas UI a stream
        stream_x, stream_y = self.main_window.ui_to_stream_coordinates(initial_x, initial_y)
        
        self.live_annotations.append({
            'widget_id': widget_id,
            'text': '',  # Inicialmente vacío
            'x': stream_x, 'y': stream_y,
            'start_time': start_time,
            'active': True
        })
    
    def update_live_text(self, widget_id, text):
        """Actualizar texto en tiempo real"""
        for annotation in self.live_annotations:
            if annotation['widget_id'] == widget_id:
                annotation['text'] = text
                break
    
    def update_live_position(self, widget_id, ui_x, ui_y):
        """Actualizar posición en tiempo real"""
        stream_x, stream_y = self.main_window.ui_to_stream_coordinates(ui_x, ui_y)
        
        for annotation in self.live_annotations:
            if annotation['widget_id'] == widget_id:
                annotation['x'] = stream_x
                annotation['y'] = stream_y
                break
    
    def save_live_annotation(self, widget_id, text, ui_x, ui_y, annotation_time):
        """Convertir anotación live a persistente"""
        # Remover de live
        live_annotation = None
        for i, ann in enumerate(self.live_annotations):
            if ann['widget_id'] == widget_id:
                live_annotation = self.live_annotations.pop(i)
                break
        
        # Agregar a persistentes (5 segundos más)
        if live_annotation and text.strip():
            stream_x, stream_y = self.main_window.ui_to_stream_coordinates(ui_x, ui_y)
            self.saved_annotations.append({
                'text': text,
                'x': stream_x, 'y': stream_y,
                'start_time': time.time(),
                'end_time': time.time() + 5,  # ✅ 5 segundos más
                'active': True
            })
    
    def cancel_live_annotation(self, widget_id):
        """Cancelar anotación → desaparece inmediatamente"""
        self.live_annotations = [
            ann for ann in self.live_annotations 
            if ann['widget_id'] != widget_id
        ]
        
    def run(self):
        """Grabación directa del stream de video o captura de pantalla como fallback"""
        try:
            # Crear directorio de videos si no existe
            videos_dir = "videos_grabados"
            os.makedirs(videos_dir, exist_ok=True)
            full_path = os.path.join(videos_dir, self.output_file)
            
            if self.use_direct_capture:
                self._record_direct_stream(full_path)
            else:
                self._record_screen_capture(full_path)
                
        except Exception as e:
            self.recording_status.emit(f"❌ Error grabando: {str(e)}")
    
    def _record_direct_stream(self, full_path):
        """Grabación directa desde el stream de la cámara IP con optimizaciones de baja latencia"""
        self.recording_status.emit("🔴 Grabando directamente desde stream de cámara...")
        
        # ✅ CONECTAR CON OPTIMIZACIONES ULTRA DE BAJA LATENCIA
        cap = cv2.VideoCapture(self.main_window.stream_url, cv2.CAP_FFMPEG)
        
        # Aplicar configuraciones ultra optimizadas
        cap = apply_opencv_ultra_low_latency(cap)
        
        # Inicializar monitor de latencia para grabación
        self.latency_monitor = LatencyMonitor()
        
        print("🚀 Grabación configurada con optimizaciones ultra de baja latencia")
        
        if not cap.isOpened():
            self.recording_status.emit("❌ Error: No se pudo conectar al stream para grabación")
            return
            
        # Obtener propiedades del video con valores seguros
        fps = int(cap.get(cv2.CAP_PROP_FPS)) or 30  # Default 30 fps (mejor que 25)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) or 1920
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) or 1080
        
        # ✅ FORZAR CONFIGURACIONES ESPECÍFICAS
        cap.set(cv2.CAP_PROP_FPS, fps)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        
        self.recording_status.emit(f"📹 Stream detectado: {width}x{height} @ {fps}fps")
        
        # ✅ CONFIGURAR GRABADOR CON CÓDEC OPTIMIZADO
        # Probar H264 primero, fallback a mp4v
        fourcc = cv2.VideoWriter_fourcc(*'H264')
        out = cv2.VideoWriter(full_path, fourcc, fps, (width, height))
        
        if not out.isOpened():
            # Fallback a mp4v
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(full_path, fourcc, fps, (width, height))
            
        frame_count = 0
        dropped_frames = 0
        last_status_time = time.time()
        last_frame_time = time.time()
        
        while self.recording and cap.isOpened():
            current_time = time.time()
            ret, frame = cap.read()
            
            if not ret:
                dropped_frames += 1
                if dropped_frames > 60:  # Si perdemos muchos frames consecutivos
                    self.recording_status.emit("❌ Error: Demasiados frames perdidos")
                    break
                time.sleep(0.01)  # Espera corta antes de reintentar
                continue
            else:
                dropped_frames = 0  # Reset contador si leemos correctamente
                
            # ✅ CONTROL DE LATENCIA: Descartar frames demasiado frecuentes
            frame_interval = 1.0 / fps
            if current_time - last_frame_time < frame_interval * 0.8:  # 80% del intervalo
                continue  # Saltar este frame para mantener la velocidad
            last_frame_time = current_time
                
            # Agregar anotaciones activas al frame (tiempo real + persistentes)
            frame_with_annotations = self._add_live_annotations_to_frame(frame)
            
            # Escribir frame al archivo
            out.write(frame_with_annotations)
            frame_count += 1
            
            # Actualizar status cada 3 segundos (más frecuente)
            if time.time() - last_status_time > 3:
                duration = time.time() - self.start_time
                latency_ms = int((time.time() - current_time) * 1000)
                self.recording_status.emit(
                    f"🔴 Grabando: {frame_count} frames ({duration:.1f}s) | Latencia: {latency_ms}ms"
                )
                last_status_time = time.time()
        
        # Limpiar recursos
        cap.release()
        out.release()
        
        # Verificar resultado
        if os.path.exists(full_path) and os.path.getsize(full_path) > 0:
            file_size = os.path.getsize(full_path) / (1024 * 1024)  # MB
            duration = time.time() - self.start_time
            self.recording_status.emit(f"✅ Video MP4 guardado: {full_path}")
            self.recording_status.emit(f"📊 {frame_count} frames, {file_size:.1f} MB, {duration:.1f}s")
        else:
            self.recording_status.emit("❌ Error: No se pudo crear el archivo MP4")
    
    def _record_screen_capture(self, full_path):
        """Grabación por captura de pantalla (modo fallback)"""
        self.recording_status.emit("🔴 Grabando por captura de pantalla...")
        
        fps = 10
        frame_count = 0
        
        # Configurar MP4 con codec compatible
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        
        # Obtener dimensiones reales del video frame
        video_frame = self.main_window.video_frame
        video_rect = video_frame.geometry()
        width, height = video_rect.width(), video_rect.height()
        
        out = cv2.VideoWriter(full_path, fourcc, fps, (width, height))
        
        while self.recording:
            try:
                # Capturar EXACTAMENTE lo que se ve en el video frame
                video_global_pos = video_frame.mapToGlobal(video_frame.rect().topLeft())
                
                # Capturar solo el área real del video frame
                screenshot = ImageGrab.grab(bbox=(
                    video_global_pos.x(),
                    video_global_pos.y(),
                    video_global_pos.x() + width,
                    video_global_pos.y() + height
                ))
                
                # Convertir a OpenCV format
                frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
                
                out.write(frame)
                frame_count += 1
                
                time.sleep(1/fps)
                
            except Exception as frame_error:
                # Si falla la captura, crear frame negro
                frame = np.zeros((height, width, 3), dtype=np.uint8)
                out.write(frame)
                frame_count += 1
                time.sleep(1/fps)
            
        # Finalizar grabación
        out.release()
        
        # Verificar que el archivo existe
        if os.path.exists(full_path) and os.path.getsize(full_path) > 0:
            file_size = os.path.getsize(full_path) / (1024 * 1024)  # MB
            self.recording_status.emit(f"✅ Video MP4 guardado: {full_path}")
            self.recording_status.emit(f"📊 {frame_count} frames, {file_size:.1f} MB")
        else:
            self.recording_status.emit("❌ Error: No se pudo crear el archivo MP4")
    
    def _add_annotations_to_frame(self, frame):
        """Agregar anotaciones activas al frame de video (sistema antiguo)"""
        if not self.annotations:
            return frame
            
        frame_copy = frame.copy()
        current_time = time.time() - self.start_time
        
        # Dibujar anotaciones que deben estar visibles
        for annotation in self.annotations:
            if annotation.get('start_time', 0) <= current_time <= annotation.get('end_time', current_time + 5):
                text = annotation['text']
                x = int(annotation.get('x', 50))
                y = int(annotation.get('y', 50))
                
                # Configurar texto
                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = 0.8
                color = (0, 255, 0)  # Verde
                thickness = 2
                
                # Fondo semi-transparente para el texto
                text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
                cv2.rectangle(frame_copy, 
                            (x-5, y-text_size[1]-10), 
                            (x+text_size[0]+5, y+5), 
                            (0, 0, 0), -1)
                
                # Texto
                cv2.putText(frame_copy, text, (x, y), font, font_scale, color, thickness)
        
        return frame_copy
    
    def _add_live_annotations_to_frame(self, frame):
        """Agregar anotaciones en tiempo real al frame"""
        frame_copy = frame.copy()
        current_time = time.time()
        
        # ✅ 1. DIBUJAR ANOTACIONES EN TIEMPO REAL (mientras escribe)
        for annotation in self.live_annotations:
            if annotation['active'] and annotation['text'].strip():
                text = annotation['text']
                x, y = int(annotation['x']), int(annotation['y'])
                
                # Asegurar que las coordenadas estén dentro del frame
                if x < 0 or y < 0 or x > frame.shape[1] - 50 or y > frame.shape[0] - 20:
                    continue
                
                # Estilo "en vivo" - borde parpadeante
                pulse = int((current_time * 4) % 2)
                border_color = (0, 255, 255) if pulse else (255, 255, 0)  # Amarillo parpadeante
                
                # Fondo con borde especial
                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = 0.7
                thickness = 2
                text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
                
                # Verificar que no se salga del frame
                if x + text_size[0] + 8 > frame.shape[1]:
                    x = frame.shape[1] - text_size[0] - 8
                if y - text_size[1] - 8 < 0:
                    y = text_size[1] + 8
                
                cv2.rectangle(frame_copy, (x-8, y-text_size[1]-8), 
                             (x+text_size[0]+8, y+8), border_color, 2)  # Borde
                cv2.rectangle(frame_copy, (x-5, y-text_size[1]-5), 
                             (x+text_size[0]+5, y+5), (0,0,0), -1)  # Fondo negro
                
                # Texto en tiempo real
                cv2.putText(frame_copy, text, (x, y), font, font_scale, (255, 255, 255), thickness)  # Blanco
        
        # ✅ 2. DIBUJAR ANOTACIONES PERSISTENTES (después de guardar)
        for annotation in self.saved_annotations:
            if annotation['start_time'] <= current_time <= annotation['end_time']:
                text = annotation['text']
                x, y = int(annotation['x']), int(annotation['y'])
                
                # Asegurar que las coordenadas estén dentro del frame
                if x < 0 or y < 0 or x > frame.shape[1] - 50 or y > frame.shape[0] - 20:
                    continue
                
                # Estilo "guardado" - sólido y verde
                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = 0.8
                thickness = 2
                text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
                
                # Verificar que no se salga del frame
                if x + text_size[0] + 5 > frame.shape[1]:
                    x = frame.shape[1] - text_size[0] - 5
                if y - text_size[1] - 5 < 0:
                    y = text_size[1] + 5
                
                cv2.rectangle(frame_copy, (x-5, y-text_size[1]-5), 
                             (x+text_size[0]+5, y+5), (0,0,0), -1)  # Fondo negro
                
                # Texto persistente
                cv2.putText(frame_copy, text, (x, y), font, font_scale, (0, 255, 0), thickness)  # Verde
        
        return frame_copy

        
    def stop_recording(self):
        self.recording = False


class CameraIPViewer(QMainWindow):
    """Aplicación principal para visualizar cámara IP"""
    
    def __init__(self):
        super().__init__()
        self.vlc_instance = None
        self.vlc_player = None
        self.recorder = None
        self.annotations_log = []
        self.recording_start_time = None
        self.stream_url = None  # URL del stream de la cámara IP
        self.active_annotation_widgets = []  # Lista de widgets activos
        self.stream_width = 1920  # Ancho por defecto del stream
        self.stream_height = 1080  # Alto por defecto del stream
        self.connection_thread = None  # Hilo para pruebas de conexión
        
        self.setup_ui()
        self.setup_connections()
        
    def setup_ui(self):
        """Configurar interfaz de usuario"""
        self.setWindowTitle("📹 Visor de Cámara IP Profesional")
        self.setGeometry(100, 100, 1400, 900)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QHBoxLayout(central_widget)
        
        # Panel izquierdo - Controles
        left_panel = self.create_control_panel()
        
        # Panel derecho - Video y anotaciones
        right_panel = self.create_video_panel()
        
        # Splitter para redimensionar
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([400, 1000])
        
        main_layout.addWidget(splitter)
        
    def create_control_panel(self):
        """Crear panel de controles"""
        panel = QFrame()
        panel.setMaximumWidth(400)
        panel.setStyleSheet("QFrame { background: #2b2b2b; border-radius: 10px; }")
        
        layout = QVBoxLayout(panel)
        
        # === CONEXIÓN ===
        connection_group = QGroupBox("🔗 Conexión a Cámara IP")
        connection_group.setStyleSheet("QGroupBox { font-weight: bold; color: #4CAF50; }")
        conn_layout = QGridLayout(connection_group)
        
        # Campos de conexión
        conn_layout.addWidget(QLabel("📡 Dirección IP:"), 0, 0)
        self.ip_input = QLineEdit("192.168.18.25")
        self.ip_input.setPlaceholderText("ej: 192.168.18.25")
        conn_layout.addWidget(self.ip_input, 0, 1)
        
        conn_layout.addWidget(QLabel("👤 Usuario:"), 1, 0)
        self.user_input = QLineEdit("admin")
        conn_layout.addWidget(self.user_input, 1, 1)
        
        conn_layout.addWidget(QLabel("🔒 Contraseña:"), 2, 0)
        
        # Layout horizontal para contraseña + botón de mostrar/ocultar
        password_layout = QHBoxLayout()
        self.pass_input = QLineEdit("Prototipo")
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pass_input.setPlaceholderText("Ingrese la contraseña")
        
        # Botón para mostrar/ocultar contraseña
        self.show_pass_btn = QPushButton("👁️")
        self.show_pass_btn.setMaximumWidth(40)
        self.show_pass_btn.setToolTip("Mostrar/Ocultar contraseña")
        self.show_pass_btn.setStyleSheet("""
            QPushButton {
                background: #555;
                border: 1px solid #777;
                border-radius: 4px;
                padding: 5px;
                color: white;
            }
            QPushButton:hover { background: #666; }
            QPushButton:pressed { background: #444; }
        """)
        
        password_layout.addWidget(self.pass_input)
        password_layout.addWidget(self.show_pass_btn)
        password_layout.setContentsMargins(0, 0, 0, 0)
        
        password_widget = QWidget()
        password_widget.setLayout(password_layout)
        conn_layout.addWidget(password_widget, 2, 1)
        
        # Botones de conexión/desconexión
        buttons_layout = QHBoxLayout()
        
        self.connect_btn = QPushButton("🚀 CONECTAR")
        self.connect_btn.setStyleSheet("""
            QPushButton {
                background: #4CAF50;
                color: white;
                border: none;
                padding: 12px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover { background: #45a049; }
        """)
        
        self.disconnect_btn = QPushButton("🔌 DESCONECTAR")
        self.disconnect_btn.setStyleSheet("""
            QPushButton {
                background: #FF5722;
                color: white;
                border: none;
                padding: 12px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover { background: #E64A19; }
        """)
        self.disconnect_btn.setEnabled(False)  # Inicialmente deshabilitado
        
        buttons_layout.addWidget(self.connect_btn)
        buttons_layout.addWidget(self.disconnect_btn)
        buttons_layout.setSpacing(10)
        
        buttons_widget = QWidget()
        buttons_widget.setLayout(buttons_layout)
        conn_layout.addWidget(buttons_widget, 3, 0, 1, 2)
        
        # Estado de conexión
        self.connection_status = QLabel("❌ Desconectado")
        self.connection_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        conn_layout.addWidget(self.connection_status, 4, 0, 1, 2)
        
        # Información del stream
        self.stream_info = QLabel("💡 Configuración: rtsp://admin:Prototipo@192.168.18.25:554/Streaming/Channels/101")
        self.stream_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.stream_info.setStyleSheet("color: #9E9E9E; font-size: 10px;")
        self.stream_info.setWordWrap(True)
        conn_layout.addWidget(self.stream_info, 5, 0, 1, 2)
        
        # Panel de progreso simplificado
        self.progress_panel = QFrame()
        self.progress_panel.setStyleSheet("QFrame { background: #333; border-radius: 5px; padding: 5px; }")
        self.progress_panel.setMaximumHeight(80)
        self.progress_panel.setVisible(False)
        
        progress_layout = QVBoxLayout(self.progress_panel)
        progress_layout.setSpacing(2)
        
        # Título del progreso
        progress_title = QLabel("🔍 Conectando a cámara IP:")
        progress_title.setStyleSheet("color: #FFA726; font-weight: bold; font-size: 11px;")
        progress_layout.addWidget(progress_title)
        
        # Estado de conexión única
        self.url_status_labels = []
        url_label = QLabel("")
        url_label.setStyleSheet("color: #9E9E9E; font-size: 9px; font-family: monospace;")
        url_label.setVisible(False)
        progress_layout.addWidget(url_label)
        self.url_status_labels.append(url_label)
        
        conn_layout.addWidget(self.progress_panel, 6, 0, 1, 2)
        
        # === GRABACIÓN ===
        recording_group = QGroupBox("🎬 Grabación")
        recording_group.setStyleSheet("QGroupBox { font-weight: bold; color: #FF9800; }")
        rec_layout = QVBoxLayout(recording_group)
        
        # Botones de grabación
        self.record_btn = QPushButton("🔴 INICIAR GRABACIÓN")
        self.record_btn.setStyleSheet("""
            QPushButton {
                background: #f44336;
                color: white;
                border: none;
                padding: 12px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover { background: #da190b; }
        """)
        
        self.stop_record_btn = QPushButton("⏹️ DETENER Y GUARDAR")
        self.stop_record_btn.setStyleSheet("""
            QPushButton {
                background: #795548;
                color: white;
                border: none;
                padding: 12px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover { background: #5d4037; }
        """)
        self.stop_record_btn.setEnabled(False)
        
        rec_layout.addWidget(self.record_btn)
        rec_layout.addWidget(self.stop_record_btn)
        
        # Estado de grabación
        self.recording_status = QLabel("⚪ No grabando")
        self.recording_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        rec_layout.addWidget(self.recording_status)
        
        # === ANOTACIONES ===
        annotation_group = QGroupBox("✏️ Anotaciones")
        annotation_group.setStyleSheet("QGroupBox { font-weight: bold; color: #2196F3; }")
        ann_layout = QVBoxLayout(annotation_group)
        
        self.annotate_btn = QPushButton("📝 ANOTAR")
        self.annotate_btn.setStyleSheet("""
            QPushButton {
                background: #2196F3;
                color: white;
                border: none;
                padding: 12px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover { background: #1976D2; }
        """)
        ann_layout.addWidget(self.annotate_btn)
        
        # Lista de anotaciones
        self.annotations_list = QListWidget()
        self.annotations_list.setMaximumHeight(200)
        ann_layout.addWidget(QLabel("📋 Historial:"))
        ann_layout.addWidget(self.annotations_list)
        
        # === TIEMPO ===
        time_group = QGroupBox("⏰ Tiempo")
        time_group.setStyleSheet("QGroupBox { font-weight: bold; color: #9C27B0; }")
        time_layout = QVBoxLayout(time_group)
        
        self.time_label = QLabel("00:00:00")
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #9C27B0;")
        time_layout.addWidget(self.time_label)
        
        # Agregar grupos al layout
        layout.addWidget(connection_group)
        layout.addWidget(recording_group)
        layout.addWidget(annotation_group)
        layout.addWidget(time_group)
        layout.addStretch()
        
        return panel
        
    def create_video_panel(self):
        """Crear panel de video"""
        panel = QFrame()
        panel.setStyleSheet("QFrame { background: #1e1e1e; border-radius: 10px; }")
        
        layout = QVBoxLayout(panel)
        
        # Título
        title = QLabel("📹 Transmisión de Cámara IP")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: white; padding: 10px;")
        layout.addWidget(title)
        
        # Área de video
        self.video_frame = QFrame()
        self.video_frame.setMinimumSize(800, 600)
        self.video_frame.setStyleSheet("QFrame { background: black; border: 2px solid #4CAF50; }")
        layout.addWidget(self.video_frame)
        
        # Controles de video
        controls_layout = QHBoxLayout()
        
        self.play_btn = QPushButton("▶️")
        self.pause_btn = QPushButton("⏸️")
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)
        
        controls_layout.addWidget(QLabel("Control:"))
        controls_layout.addWidget(self.play_btn)
        controls_layout.addWidget(self.pause_btn)
        controls_layout.addWidget(QLabel("🔊"))
        controls_layout.addWidget(self.volume_slider)
        controls_layout.addStretch()
        
        layout.addLayout(controls_layout)
        
        return panel
        
    def setup_connections(self):
        """Configurar conexiones de señales"""
        self.connect_btn.clicked.connect(self.connect_to_camera)
        self.disconnect_btn.clicked.connect(self.disconnect_from_camera)
        self.show_pass_btn.clicked.connect(self.toggle_password_visibility)
        self.record_btn.clicked.connect(self.start_recording)
        self.stop_record_btn.clicked.connect(self.stop_recording)
        self.annotate_btn.clicked.connect(self.create_annotation)
        
        # Timer para actualizar tiempo
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)  # Actualizar cada segundo
        
    def connect_to_camera(self):
        """Conectar a la cámara IP usando hilo separado"""
        # Verificar si ya está conectado
        if self.stream_url and self.vlc_player:
            QMessageBox.warning(self, "Ya Conectado", 
                              "Ya hay una conexión activa.\n\n"
                              "Use el botón 'DESCONECTAR' primero si desea cambiar de cámara.")
            return
        
        # Verificar si ya hay una prueba de conexión en curso
        if self.connection_thread and self.connection_thread.isRunning():
            QMessageBox.warning(self, "Conexión en Proceso", 
                              "Ya hay una prueba de conexión en curso.\n\n"
                              "Espere a que termine o presione 'DESCONECTAR' para cancelar.")
            return
        
        ip = self.ip_input.text().strip()
        user = self.user_input.text().strip()
        password = self.pass_input.text()
        
        if not all([ip, user, password]):
            QMessageBox.warning(self, "Campos Incompletos", 
                              "Por favor complete todos los campos:\n\n"
                              "• Dirección IP\n"
                              "• Usuario\n" 
                              "• Contraseña")
            return
        
        # URL específica para esta cámara IP
        possible_urls = [
            f"rtsp://{user}:{password}@{ip}:554/Streaming/Channels/101"
        ]
        
        # Iniciar prueba de conexión en hilo separado
        self.connection_thread = ConnectionTestThread(possible_urls)
        self.connection_thread.progress_update.connect(self.update_connection_progress)
        self.connection_thread.url_test_start.connect(self.show_url_test_start)
        self.connection_thread.url_test_result.connect(self.show_url_test_result)
        self.connection_thread.connection_result.connect(self.handle_connection_result)
        
        # Actualizar UI para mostrar que está probando
        self.connect_btn.setText("⏹️ CANCELAR")
        self.connect_btn.setStyleSheet("""
            QPushButton {
                background: #FF9800;
                color: white;
                border: none;
                padding: 12px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover { background: #F57C00; }
        """)
        self.connection_status.setText("🔄 Probando conexión...")
        self.connection_status.setStyleSheet("color: #FF9800; font-weight: bold;")
        
        # Mostrar panel de progreso
        self.progress_panel.setVisible(True)
        if self.url_status_labels:
            self.url_status_labels[0].setVisible(False)
            self.url_status_labels[0].setText("")
        
        # Reconectar el botón para cancelar
        self.connect_btn.clicked.disconnect()
        self.connect_btn.clicked.connect(self.cancel_connection)
        
        # Iniciar prueba
        self.connection_thread.start()
    
    def update_connection_progress(self, message):
        """Actualizar progreso de la conexión"""
        self.recording_status.setText(message)
    
    def show_url_test_start(self, index, url_display, url_type):
        """Mostrar que se está probando una URL específica"""
        if index < len(self.url_status_labels):
            label = self.url_status_labels[index]
            label.setText(f"🔄 [{index+1}] {url_type}: {url_display}")
            label.setStyleSheet("color: #FF9800; font-size: 9px; font-family: monospace; font-weight: bold;")
            label.setVisible(True)
        
        # Actualizar mensaje principal
        self.recording_status.setText(f"🔍 Conectando: {url_type}")
    
    def show_url_test_result(self, index, success, message, elapsed_time):
        """Mostrar el resultado de la prueba de una URL"""
        if index < len(self.url_status_labels):
            label = self.url_status_labels[index]
            time_str = f"({elapsed_time:.1f}s)"
            
            if success:
                label.setText(f"✅ {message} {time_str}")
                label.setStyleSheet("color: #4CAF50; font-size: 9px; font-family: monospace; font-weight: bold;")
                # Si esta URL funcionó, resaltar que fue la exitosa
                self.recording_status.setText(f"✅ CONEXIÓN EXITOSA: {message}")
            else:
                label.setText(f"❌ {message} {time_str}")
                label.setStyleSheet("color: #F44336; font-size: 9px; font-family: monospace;")
            
            label.setVisible(True)
    
    def handle_connection_result(self, success, url, width, height):
        """Manejar resultado de la prueba de conexión"""
        # Restaurar botón conectar
        self.restore_connect_button()
        
        if success:
            # ✅ Conexión exitosa
            self.stream_url = url
            self.stream_width = width
            self.stream_height = height
            
            # Ocultar panel de progreso después de éxito
            QTimer.singleShot(2000, lambda: self.progress_panel.setVisible(False))
            
            self.setup_vlc_player()
        else:
            # ❌ Ninguna URL funcionó
            ip = self.ip_input.text().strip()
            user = self.user_input.text().strip()
            
            # Mantener panel de progreso visible para ver qué falló
            QMessageBox.critical(self, "Error de Conexión", 
                               f"No se pudo conectar a la cámara IP:\n\n"
                               f"📡 IP: {ip}\n"
                               f"👤 Usuario: {user}\n\n"
                               f"❌ No se pudo conectar a la cámara\n\n"
                               f"💡 Sugerencias:\n"
                               f"• Verifique que la IP 192.168.18.25 sea correcta\n"
                               f"• Confirme que las credenciales admin:Prototipo sean válidas\n"
                               f"• Asegúrese que esté en la misma red\n"
                               f"• Verifique que la cámara esté encendida\n"
                               f"• Confirme que el canal 101 esté disponible\n\n"
                               f"📋 Revise el panel de estado para ver detalles específicos")
            
            self.connection_status.setText("❌ Error de conexión")
            self.connection_status.setStyleSheet("color: #f44336; font-weight: bold;")
            self.recording_status.setText("❌ No se pudo conectar a ninguna URL")
    
    def setup_vlc_player(self):
        """Configurar VLC player optimizado para baja latencia"""
        self.video_frame.setText("🔗 Conectando al stream...")
        
        # ✅ USAR CONFIGURACIÓN ULTRA OPTIMIZADA DE BAJA LATENCIA
        vlc_args = VLC_ULTRA_LOW_LATENCY_ARGS.copy()
        
        # Inicializar monitor de latencia
        self.latency_monitor = LatencyMonitor()
        
        print("🚀 Usando configuración ULTRA de baja latencia para VLC")
        print(f"📊 Parámetros VLC: {len(vlc_args)} opciones de optimización")
        
        # Crear instancia VLC con configuración optimizada
        self.vlc_instance = vlc.Instance(vlc_args)
        self.vlc_player = self.vlc_instance.media_player_new()
        
        # Configurar el widget de video para VLC
        if sys.platform.startswith('linux'):
            self.vlc_player.set_xwindow(int(self.video_frame.winId()))
        elif sys.platform == "win32":
            self.vlc_player.set_hwnd(int(self.video_frame.winId()))
        elif sys.platform == "darwin":
            self.vlc_player.set_nsobject(int(self.video_frame.winId()))
        
        # ✅ CONFIGURAR MEDIA CON OPCIONES ADICIONALES DE BAJA LATENCIA
        media = self.vlc_instance.media_new(self.stream_url)
        
        # Opciones adicionales de red para RTSP
        media.add_option(':network-caching=50')
        media.add_option(':live-caching=50') 
        media.add_option(':rtsp-tcp')
        media.add_option(':no-audio')
        media.add_option(':avcodec-skiploopfilter=4')
        media.add_option(':drop-late-frames')
        media.add_option(':avcodec-fast')
        
        self.vlc_player.set_media(media)
        
        # Configurar eventos del reproductor
        event_manager = self.vlc_player.event_manager()
        event_manager.event_attach(vlc.EventType.MediaPlayerEndReached, self.on_vlc_end_reached)
        event_manager.event_attach(vlc.EventType.MediaPlayerEncounteredError, self.on_vlc_error)
        
        # Iniciar reproducción
        self.vlc_player.play()
        
        # Timer para actualizar el tiempo del video
        self.video_timer = QTimer()
        self.video_timer.timeout.connect(self.update_time)
        self.video_timer.start(100)  # Actualizar cada 100ms
        
        print("✅ VLC Player configurado con optimizaciones de baja latencia")
    
    def on_vlc_end_reached(self, event):
        """Manejar evento de finalización de reproducción"""
        print("🎬 VLC Player finalizado")
    
    def on_vlc_error(self, event):
        """Manejar evento de error en reproducción"""
        error_code = event.event_data()
        print(f"❌ VLC Player error: {error_code}")
    
    def cancel_connection(self):
        """Cancelar prueba de conexión en curso"""
        if self.connection_thread and self.connection_thread.isRunning():
            self.connection_thread.stop()
            self.connection_thread.wait(3000)  # Esperar máximo 3 segundos
            
        self.restore_connect_button()
        self.progress_panel.setVisible(False)  # Ocultar panel de progreso
        self.connection_status.setText("❌ Conexión cancelada")
        self.connection_status.setStyleSheet("color: #9E9E9E; font-weight: bold;")
        self.recording_status.setText("⚪ Listo para conectar")
    
    def restore_connect_button(self):
        """Restaurar botón conectar a su estado original"""
        self.connect_btn.setText("🚀 CONECTAR")
        self.connect_btn.setStyleSheet("""
            QPushButton {
                background: #4CAF50;
                color: white;
                border: none;
                padding: 12px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover { background: #45a049; }
        """)
        self.connect_btn.setEnabled(True)
        
        # Reconectar a la función original
        self.connect_btn.clicked.disconnect()
        self.connect_btn.clicked.connect(self.connect_to_camera)
    
    def disconnect_from_camera(self):
        """Desconectar de la cámara IP"""
        try:
            # Detener hilo de conexión si está corriendo
            if self.connection_thread and self.connection_thread.isRunning():
                self.connection_thread.stop()
                self.connection_thread.wait(3000)  # Esperar máximo 3 segundos
            
            # Detener grabación si está activa
            if self.recorder and self.recorder.isRunning():
                self.stop_recording()
            
            # Detener reproductor VLC
            if self.vlc_player:
                self.vlc_player.stop()
                self.vlc_player.release()
                self.vlc_player = None
            
            if self.vlc_instance:
                self.vlc_instance.release()
                self.vlc_instance = None
            
            # Limpiar variables
            self.stream_url = None
            self.stream_width = 1920
            self.stream_height = 1080
            
            # Restaurar botón conectar si estaba en modo cancelar
            self.restore_connect_button()
            
            # Actualizar interfaz
            self.progress_panel.setVisible(False)  # Ocultar panel de progreso
            self.connection_status.setText("❌ Desconectado")
            self.connection_status.setStyleSheet("color: #9E9E9E; font-weight: bold;")
            self.stream_info.setText("💡 Configuración: rtsp://admin:Prototipo@192.168.18.5:554/Streaming/Channels/101")
            self.stream_info.setStyleSheet("color: #9E9E9E; font-size: 10px;")
            self.recording_status.setText("⚪ Listo para conectar")
            
            # Actualizar estado de botones
            self.disconnect_btn.setEnabled(False)
            
            QMessageBox.information(self, "Desconexión", "🔌 Desconectado exitosamente\n\nYa puedes conectar a otra cámara IP")
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error al desconectar: {str(e)}")
    
    def toggle_password_visibility(self):
        """Alternar visibilidad de la contraseña"""
        if self.pass_input.echoMode() == QLineEdit.EchoMode.Password:
            # Mostrar contraseña
            self.pass_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.show_pass_btn.setText("🙈")
            self.show_pass_btn.setToolTip("Ocultar contraseña")
        else:
            # Ocultar contraseña
            self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.show_pass_btn.setText("👁️")
            self.show_pass_btn.setToolTip("Mostrar contraseña")
            
    def start_recording(self):
        """Iniciar grabación"""
        # Permitir grabar sin conexión para testing
        # if not self.vlc_player:
        #     QMessageBox.warning(self, "Error", "Primero conecte a una cámara")
        #     return
            
        # Crear directorio de videos
        videos_dir = "videos_grabados"
        os.makedirs(videos_dir, exist_ok=True)
        
        # Nombre con timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"camara_ip_{timestamp}.mp4"
        
        self.recorder = VideoRecorder("camera_stream", output_file, self)
        self.recorder.recording_status.connect(self.update_recording_status)
        self.recorder.start()
        
        self.recording_start_time = time.time()
        self.record_btn.setEnabled(False)
        self.stop_record_btn.setEnabled(True)
        self.recording_status.setText("🔴 GRABANDO...")
        self.recording_status.setStyleSheet("color: #f44336; font-weight: bold;")
        
    def stop_recording(self):
        """Detener grabación"""
        if self.recorder:
            self.recorder.stop_recording()
            self.recorder.wait()
            
        self.record_btn.setEnabled(True)
        self.stop_record_btn.setEnabled(False)
        self.recording_status.setText("✅ Grabación guardada")
        self.recording_status.setStyleSheet("color: #4CAF50; font-weight: bold;")
    
    def ui_to_stream_coordinates(self, ui_x, ui_y):
        """Convertir coordenadas de UI a coordenadas del stream"""
        # Obtener dimensiones del widget de video en UI
        video_widget_rect = self.video_frame.geometry()
        ui_width = video_widget_rect.width()
        ui_height = video_widget_rect.height()
        
        # Convertir coordenadas proporcionalmente
        stream_x = int((ui_x / ui_width) * self.stream_width) if ui_width > 0 else 0
        stream_y = int((ui_y / ui_height) * self.stream_height) if ui_height > 0 else 0
        
        # Asegurar que estén dentro de los límites
        stream_x = max(0, min(stream_x, self.stream_width - 1))
        stream_y = max(0, min(stream_y, self.stream_height - 1))
        
        return stream_x, stream_y
    
    def remove_annotation_widget(self, widget):
        """Remover widget de la lista activa"""
        if widget in self.active_annotation_widgets:
            self.active_annotation_widgets.remove(widget)
        
    def create_annotation(self):
        """Crear widget de anotación con tracking en tiempo real"""
        # Obtener tiempo actual del video
        current_video_time = self.get_current_video_time()
        
        annotation_widget = MovableAnnotationWidget(self, current_video_time)
        
        # ✅ ASIGNAR ID único al widget
        widget_id = len(self.active_annotation_widgets)
        annotation_widget.widget_id = widget_id
        
        # Agregar a lista de widgets activos
        self.active_annotation_widgets.append(annotation_widget)
        
        # Posicionar perfectamente centrado en el área de video
        video_center = self.video_frame.rect().center()
        video_global_center = self.video_frame.mapToGlobal(video_center)
        
        widget_x = video_global_center.x() - annotation_widget.width() // 2
        widget_y = video_global_center.y() - annotation_widget.height() // 2
        
        annotation_widget.move(widget_x, widget_y)
        
        # ✅ CONECTAR todas las señales para tiempo real
        if self.recorder and self.recorder.isRunning():
            # Agregar anotación live inicial
            self.recorder.add_live_annotation(widget_id, current_video_time, widget_x, widget_y)
            
            # Conectar cambios de texto en tiempo real
            annotation_widget.text_changed.connect(
                lambda widget_id, text: self.recorder.update_live_text(widget_id, text)
            )
            
            # Conectar movimientos en tiempo real
            annotation_widget.position_changed.connect(
                lambda widget_id, x, y: self.recorder.update_live_position(widget_id, x, y)
            )
            
            # Conectar guardar (persistencia)
            annotation_widget.annotation_saved.connect(
                lambda text, x, y, time: self.recorder.save_live_annotation(
                    widget_id, text, x, y, time
                )
            )
            
            # Conectar cancelar
            annotation_widget.annotation_cancelled.connect(
                lambda widget_id: self.recorder.cancel_live_annotation(widget_id)
            )
        
        # Conectar para limpieza
        annotation_widget.annotation_saved.connect(self.save_annotation)
        annotation_widget.finished.connect(lambda: self.remove_annotation_widget(annotation_widget))
        
        # Mostrar widget
        annotation_widget.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        annotation_widget.show()
        annotation_widget.raise_()
        annotation_widget.activateWindow()
        
    def save_annotation(self, text, x, y, annotation_time):
        """Guardar anotación en el log"""
        annotation = {
            'text': text,
            'time': annotation_time,  # Usar el tiempo cuando se hizo clic en anotar
            'position': (x, y),
            'duration': 0,  # Duración ya no es relevante con tiempo fijo
            'timestamp': datetime.now()
        }
        
        self.annotations_log.append(annotation)
        
        # Agregar a la lista visual
        time_str = self.format_time(annotation_time)
        list_item = f"[{time_str}] {text[:30]}..."
        self.annotations_list.addItem(list_item)
        
        # Si está grabando, marcar final de anotación
        if self.recorder and self.recorder.isRunning():
            self.recorder.annotation_end(text, x, y, annotation_time)
            
    def get_current_video_time(self):
        """Obtener tiempo actual del video"""
        if self.recording_start_time:
            return time.time() - self.recording_start_time
        return 0
        
    def format_time(self, seconds):
        """Formatear tiempo en HH:MM:SS"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        
    def update_time(self):
        """Actualizar display de tiempo"""
        current_time = self.get_current_video_time()
        self.time_label.setText(self.format_time(current_time))
        
    def update_recording_status(self, status):
        """Actualizar estado de grabación"""
        self.recording_status.setText(status)
        
        # Si es un mensaje de éxito, mostrar información adicional
        if "Video MP4 guardado:" in status:
            QMessageBox.information(
                self, 
                "🎬 Grabación MP4 Completada", 
                f"{status}\n\n"
                f"📁 Ubicación: videos_grabados/\n"
                f"📋 Anotaciones capturadas: {len(self.annotations_log)}\n"
                f"🎥 Formato: MP4 con anotaciones superpuestas\n"
                f"⏱️ Grabación finalizada exitosamente"
            )


def main():
    """Función principal"""
    app = QApplication(sys.argv)
    
    # Aplicar tema oscuro moderno
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt6())
    
    # Crear y mostrar ventana
    window = CameraIPViewer()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main() 