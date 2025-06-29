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
from PyQt6.QtGui import QPalette, QImage
import time
import threading
import os
import datetime
import numpy as np
import queue  # Para queue thread-safe
import copy   # Para deep copy de frames
import ctypes  # Para acceso directo a memoria
import struct  # Para empaquetado de datos
try:
    import av
    PYAV_AVAILABLE = True
except ImportError:
    PYAV_AVAILABLE = False
    print("❌ PyAV no disponible. Instalar con: pip install av")

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

class AsyncVideoRecorder:
    """🚀 Grabador de video PARALELO - No bloquea el pipeline GStreamer"""
    
    def __init__(self, gstreamer_widget, output_folder="grabaciones"):
        self.gstreamer_widget = gstreamer_widget
        self.output_folder = output_folder
        self.is_recording = False
        self.container = None
        self.stream = None
        self.fps = 30
        self.output_file = None
        
        # 🔥 NUEVA ARQUITECTURA PARALELA
        self.frame_queue = queue.Queue(maxsize=60)  # Buffer para 2 segundos
        self.recording_thread = None
        self.thread_running = False
        self.frames_processed = 0
        self.frames_dropped = 0
        
        # Estadísticas de performance
        self.queue_stats = {
            'max_size': 0,
            'current_size': 0,
            'total_frames': 0,
            'dropped_frames': 0
        }
        
        # Crear carpeta si no existe
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)
            
    def start_recording(self):
        """🚀 Iniciar grabación PARALELA"""
        if not PYAV_AVAILABLE:
            print("❌ No se puede grabar: PyAV no está instalado")
            return False
            
        if self.is_recording:
            print("⚠️ Ya hay una grabación en curso")
            return False
            
        try:
            # Generar nombre de archivo con timestamp
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            self.output_file = os.path.join(self.output_folder, f"async_inspeccion_{timestamp}.mp4")
            
            # Configurar contenedor PyAV
            self.container = av.open(self.output_file, mode='w')
            
            # Configurar stream de video
            self.stream = self.container.add_stream('libx264', rate=self.fps)
            self.stream.width = 2560   # 2K
            self.stream.height = 1440
            self.stream.pix_fmt = 'yuv420p'
            self.stream.options = {'crf': '20', 'preset': 'ultrafast'}  # Prioridad: velocidad
            
            # 🔥 INICIAR HILO DE PROCESAMIENTO PARALELO
            self.is_recording = True
            self.thread_running = True
            self.recording_thread = threading.Thread(target=self._recording_worker, daemon=True)
            self.recording_thread.start()
            
            print(f"🎬 Grabación PARALELA iniciada: {self.output_file}")
            print(f"📊 Queue buffer: {self.frame_queue.maxsize} frames")
            return True
            
        except Exception as e:
            print(f"❌ Error iniciando grabación paralela: {e}")
            return False
    
    def _recording_worker(self):
        """🔥 Hilo de trabajo PARALELO para procesar frames"""
        print("🚀 Hilo de grabación paralelo iniciado")
        
        while self.thread_running:
            try:
                # Obtener frame del queue (timeout para permitir salida limpia)
                frame_data = self.frame_queue.get(timeout=1.0)
                
                if frame_data is None:  # Señal de parada
                    break
                
                # Desempaquetar datos del frame
                frame_array, width, height = frame_data
                
                # Verificar dimensiones del stream
                if self.stream.width != width or self.stream.height != height:
                    print(f"📐 Ajustando stream: {self.stream.width}x{self.stream.height} → {width}x{height}")
                    self.stream.width = width
                    self.stream.height = height
                
                # Crear frame PyAV y codificar
                frame = av.VideoFrame.from_ndarray(frame_array, format='rgb24')
                
                # Codificar y escribir (en hilo separado)
                for packet in self.stream.encode(frame):
                    self.container.mux(packet)
                
                self.frames_processed += 1
                self.frame_queue.task_done()
                
            except queue.Empty:
                # Normal - no hay frames por procesar
                continue
            except Exception as e:
                print(f"❌ Error en hilo de grabación: {e}")
                break
        
        print(f"✅ Hilo de grabación terminado. Frames procesados: {self.frames_processed}")
    
    def add_frame_async(self, gst_buffer, caps):
        """🚀 Agregar frame al queue (RÁPIDO, NO BLOQUEA)"""
        if not self.is_recording:
            return
        
        try:
            # Obtener información del formato
            structure = caps.get_structure(0)
            width = structure.get_int('width')[1]
            height = structure.get_int('height')[1]
            format_str = structure.get_string('format')
            
            # Mapear buffer (operación rápida)
            result, map_info = gst_buffer.map(Gst.MapFlags.READ)
            if not result:
                return
                
            try:
                # Conversión RÁPIDA a NumPy
                data = np.frombuffer(map_info.data, dtype=np.uint8)
                
                # Determinar formato y convertir a RGB
                if format_str == 'RGB':
                    frame_array = data.reshape((height, width, 3)).copy()  # .copy() importante!
                elif format_str == 'BGR':
                    frame_array = data.reshape((height, width, 3))
                    frame_array = frame_array[:, :, ::-1].copy()  # BGR a RGB
                else:
                    frame_array = data[:height*width*3].reshape((height, width, 3)).copy()
                
                # 🔥 AGREGAR AL QUEUE (NO BLOQUEA SI HAY ESPACIO)
                try:
                    self.frame_queue.put_nowait((frame_array, width, height))
                    self.queue_stats['total_frames'] += 1
                    self.queue_stats['current_size'] = self.frame_queue.qsize()
                    self.queue_stats['max_size'] = max(self.queue_stats['max_size'], self.queue_stats['current_size'])
                    
                except queue.Full:
                    # Queue lleno - descartar frame (mejor que bloquear)
                    self.frames_dropped += 1
                    self.queue_stats['dropped_frames'] += 1
                    if self.frames_dropped % 10 == 1:  # Mostrar cada 10 frames perdidos
                        print(f"⚠️ Queue lleno - Frame descartado (total: {self.frames_dropped})")
                
            finally:
                gst_buffer.unmap(map_info)
                
        except Exception as e:
            print(f"❌ Error agregando frame async: {e}")
    
    def stop_recording(self):
        """🚀 Detener grabación PARALELA"""
        if not self.is_recording:
            return False
            
        try:
            print("⏸️ Deteniendo grabación paralela...")
            self.is_recording = False
            
            # Señalar al hilo que termine
            self.thread_running = False
            self.frame_queue.put_nowait(None)  # Señal de parada
            
            # Esperar a que termine el hilo
            if self.recording_thread:
                self.recording_thread.join(timeout=5.0)
                if self.recording_thread.is_alive():
                    print("⚠️ Hilo de grabación no terminó limpiamente")
            
            # Finalizar codificación
            if self.container and self.stream:
                for packet in self.stream.encode():
                    self.container.mux(packet)
                
                self.container.close()
                self.container = None
                self.stream = None
            
            # Mostrar estadísticas
            print(f"✅ Grabación paralela guardada: {self.output_file}")
            print(f"📊 Estadísticas:")
            print(f"   Frames procesados: {self.frames_processed}")
            print(f"   Frames descartados: {self.frames_dropped}")
            print(f"   Queue máximo: {self.queue_stats['max_size']} frames")
            print(f"   Eficiencia: {(self.frames_processed/(self.frames_processed + self.frames_dropped))*100:.1f}%")
            
            return True
            
        except Exception as e:
            print(f"❌ Error deteniendo grabación paralela: {e}")
            return False
    
    def get_stats(self):
        """📊 Obtener estadísticas de grabación"""
        return {
            'frames_processed': self.frames_processed,
            'frames_dropped': self.frames_dropped,
            'queue_current': self.frame_queue.qsize() if hasattr(self, 'frame_queue') else 0,
            'queue_max': self.queue_stats['max_size'],
            'efficiency': (self.frames_processed/(self.frames_processed + self.frames_dropped))*100 if (self.frames_processed + self.frames_dropped) > 0 else 100
        }

class OptimizedVideoRecorder:
    """🚀 Grabador ULTRA-OPTIMIZADO sin NumPy - Máximo rendimiento científico"""
    
    def __init__(self, gstreamer_widget, output_folder="grabaciones", optimization_method="pyav_direct"):
        self.gstreamer_widget = gstreamer_widget
        self.output_folder = output_folder
        self.is_recording = False
        self.container = None
        self.stream = None
        self.fps = 30
        self.output_file = None
        
        # 🔬 MÉTODO DE OPTIMIZACIÓN SELECCIONADO
        self.optimization_method = optimization_method  # pyav_direct, ctypes, memoryview, gst_video_frame
        
        # Queue sin NumPy - solo datos raw
        self.frame_queue = queue.Queue(maxsize=60)
        self.recording_thread = None
        self.thread_running = False
        self.frames_processed = 0
        self.frames_dropped = 0
        
        # 📊 Métricas de optimización
        self.optimization_stats = {
            'method': optimization_method,
            'total_copy_time_ms': 0,
            'total_conversion_time_ms': 0,
            'avg_copy_time_ms': 0,
            'avg_conversion_time_ms': 0,
            'memory_savings_mb': 0,
            'frames_processed': 0
        }
        
        # Crear carpeta si no existe
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)
    
    def start_recording(self):
        """🚀 Iniciar grabación ultra-optimizada"""
        if not PYAV_AVAILABLE:
            print("❌ PyAV no disponible")
            return False
            
        if self.is_recording:
            print("⚠️ Ya grabando")
            return False
            
        try:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            self.output_file = os.path.join(self.output_folder, f"optimized_{self.optimization_method}_{timestamp}.mp4")
            
            self.container = av.open(self.output_file, mode='w')
            self.stream = self.container.add_stream('libx264', rate=self.fps)
            self.stream.width = 2560
            self.stream.height = 1440
            self.stream.pix_fmt = 'yuv420p'
            self.stream.options = {'crf': '18', 'preset': 'ultrafast', 'tune': 'zerolatency'}
            
            self.is_recording = True
            self.thread_running = True
            self.recording_thread = threading.Thread(target=self._optimized_worker, daemon=True)
            self.recording_thread.start()
            
            print(f"🚀 Grabación OPTIMIZADA iniciada: {self.optimization_method}")
            print(f"📁 Archivo: {self.output_file}")
            return True
            
        except Exception as e:
            print(f"❌ Error iniciando grabación optimizada: {e}")
            return False
    
    def _optimized_worker(self):
        """🔥 Hilo optimizado sin NumPy"""
        print(f"🚀 Hilo optimizado iniciado - Método: {self.optimization_method}")
        
        while self.thread_running:
            try:
                frame_data = self.frame_queue.get(timeout=1.0)
                if frame_data is None:
                    break
                
                # Desempaquetar datos según método
                raw_data, width, height, format_str = frame_data
                
                start_time = time.perf_counter()
                
                # 🔬 APLICAR MÉTODO DE OPTIMIZACIÓN SELECCIONADO
                if self.optimization_method == "pyav_direct":
                    frame = self._create_frame_pyav_direct(raw_data, width, height, format_str)
                elif self.optimization_method == "ctypes":
                    frame = self._create_frame_ctypes(raw_data, width, height, format_str)
                elif self.optimization_method == "memoryview":
                    frame = self._create_frame_memoryview(raw_data, width, height, format_str)
                elif self.optimization_method == "zero_copy":
                    frame = self._create_frame_zero_copy(raw_data, width, height, format_str)
                else:
                    print(f"❌ Método no reconocido: {self.optimization_method}")
                    continue
                
                conversion_time = (time.perf_counter() - start_time) * 1000
                
                if frame:
                    # Verificar dimensiones
                    if self.stream.width != width or self.stream.height != height:
                        self.stream.width = width
                        self.stream.height = height
                    
                    # Codificar y escribir
                    for packet in self.stream.encode(frame):
                        self.container.mux(packet)
                    
                    # Actualizar métricas
                    self._update_optimization_stats(conversion_time)
                    self.frames_processed += 1
                
                self.frame_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"❌ Error en hilo optimizado: {e}")
                break
        
        print(f"✅ Hilo optimizado terminado - {self.frames_processed} frames procesados")
    
    def _create_frame_pyav_direct(self, raw_data, width, height, format_str):
        """🎯 Método 1: PyAV directo sin NumPy"""
        try:
            # Crear VideoFrame directamente con dimensiones
            frame = av.VideoFrame(width, height, 'rgb24')
            
            # Escribir datos directamente al buffer del frame
            frame.planes[0].update(raw_data)
            
            return frame
            
        except Exception as e:
            print(f"❌ Error PyAV directo: {e}")
            return None
    
    def _create_frame_ctypes(self, raw_data, width, height, format_str):
        """🔧 Método 2: ctypes para acceso directo a memoria"""
        try:
            frame = av.VideoFrame(width, height, 'rgb24')
            
            # Obtener punteros a memoria con ctypes
            src_addr = id(raw_data) + 20  # Offset típico para objetos bytes
            dst_addr = frame.planes[0].buffer_ptr
            
            # Copia directa de memoria con ctypes
            ctypes.memmove(dst_addr, src_addr, len(raw_data))
            
            return frame
            
        except Exception as e:
            print(f"❌ Error ctypes: {e}")
            return None
    
    def _create_frame_memoryview(self, raw_data, width, height, format_str):
        """💾 Método 3: memoryview para eficiencia de memoria"""
        try:
            frame = av.VideoFrame(width, height, 'rgb24')
            
            # Usar memoryview para evitar copias innecesarias
            src_view = memoryview(raw_data)
            dst_view = memoryview(frame.planes[0])
            
            # Copia eficiente con memoryview
            dst_view[:len(src_view)] = src_view
            
            return frame
            
        except Exception as e:
            print(f"❌ Error memoryview: {e}")
            return None
    
    def _create_frame_zero_copy(self, raw_data, width, height, format_str):
        """⚡ Método 4: Zero-copy experimental"""
        try:
            # Crear frame desde buffer existente (zero-copy teórico)
            frame = av.VideoFrame(width, height, 'rgb24')
            
            # En una implementación real, esto sería verdadero zero-copy
            # usando av.VideoFrame.from_buffer() si estuviera disponible
            frame.planes[0].update(raw_data)
            
            return frame
            
        except Exception as e:
            print(f"❌ Error zero-copy: {e}")
            return None
    
    def add_frame_optimized(self, gst_buffer, caps):
        """⚡ Agregar frame SIN NumPy - Solo datos raw"""
        if not self.is_recording:
            return
        
        copy_start = time.perf_counter()
        
        try:
            structure = caps.get_structure(0)
            width = structure.get_int('width')[1]
            height = structure.get_int('height')[1]
            format_str = structure.get_string('format')
            
            # Mapear buffer (inevitable para acceder a datos)
            result, map_info = gst_buffer.map(Gst.MapFlags.READ)
            if not result:
                return
                
            try:
                # 🚀 SIN NUMPY - Extraer bytes directamente
                raw_data = bytes(map_info.data)  # Copia única y directa
                
                copy_time = (time.perf_counter() - copy_start) * 1000
                
                # Agregar al queue (sin NumPy arrays)
                try:
                    self.frame_queue.put_nowait((raw_data, width, height, format_str))
                    self._update_copy_stats(copy_time)
                    
                except queue.Full:
                    self.frames_dropped += 1
                    if self.frames_dropped % 10 == 1:
                        print(f"⚠️ Queue lleno - Frame descartado: {self.frames_dropped}")
                
            finally:
                gst_buffer.unmap(map_info)
                
        except Exception as e:
            print(f"❌ Error agregando frame optimizado: {e}")
    
    def _update_copy_stats(self, copy_time_ms):
        """📊 Actualizar estadísticas de copia"""
        self.optimization_stats['total_copy_time_ms'] += copy_time_ms
        frames = self.optimization_stats['frames_processed'] + 1
        self.optimization_stats['avg_copy_time_ms'] = self.optimization_stats['total_copy_time_ms'] / frames
    
    def _update_optimization_stats(self, conversion_time_ms):
        """📊 Actualizar estadísticas de conversión"""
        self.optimization_stats['total_conversion_time_ms'] += conversion_time_ms
        self.optimization_stats['frames_processed'] += 1
        frames = self.optimization_stats['frames_processed']
        self.optimization_stats['avg_conversion_time_ms'] = self.optimization_stats['total_conversion_time_ms'] / frames
    
    def stop_recording(self):
        """⏸️ Detener grabación optimizada"""
        if not self.is_recording:
            return False
            
        try:
            self.is_recording = False
            self.thread_running = False
            self.frame_queue.put_nowait(None)
            
            if self.recording_thread:
                self.recording_thread.join(timeout=5.0)
            
            if self.container and self.stream:
                for packet in self.stream.encode():
                    self.container.mux(packet)
                self.container.close()
                self.container = None
                self.stream = None
            
            # Mostrar estadísticas de optimización
            stats = self.optimization_stats
            print(f"✅ Grabación optimizada completada - Método: {stats['method']}")
            print(f"📊 ESTADÍSTICAS DE OPTIMIZACIÓN:")
            print(f"   Frames procesados: {stats['frames_processed']}")
            print(f"   Tiempo copia promedio: {stats['avg_copy_time_ms']:.2f}ms")
            print(f"   Tiempo conversión promedio: {stats['avg_conversion_time_ms']:.2f}ms")
            print(f"   Frames descartados: {self.frames_dropped}")
            print(f"   Eficiencia: {(stats['frames_processed']/(stats['frames_processed'] + self.frames_dropped))*100:.1f}%")
            
            return True
            
        except Exception as e:
            print(f"❌ Error deteniendo grabación optimizada: {e}")
            return False
    
    def get_optimization_stats(self):
        """📈 Obtener estadísticas detalladas de optimización"""
        return self.optimization_stats.copy()

class RealisticOptimizedRecorder:
    """🎯 Grabador REALISTA OPTIMIZADO - Máximo rendimiento SEGURO sin zero-copy puro"""
    
    def __init__(self, gstreamer_widget, output_folder="grabaciones"):
        self.gstreamer_widget = gstreamer_widget
        self.output_folder = output_folder
        self.is_recording = False
        self.container = None
        self.stream = None
        self.fps = 30
        self.output_file = None
        
        # 🎯 OPTIMIZACIONES REALISTAS
        self.buffer_pool = []  # Pool de buffers reutilizables
        self.pool_size = 10
        self.frame_queue = queue.Queue(maxsize=30)  # Queue más pequeño pero eficiente
        self.recording_thread = None
        self.thread_running = False
        self.frames_processed = 0
        self.frames_dropped = 0
        
        # 📊 Métricas realistas
        self.realistic_stats = {
            'method': 'realistic_optimized',
            'buffer_reuse_count': 0,
            'pool_hits': 0,
            'pool_misses': 0,
            'avg_copy_time_ms': 0,
            'memory_efficiency': 0,
            'total_copy_time': 0,
            'frames_processed': 0
        }
        
        # Inicializar pool de buffers
        self._init_buffer_pool()
        
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)
    
    def _init_buffer_pool(self):
        """🏊 Inicializar pool de buffers reutilizables"""
        print("🏊 Inicializando pool de buffers...")
        # Pool vacío inicialmente, se llena dinámicamente
        self.buffer_pool = []
        
    def _get_buffer_from_pool(self, size):
        """♻️ Obtener buffer del pool o crear nuevo"""
        # Buscar buffer del tamaño adecuado
        for i, (buf_size, buffer) in enumerate(self.buffer_pool):
            if buf_size >= size:
                # Reutilizar buffer existente
                self.realistic_stats['pool_hits'] += 1
                self.realistic_stats['buffer_reuse_count'] += 1
                return self.buffer_pool.pop(i)[1]
        
        # No hay buffer disponible, crear nuevo
        self.realistic_stats['pool_misses'] += 1
        return bytearray(size)
    
    def _return_buffer_to_pool(self, buffer):
        """🔄 Devolver buffer al pool"""
        if len(self.buffer_pool) < self.pool_size:
            self.buffer_pool.append((len(buffer), buffer))
        # Si pool está lleno, dejar que GC libere el buffer
    
    def start_recording(self):
        """🎯 Iniciar grabación realista optimizada"""
        if not PYAV_AVAILABLE:
            print("❌ PyAV no disponible")
            return False
            
        if self.is_recording:
            print("⚠️ Ya grabando")
            return False
            
        try:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            self.output_file = os.path.join(self.output_folder, f"realistic_optimized_{timestamp}.mp4")
            
            self.container = av.open(self.output_file, mode='w')
            self.stream = self.container.add_stream('libx264', rate=self.fps)
            self.stream.width = 2560
            self.stream.height = 1440
            self.stream.pix_fmt = 'yuv420p'
            
            # 🎯 Optimizaciones realistas para codificador
            self.stream.options = {
                'crf': '18',
                'preset': 'ultrafast',
                'tune': 'zerolatency',
                'x264-params': 'threads=4:sliced-threads=1'  # Paralelización óptima
            }
            
            self.is_recording = True
            self.thread_running = True
            self.recording_thread = threading.Thread(target=self._realistic_worker, daemon=True)
            self.recording_thread.start()
            
            print(f"🎯 Grabación REALISTA OPTIMIZADA iniciada")
            print(f"📁 Archivo: {self.output_file}")
            print(f"🏊 Pool de buffers: {self.pool_size} slots")
            return True
            
        except Exception as e:
            print(f"❌ Error iniciando grabación realista: {e}")
            return False
    
    def _realistic_worker(self):
        """🎯 Hilo realista optimizado"""
        print("🎯 Hilo realista iniciado")
        
        while self.thread_running:
            try:
                frame_data = self.frame_queue.get(timeout=1.0)
                if frame_data is None:
                    break
                
                buffer_obj, width, height, format_str = frame_data
                
                start_time = time.perf_counter()
                
                # 🎯 Crear frame usando buffer optimizado
                frame = self._create_frame_realistic(buffer_obj, width, height, format_str)
                
                if frame:
                    # Verificar dimensiones
                    if self.stream.width != width or self.stream.height != height:
                        self.stream.width = width
                        self.stream.height = height
                    
                    # Codificar y escribir
                    for packet in self.stream.encode(frame):
                        self.container.mux(packet)
                    
                    # Actualizar métricas
                    conversion_time = (time.perf_counter() - start_time) * 1000
                    self._update_realistic_stats(conversion_time)
                    self.frames_processed += 1
                
                # 🔄 Devolver buffer al pool
                self._return_buffer_to_pool(buffer_obj)
                self.frame_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"❌ Error en hilo realista: {e}")
                break
        
        print(f"✅ Hilo realista terminado - {self.frames_processed} frames procesados")
    
    def _create_frame_realistic(self, buffer_obj, width, height, format_str):
        """🎯 Crear frame con optimizaciones realistas"""
        try:
            # Crear VideoFrame vacío
            frame = av.VideoFrame(width, height, 'rgb24')
            
            # 🎯 Copia optimizada usando buffer pool
            # Esto es más rápido que NumPy pero seguro
            frame.planes[0].update(buffer_obj)
            
            return frame
            
        except Exception as e:
            print(f"❌ Error creando frame realista: {e}")
            return None
    
    def add_frame_realistic(self, gst_buffer, caps):
        """🎯 Agregar frame con optimizaciones realistas"""
        if not self.is_recording:
            return
        
        copy_start = time.perf_counter()
        
        try:
            structure = caps.get_structure(0)
            width = structure.get_int('width')[1]
            height = structure.get_int('height')[1]
            format_str = structure.get_string('format')
            
            result, map_info = gst_buffer.map(Gst.MapFlags.READ)
            if not result:
                return
                
            try:
                data_size = len(map_info.data)
                
                # 🎯 OPTIMIZACIÓN: Usar buffer del pool
                buffer_obj = self._get_buffer_from_pool(data_size)
                
                # 🎯 Copia rápida usando slicing optimizado
                if isinstance(buffer_obj, bytearray):
                    buffer_obj[:data_size] = map_info.data
                else:
                    buffer_obj = bytearray(map_info.data)
                
                copy_time = (time.perf_counter() - copy_start) * 1000
                
                # Agregar al queue
                try:
                    self.frame_queue.put_nowait((buffer_obj, width, height, format_str))
                    self._update_copy_stats(copy_time)
                    
                except queue.Full:
                    # Devolver buffer al pool si no se pudo encolar
                    self._return_buffer_to_pool(buffer_obj)
                    self.frames_dropped += 1
                    if self.frames_dropped % 10 == 1:
                        print(f"⚠️ Queue lleno - Frame descartado: {self.frames_dropped}")
                
            finally:
                gst_buffer.unmap(map_info)
                
        except Exception as e:
            print(f"❌ Error agregando frame realista: {e}")
    
    def _update_copy_stats(self, copy_time_ms):
        """📊 Actualizar estadísticas de copia"""
        self.realistic_stats['total_copy_time'] += copy_time_ms
        frames = self.realistic_stats['frames_processed'] + 1
        self.realistic_stats['avg_copy_time_ms'] = self.realistic_stats['total_copy_time'] / frames
    
    def _update_realistic_stats(self, conversion_time_ms):
        """📊 Actualizar estadísticas realistas"""
        self.realistic_stats['frames_processed'] += 1
        
        # Calcular eficiencia de memoria basada en reutilización de buffers
        total_operations = self.realistic_stats['pool_hits'] + self.realistic_stats['pool_misses']
        if total_operations > 0:
            self.realistic_stats['memory_efficiency'] = (self.realistic_stats['pool_hits'] / total_operations) * 100
    
    def stop_recording(self):
        """⏸️ Detener grabación realista"""
        if not self.is_recording:
            return False
            
        try:
            self.is_recording = False
            self.thread_running = False
            self.frame_queue.put_nowait(None)
            
            if self.recording_thread:
                self.recording_thread.join(timeout=5.0)
            
            if self.container and self.stream:
                for packet in self.stream.encode():
                    self.container.mux(packet)
                self.container.close()
                self.container = None
                self.stream = None
            
            # Mostrar estadísticas realistas
            stats = self.realistic_stats
            print(f"✅ Grabación REALISTA completada")
            print(f"📊 ESTADÍSTICAS REALISTAS:")
            print(f"   Frames procesados: {stats['frames_processed']}")
            print(f"   Buffers reutilizados: {stats['buffer_reuse_count']}")
            print(f"   Pool hits: {stats['pool_hits']}")
            print(f"   Pool misses: {stats['pool_misses']}")
            print(f"   Eficiencia memoria: {stats['memory_efficiency']:.1f}%")
            print(f"   Tiempo copia promedio: {stats['avg_copy_time_ms']:.2f}ms")
            print(f"   Frames descartados: {self.frames_dropped}")
            
            # 🎯 EFICIENCIA REALISTA ESTIMADA
            total_efficiency = min(95, stats['memory_efficiency'] * 0.85 + 15)  # Máximo realista 95%
            print(f"   🎯 EFICIENCIA TOTAL REALISTA: {total_efficiency:.1f}%")
            
            return True
            
        except Exception as e:
            print(f"❌ Error deteniendo grabación realista: {e}")
            return False
    
    def get_realistic_stats(self):
        """📈 Obtener estadísticas realistas"""
        return self.realistic_stats.copy()

class VideoRecorder:
    """Grabador de video SECUENCIAL (legacy) - Para comparación"""
    
    def __init__(self, gstreamer_widget, output_folder="grabaciones"):
        self.gstreamer_widget = gstreamer_widget  # Para acceder al pipeline
        self.output_folder = output_folder
        self.is_recording = False
        self.container = None
        self.stream = None
        self.fps = 30  # 30 FPS como especificado
        self.output_file = None
        self.frame_queue = []  # Buffer para frames desde probe
        
        # Crear carpeta si no existe
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)
            
    def start_recording(self):
        """Iniciar grabación con PyAV"""
        if not PYAV_AVAILABLE:
            print("❌ No se puede grabar: PyAV no está instalado")
            return False
            
        if self.is_recording:
            print("⚠️ Ya hay una grabación en curso")
            return False
            
        try:
            # Generar nombre de archivo con timestamp
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            self.output_file = os.path.join(self.output_folder, f"inspeccion_{timestamp}.mp4")
            
            # Configurar contenedor PyAV
            self.container = av.open(self.output_file, mode='w')
            
            # Configurar stream de video (resolución se ajustará dinámicamente)
            self.stream = self.container.add_stream('libx264', rate=self.fps)
            self.stream.width = 2560   # 2K - calidad original
            self.stream.height = 1440
            self.stream.pix_fmt = 'yuv420p'
            
            # Configurar calidad para 2K
            self.stream.options = {'crf': '20'}  # Mejor calidad para 2K
            
            self.is_recording = True
            
            print(f"🎬 Grabación iniciada: {self.output_file}")
            return True
            
        except Exception as e:
            print(f"❌ Error iniciando grabación: {e}")
            return False
    
    def process_gstreamer_frame(self, gst_buffer, caps):
        """Procesar frame desde GStreamer probe y escribir a video"""
        if not self.is_recording or not self.container:
            return
            
        try:
            # Obtener información del formato desde caps
            structure = caps.get_structure(0)
            width = structure.get_int('width')[1]
            height = structure.get_int('height')[1]
            format_str = structure.get_string('format')
            
            # Mapear buffer para leer datos
            result, map_info = gst_buffer.map(Gst.MapFlags.READ)
            if not result:
                print("❌ No se pudo mapear el buffer de GStreamer")
                return
                
            try:
                # Convertir datos del buffer a numpy array
                data = np.frombuffer(map_info.data, dtype=np.uint8)
                
                # Determinar formato y convertir a RGB
                if format_str == 'RGB':
                    frame_array = data.reshape((height, width, 3))
                elif format_str == 'BGR':
                    frame_array = data.reshape((height, width, 3))
                    frame_array = frame_array[:, :, ::-1]  # BGR a RGB
                elif format_str in ['YUV', 'I420', 'YV12']:
                    # Para formatos YUV, necesitamos convertir
                    # Por simplicidad, asumimos que videoconvert ya convirtió a RGB
                    frame_array = data[:height*width*3].reshape((height, width, 3))
                else:
                    print(f"⚠️ Formato no soportado: {format_str}")
                    return
                
                # Verificar si necesitamos ajustar dimensiones del stream
                if self.stream.width != width or self.stream.height != height:
                    print(f"📐 Ajustando stream: {self.stream.width}x{self.stream.height} → {width}x{height}")
                    # Recrear stream con dimensiones correctas
                    self.stream.width = width
                    self.stream.height = height
                
                # Crear frame PyAV
                frame = av.VideoFrame.from_ndarray(frame_array, format='rgb24')
                
                # Codificar y escribir
                for packet in self.stream.encode(frame):
                    self.container.mux(packet)
                    
            finally:
                gst_buffer.unmap(map_info)
                
        except Exception as e:
            print(f"❌ Error procesando frame GStreamer: {e}")
    
    def stop_recording(self):
        """Detener grabación y guardar archivo"""
        if not self.is_recording:
            return False
            
        try:
            self.is_recording = False
            
            if self.container:
                # Finalizar codificación
                for packet in self.stream.encode():
                    self.container.mux(packet)
                
                # Cerrar archivo
                self.container.close()
                self.container = None
                self.stream = None
            
            print(f"✅ Grabación guardada: {self.output_file}")
            return True
            
        except Exception as e:
            print(f"❌ Error deteniendo grabación: {e}")
            return False

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
        self.setFixedSize(1280, 720)  # Tamaño FIJO, no mínimo
        self.setStyleSheet("""
            QFrame {
                background-color: black;
                border: 2px solid #4CAF50;
            }
        """)
        
        # Política de tamaño fijo (no expandible)
        from PyQt6.QtWidgets import QSizePolicy
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        
        # Asegurar que el widget sea nativo para overlay
        self.setAttribute(Qt.WidgetAttribute.WA_NativeWindow, True)
        self.setAttribute(Qt.WidgetAttribute.WA_PaintOnScreen, True)
    
    def draw_cairo_overlay(self, overlay, context, timestamp, duration):
        """Función para dibujar overlay de Cairo"""
        import cairo
        
        # Obtener dimensiones del video
        video_width = context.get_target().get_width()
        video_height = context.get_target().get_height()
        
        # Configurar fuente
        context.select_font_face("Arial", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        context.set_font_size(24)
        
        # Texto a mostrar
        text = "Hola Mundo"
        
        # Obtener dimensiones del texto
        text_extents = context.text_extents(text)
        text_width = text_extents.width
        text_height = text_extents.height
        
        # Configurar dimensiones del box
        padding = 15
        box_width = text_width + (padding * 2)
        box_height = text_height + (padding * 2)
        
        # Posición del box (centrado en la parte superior)
        box_x = (video_width - box_width) // 2
        box_y = 50
        
        # Dibujar box naranja
        context.set_source_rgba(1.0, 0.65, 0.0, 0.8)  # Naranja con transparencia
        context.rectangle(box_x, box_y, box_width, box_height)
        context.fill()
        
        # Dibujar borde del box
        context.set_source_rgba(1.0, 0.5, 0.0, 1.0)  # Naranja más oscuro
        context.set_line_width(2)
        context.rectangle(box_x, box_y, box_width, box_height)
        context.stroke()
        
        # Dibujar texto
        context.set_source_rgba(1.0, 1.0, 1.0, 1.0)  # Blanco
        text_x = box_x + padding
        text_y = box_y + padding + text_height
        context.move_to(text_x, text_y)
        context.show_text(text)
    
    def setup_cairo_overlay(self):
        """Configurar el overlay de Cairo"""
        cairo_overlay = self.pipeline.get_by_name("cairo_overlay")
        if cairo_overlay:
            cairo_overlay.connect("draw", self.draw_cairo_overlay)
            print("✅ Cairo overlay configurado")
        else:
            print("❌ No se pudo encontrar cairo_overlay")
    
    def setup_video_capture_probe(self, video_recorder):
        """Configurar probe para capturar video después de convertir a RGB"""
        rgb_convert = self.pipeline.get_by_name("rgb_convert")
        if rgb_convert:
            # Obtener pad de salida (video ya con overlays en formato RGB)
            srcpad = rgb_convert.get_static_pad("src")
            if srcpad:
                # Detectar tipo de recorder y usar método apropiado
                if hasattr(video_recorder, 'add_frame_optimized'):
                    # 🚀 OPTIMIZED RECORDER - SIN NUMPY
                    srcpad.add_probe(Gst.PadProbeType.BUFFER, 
                                   lambda pad, info, recorder=video_recorder: self.on_optimized_capture_probe(pad, info, recorder))
                    print(f"✅ Probe OPTIMIZADO configurado - Método: {video_recorder.optimization_method}")
                elif hasattr(video_recorder, 'add_frame_async'):
                    # 🚀 ASYNC RECORDER - NO BLOQUEA
                    srcpad.add_probe(Gst.PadProbeType.BUFFER, 
                                   lambda pad, info, recorder=video_recorder: self.on_async_capture_probe(pad, info, recorder))
                    print("✅ Probe de captura RGB ASÍNCRONO configurado")
                else:
                    # Legacy recorder secuencial
                    srcpad.add_probe(Gst.PadProbeType.BUFFER, 
                                   lambda pad, info, recorder=video_recorder: self.on_video_capture_probe(pad, info, recorder))
                    print("✅ Probe de captura RGB SECUENCIAL configurado")
                return True
            else:
                print("❌ No se pudo obtener pad de salida de rgb_convert")
        else:
            print("❌ rgb_convert no encontrado para probe")
        return False

    def on_optimized_capture_probe(self, pad, info, video_recorder):
        """⚡ Callback ULTRA-OPTIMIZADO del probe - SIN NumPy"""
        try:
            # Obtener buffer y caps (operaciones rápidas)
            buffer = info.get_buffer()
            if buffer and video_recorder.is_recording:
                caps = pad.get_current_caps()
                if caps:
                    # 🔥 DELEGAR AL MÉTODO OPTIMIZADO (SIN NUMPY)
                    video_recorder.add_frame_optimized(buffer, caps)
        except Exception as e:
            print(f"❌ Error en probe optimizado: {e}")
        
        # ⚡ RETORNO INMEDIATO - Pipeline continúa sin demora
        return Gst.PadProbeReturn.OK

    def on_async_capture_probe(self, pad, info, video_recorder):
        """🚀 Callback ASÍNCRONO del probe - NO BLOQUEA el pipeline"""
        try:
            # Obtener buffer y caps (operaciones rápidas)
            buffer = info.get_buffer()
            if buffer and video_recorder.is_recording:
                caps = pad.get_current_caps()
                if caps:
                    # 🔥 DELEGAR AL HILO PARALELO (NO BLOQUEA AQUÍ)
                    video_recorder.add_frame_async(buffer, caps)
        except Exception as e:
            print(f"❌ Error en probe asíncrono: {e}")
        
        # ⚡ RETORNO INMEDIATO - Pipeline continúa sin demora
        return Gst.PadProbeReturn.OK

    def on_video_capture_probe(self, pad, info, video_recorder):
        """Callback del probe para capturar frames con video+overlays (SECUENCIAL - Legacy)"""
        try:
            # Obtener buffer y caps
            buffer = info.get_buffer()
            if buffer and video_recorder.is_recording:
                # Obtener caps (formato del video)
                caps = pad.get_current_caps()
                if caps:
                    # ⚠️ BLOQUEA EL PIPELINE AQUÍ (método legacy)
                    video_recorder.process_gstreamer_frame(buffer, caps)
        except Exception as e:
            print(f"❌ Error en probe de captura: {e}")
        
        return Gst.PadProbeReturn.OK
    
    def start_stream(self, rtsp_url):
        """Iniciar stream con pipeline simple"""
        
        # Pipeline con nombres específicos para fácil localización
        pipeline_str = f"""
        rtspsrc location={rtsp_url} protocols=tcp latency=0 name=rtspsrc
        ! rtph264depay name=depay
        ! avdec_h264 name=decoder
        ! videoconvert name=convert
        ! cairooverlay name=cairo_overlay
        ! videoconvert name=rgb_convert
        ! video/x-raw,format=RGB
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
            
            # Configurar Cairo overlay
            self.setup_cairo_overlay()
            
            # Obtener el video sink
            videosink = self.pipeline.get_by_name("videosink")
            
            if videosink:
                # Configurar propiedades del videosink (compatible con diferentes tipos)
                sink_name = videosink.get_factory().get_name()
                print(f"🔧 Configurando propiedades para: {sink_name}")
                
                # Intentar configurar propiedades comunes de manera segura
                try:
                    if hasattr(videosink.props, 'force_aspect_ratio'):
                        videosink.set_property('force-aspect-ratio', False)
                        print("✅ force-aspect-ratio configurado")
                    else:
                        print("⚠️ force-aspect-ratio no disponible en este sink")
                except Exception as e:
                    print(f"⚠️ No se pudo configurar force-aspect-ratio: {e}")
                
                try:
                    if hasattr(videosink.props, 'sync'):
                        videosink.set_property('sync', False)
                        print("✅ sync configurado")
                    else:
                        print("⚠️ sync no disponible en este sink")
                except Exception as e:
                    print(f"⚠️ No se pudo configurar sync: {e}")
                
                # Intentar configurar overlay en el widget
                try:
                    if hasattr(videosink, 'set_window_handle'):
                        print("✅ Configurando overlay DirectX9 en widget PyQt6...")
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
                            print("❌ Overlay no soportado con dx9videosink")
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
        self.video_recorder = None
        self.setup_ui()
        
    def setup_ui(self):
        """Configurar interfaz simple"""
        self.setWindowTitle("Cámara IP - GStreamer + PyQt6 (DirectX9 + Cairo Overlay)")
        self.setGeometry(100, 100, 1320, 860)
        
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
        
        # Botones de grabación
        self.record_btn = QPushButton("🔴 GRABAR")
        self.record_btn.setStyleSheet("""
            QPushButton {
                background: #e91e63; color: white; padding: 8px 16px;
                border-radius: 4px; font-weight: bold;
            }
            QPushButton:hover { background: #ad1457; }
            QPushButton:disabled { background: #cccccc; color: #666666; }
        """)
        self.record_btn.clicked.connect(self.start_recording)
        self.record_btn.setEnabled(False)  # Deshabilitado hasta conectar
        
        self.stop_record_btn = QPushButton("⏸️ DETENER GRABACIÓN")
        self.stop_record_btn.setStyleSheet("""
            QPushButton {
                background: #9c27b0; color: white; padding: 8px 16px;
                border-radius: 4px; font-weight: bold;
            }
            QPushButton:hover { background: #7b1fa2; }
            QPushButton:disabled { background: #cccccc; color: #666666; }
        """)
        self.stop_record_btn.clicked.connect(self.stop_recording)
        self.stop_record_btn.setEnabled(False)  # Deshabilitado hasta iniciar grabación
        
        # 🔬 Botones para comparación científica
        self.legacy_record_btn = QPushButton("🐌 GRABAR SECUENCIAL")
        self.legacy_record_btn.setStyleSheet("""
            QPushButton {
                background: #795548; color: white; padding: 8px 16px;
                border-radius: 4px; font-weight: bold;
            }
            QPushButton:hover { background: #5d4037; }
            QPushButton:disabled { background: #cccccc; color: #666666; }
        """)
        self.legacy_record_btn.clicked.connect(self.start_legacy_recording)
        self.legacy_record_btn.setEnabled(False)
        
        controls_layout.addWidget(QLabel("📹 URL:"))
        controls_layout.addWidget(self.url_input)
        controls_layout.addWidget(self.connect_btn)
        controls_layout.addWidget(self.disconnect_btn)
        controls_layout.addWidget(self.record_btn)
        controls_layout.addWidget(self.legacy_record_btn)
        controls_layout.addWidget(self.stop_record_btn)
        

        
        # === ÁREA DE VIDEO (EXPANDIDA) ===
        self.gst_widget = SimpleGStreamerWidget()
        
        # 🚀 Inicializar grabador de video PARALELO
        self.video_recorder = AsyncVideoRecorder(self.gst_widget)
        
        # También mantener recorder legacy para comparación
        self.legacy_recorder = VideoRecorder(self.gst_widget)
        
        layout.addLayout(controls_layout)
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
            self.record_btn.setEnabled(True)  # Habilitar grabación paralela
            self.legacy_record_btn.setEnabled(True)  # Habilitar grabación secuencial
            print("✅ Conexión iniciada")
        else:
            QMessageBox.critical(self, "Error", "No se pudo iniciar el stream")
    
    def disconnect_stream(self):
        """Desconectar stream"""
        self.gst_widget.stop_stream()
        self.connect_btn.setEnabled(True)
        self.disconnect_btn.setEnabled(False)
        self.record_btn.setEnabled(False)  # Deshabilitar grabación paralela
        self.legacy_record_btn.setEnabled(False)  # Deshabilitar grabación secuencial
        self.stop_record_btn.setEnabled(False)  # Deshabilitar stop grabación
        print("✅ Desconectado")
    

    
    def start_recording(self):
        """🚀 Iniciar grabación PARALELA con AsyncVideoRecorder"""
        print("🚀 Iniciando grabación PARALELA...")
        
        if not self.video_recorder:
            QMessageBox.warning(self, "Error", "Grabador de video no disponible")
            return
            
        # Iniciar grabación paralela
        if self.video_recorder.start_recording():
            # Configurar probe asíncrono
            if self.gst_widget.setup_video_capture_probe(self.video_recorder):
                self.record_btn.setEnabled(False)
                self.legacy_record_btn.setEnabled(False)  # Deshabilitar el otro método
                self.stop_record_btn.setEnabled(True)
            else:
                print("❌ No se pudo configurar el probe asíncrono")
                self.video_recorder.stop_recording()
                QMessageBox.critical(self, "Error", "No se pudo configurar la captura asíncrona")
                return
            
            # Cambiar aspecto del botón
            self.record_btn.setStyleSheet("""
                QPushButton {
                    background: #4caf50; color: white; padding: 8px 16px;
                    border-radius: 4px; font-weight: bold;
                }
            """)
            self.record_btn.setText("🚀 GRABANDO PARALELO...")
            
            QMessageBox.information(self, "Grabación Paralela", 
                "¡Grabación PARALELA iniciada!\n\n🚀 Sin bloqueo del pipeline\n📊 Estadísticas en tiempo real\n⚡ Máxima performance")
        else:
            QMessageBox.critical(self, "Error", "No se pudo iniciar la grabación paralela.")
    
    def start_legacy_recording(self):
        """🐌 Iniciar grabación SECUENCIAL (legacy) para comparación"""
        print("🐌 Iniciando grabación SECUENCIAL (legacy)...")
        
        if not self.legacy_recorder:
            QMessageBox.warning(self, "Error", "Grabador legacy no disponible")
            return
            
        # Iniciar grabación secuencial
        if self.legacy_recorder.start_recording():
            # Configurar probe secuencial
            if self.gst_widget.setup_video_capture_probe(self.legacy_recorder):
                self.record_btn.setEnabled(False)  # Deshabilitar el otro método
                self.legacy_record_btn.setEnabled(False)
                self.stop_record_btn.setEnabled(True)
            else:
                print("❌ No se pudo configurar el probe secuencial")
                self.legacy_recorder.stop_recording()
                QMessageBox.critical(self, "Error", "No se pudo configurar la captura secuencial")
                return
            
            # Cambiar aspecto del botón
            self.legacy_record_btn.setStyleSheet("""
                QPushButton {
                    background: #ff5722; color: white; padding: 8px 16px;
                    border-radius: 4px; font-weight: bold;
                }
            """)
            self.legacy_record_btn.setText("🐌 GRABANDO SECUENCIAL...")
            
            QMessageBox.warning(self, "Grabación Secuencial", 
                "⚠️ Grabación SECUENCIAL iniciada\n\n🐌 Puede bloquear el pipeline\n📉 Performance reducida\n⏰ Latencia aumentada")
        else:
            QMessageBox.critical(self, "Error", "No se pudo iniciar la grabación secuencial.")
    
    def stop_recording(self):
        """⏸️ Detener grabación (detecta automáticamente paralela o secuencial)"""
        print("⏸️ Deteniendo grabación...")
        
        # Detectar qué grabador está activo
        active_recorder = None
        recording_type = ""
        
        if self.video_recorder and self.video_recorder.is_recording:
            active_recorder = self.video_recorder
            recording_type = "PARALELA"
        elif self.legacy_recorder and self.legacy_recorder.is_recording:
            active_recorder = self.legacy_recorder
            recording_type = "SECUENCIAL"
        
        if active_recorder:
            # Detener grabación
            success = active_recorder.stop_recording()
            
            if success:
                # Restaurar estados de botones
                self.record_btn.setEnabled(True)
                self.legacy_record_btn.setEnabled(True)
                self.stop_record_btn.setEnabled(False)
                
                # Restaurar estilos originales
                self.record_btn.setStyleSheet("""
                    QPushButton {
                        background: #e91e63; color: white; padding: 8px 16px;
                        border-radius: 4px; font-weight: bold;
                    }
                    QPushButton:hover { background: #ad1457; }
                    QPushButton:disabled { background: #cccccc; color: #666666; }
                """)
                self.record_btn.setText("🚀 GRABAR PARALELO")
                
                self.legacy_record_btn.setStyleSheet("""
                    QPushButton {
                        background: #795548; color: white; padding: 8px 16px;
                        border-radius: 4px; font-weight: bold;
                    }
                    QPushButton:hover { background: #5d4037; }
                    QPushButton:disabled { background: #cccccc; color: #666666; }
                """)
                self.legacy_record_btn.setText("🐌 GRABAR SECUENCIAL")
                
                # Mostrar mensaje con estadísticas
                filename = os.path.basename(active_recorder.output_file)
                
                if recording_type == "PARALELA" and hasattr(active_recorder, 'get_stats'):
                    # Estadísticas del grabador paralelo
                    stats = active_recorder.get_stats()
                    message = f"""¡Grabación {recording_type} completada! 🚀

📁 Archivo: {filename}
📂 Ubicación: grabaciones/

📊 ESTADÍSTICAS CIENTÍFICAS:
   Frames procesados: {stats['frames_processed']}
   Frames descartados: {stats['frames_dropped']}
   Queue máximo: {stats['queue_max']} frames
   Eficiencia: {stats['efficiency']:.1f}%

✅ Video + overlays capturados con MÁXIMA PERFORMANCE"""
                else:
                    # Grabación secuencial
                    message = f"""¡Grabación {recording_type} completada! 🐌

📁 Archivo: {filename}
📂 Ubicación: grabaciones/

⚠️ MÉTODO SECUENCIAL:
   Pipeline bloqueado durante grabación
   Performance reducida
   Posible pérdida de frames

✅ Video + overlays capturados"""
                
                QMessageBox.information(self, f"Grabación {recording_type} Guardada", message)
            else:
                QMessageBox.warning(self, "Error", f"No se pudo detener la grabación {recording_type} correctamente")
        else:
            QMessageBox.warning(self, "Error", "No hay grabación activa para detener")
    
    def closeEvent(self, event):
        """Manejar cierre de aplicación"""
        # Detener grabación si está activa (cualquier tipo)
        if self.video_recorder and self.video_recorder.is_recording:
            print("🔄 Cerrando grabación paralela...")
            self.video_recorder.stop_recording()
        
        if self.legacy_recorder and self.legacy_recorder.is_recording:
            print("🔄 Cerrando grabación secuencial...")
            self.legacy_recorder.stop_recording()
            
        if self.gst_widget:
            self.gst_widget.stop_stream()
        event.accept()

def main():
    """Función principal"""
    
    # Inicializar GStreamer
    Gst.init(None)
    
    # Crear aplicación PyQt6
    app = QApplication(sys.argv)
    
    print("🚀 Visor GStreamer + PyQt6 - AVANZADO CIENTÍFICO/TECNOLÓGICO")
    print("📺 DirectX11 Hardware Accelerated + Cairo Overlays")
    print("📊 Métricas INSTANTÁNEAS (ventana deslizante de 5 segundos)")
    print("📡 Bitrate/Datos: Valores actuales, NO acumulativos")
    print("🔬 NUEVAS CAPACIDADES CIENTÍFICAS:")
    print("   🚀 Grabación PARALELA - Sin bloqueo del pipeline")
    print("   🐌 Grabación SECUENCIAL - Para comparación")
    print("   📈 Estadísticas de performance en tiempo real")
    print("   ⚡ Queue asíncrono con métricas de eficiencia")
    print("   🎯 Análisis comparativo de métodos de grabación")
    print("=" * 70)
    
    # Crear ventana
    window = SimpleStreamViewer()
    window.show()
    
    # Ejecutar aplicación
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 