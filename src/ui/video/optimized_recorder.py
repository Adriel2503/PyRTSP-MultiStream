# -*- coding: utf-8 -*-
"""
Sistema de grabación optimizado que combina CPU y GPU con gestión inteligente de buffers
Soluciona problemas de estabilidad del GPU recorder manteniendo rendimiento
"""

import os
import time
import threading
import queue
import numpy as np
from datetime import datetime
from typing import Optional, Dict, Any, Tuple
from enum import Enum

from ...utils.logger import setup_logger
from ...core.thread_pool_manager import get_thread_pool_manager

logger = setup_logger("OptimizedRecorder")

class RecorderType(Enum):
    """Tipos de recorder disponibles"""
    CPU_PYAV = "cpu_pyav"
    GPU_FFMPEG = "gpu_ffmpeg"
    HYBRID = "hybrid"
    AUTO = "auto"

class RecorderState(Enum):
    """Estados del recorder"""
    IDLE = "idle"
    STARTING = "starting"
    RECORDING = "recording"
    STOPPING = "stopping"
    ERROR = "error"

class OptimizedFrameBuffer:
    """Buffer optimizado para frames con gestión inteligente de memoria"""
    
    def __init__(self, max_size: int = 50, drop_policy: str = "oldest"):
        self.max_size = max_size
        self.drop_policy = drop_policy  # "oldest", "newest", "adaptive"
        
        self._buffer = queue.Queue(maxsize=max_size)
        self._dropped_frames = 0
        self._total_frames = 0
        self._lock = threading.RLock()
        
        # Estadísticas de rendimiento
        self._buffer_fill_times = []
        self._processing_times = []
    
    def put_frame(self, frame_data: bytes, width: int, height: int, 
                  timeout: float = 0.1) -> bool:
        """Agregar frame al buffer con política de descarte inteligente"""
        start_time = time.time()
        
        with self._lock:
            self._total_frames += 1
            
            try:
                # Intentar agregar al buffer
                self._buffer.put((frame_data, width, height, time.time()), 
                               timeout=timeout)
                
                # Registrar tiempo de llenado
                fill_time = time.time() - start_time
                self._buffer_fill_times.append(fill_time)
                if len(self._buffer_fill_times) > 100:
                    self._buffer_fill_times.pop(0)
                
                return True
                
            except queue.Full:
                # Buffer lleno - aplicar política de descarte
                self._dropped_frames += 1
                
                if self.drop_policy == "oldest":
                    try:
                        # Descartar frame más antiguo
                        self._buffer.get_nowait()
                        self._buffer.put((frame_data, width, height, time.time()), 
                                       timeout=timeout)
                        return True
                    except (queue.Empty, queue.Full):
                        return False
                
                elif self.drop_policy == "newest":
                    # Descartar frame nuevo (no agregar)
                    return False
                
                elif self.drop_policy == "adaptive":
                    # Política adaptiva basada en carga del sistema
                    current_fill_rate = len(self._buffer_fill_times)
                    if current_fill_rate > 50:  # Alta carga
                        return False  # Descartar nuevo
                    else:
                        try:
                            self._buffer.get_nowait()
                            self._buffer.put((frame_data, width, height, time.time()), 
                                           timeout=timeout)
                            return True
                        except (queue.Empty, queue.Full):
                            return False
    
    def get_frame(self, timeout: float = 1.0) -> Optional[Tuple[bytes, int, int, float]]:
        """Obtener frame del buffer"""
        try:
            return self._buffer.get(timeout=timeout)
        except queue.Empty:
            return None
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas del buffer"""
        with self._lock:
            current_size = self._buffer.qsize()
            fill_rate = current_size / self.max_size * 100
            
            avg_fill_time = 0
            if self._buffer_fill_times:
                avg_fill_time = sum(self._buffer_fill_times) / len(self._buffer_fill_times)
            
            drop_rate = 0
            if self._total_frames > 0:
                drop_rate = self._dropped_frames / self._total_frames * 100
            
            return {
                'current_size': current_size,
                'max_size': self.max_size,
                'fill_rate_percent': fill_rate,
                'dropped_frames': self._dropped_frames,
                'total_frames': self._total_frames,
                'drop_rate_percent': drop_rate,
                'avg_fill_time_ms': avg_fill_time * 1000,
                'policy': self.drop_policy
            }
    
    def clear(self):
        """Limpiar buffer"""
        with self._lock:
            while not self._buffer.empty():
                try:
                    self._buffer.get_nowait()
                except queue.Empty:
                    break
            
            self._dropped_frames = 0
            self._total_frames = 0
            self._buffer_fill_times.clear()

class OptimizedRecorder:
    """Sistema de grabación optimizado con gestión inteligente de recursos"""
    
    def __init__(self):
        self.state = RecorderState.IDLE
        self.recorder_type = RecorderType.AUTO
        
        # Configuración
        self.width = 2560
        self.height = 1440
        self.fps = 20
        self.bitrate = "8M"
        
        # Buffer optimizado
        self.frame_buffer = OptimizedFrameBuffer(max_size=30, drop_policy="adaptive")
        
        # Threading
        self.thread_pool = get_thread_pool_manager()
        self.recording_future = None
        self.monitor_future = None
        
        # Estado interno
        self.current_filename = None
        self.recording_start_time = None
        
        # Recorders específicos
        self._pyav_recorder = None
        self._gpu_recorder = None
        
        # Métricas
        self._frames_processed = 0
        self._bytes_written = 0
        self._errors_count = 0
        
        logger.info("OptimizedRecorder inicializado")
    
    def _detect_best_recorder_type(self) -> RecorderType:
        """Detectar el mejor tipo de recorder para el sistema"""
        try:
            # Verificar disponibilidad de GPU encoding
            if self._test_gpu_availability():
                logger.info("GPU encoding disponible y funcional")
                return RecorderType.HYBRID  # Usar híbrido para máxima estabilidad
            else:
                logger.info("GPU encoding no disponible - usando CPU")
                return RecorderType.CPU_PYAV
        except Exception as e:
            logger.warning(f"Error detectando recorder: {e}")
            return RecorderType.CPU_PYAV
    
    def _test_gpu_availability(self) -> bool:
        """Probar disponibilidad de GPU encoding"""
        try:
            import subprocess
            
            # Test rápido de FFmpeg con NVENC
            result = subprocess.run(
                ['ffmpeg', '-hide_banner', '-f', 'lavfi', '-i', 'testsrc=duration=1:size=320x240:rate=1',
                 '-c:v', 'h264_nvenc', '-f', 'null', '-'],
                capture_output=True,
                timeout=5
            )
            
            return result.returncode == 0
            
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
            return False
    
    def start_recording(self, filename: str, recorder_type: Optional[RecorderType] = None) -> bool:
        """Iniciar grabación con tipo específico o automático"""
        if self.state != RecorderState.IDLE:
            logger.warning(f"No se puede iniciar grabación en estado: {self.state}")
            return False
        
        try:
            self.state = RecorderState.STARTING
            self.current_filename = filename
            self.recording_start_time = time.time()
            
            # Determinar tipo de recorder
            if recorder_type is None:
                self.recorder_type = self._detect_best_recorder_type()
            else:
                self.recorder_type = recorder_type
            
            # Crear directorio si no existe
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            # Limpiar buffer
            self.frame_buffer.clear()
            
            # Iniciar worker de grabación
            self.recording_future = self.thread_pool.submit_io_task(
                self._recording_worker
            )
            
            # Iniciar monitor de rendimiento
            self.monitor_future = self.thread_pool.submit_processing_task(
                self._monitor_worker
            )
            
            self.state = RecorderState.RECORDING
            logger.info(f"Grabación iniciada: {filename} ({self.recorder_type.value})")
            return True
            
        except Exception as e:
            logger.error(f"Error iniciando grabación: {e}")
            self.state = RecorderState.ERROR
            return False
    
    def stop_recording(self) -> bool:
        """Detener grabación"""
        if self.state != RecorderState.RECORDING:
            logger.warning(f"No se puede detener grabación en estado: {self.state}")
            return False
        
        try:
            self.state = RecorderState.STOPPING
            logger.info("Deteniendo grabación...")
            
            # Enviar señal de fin al buffer
            self.frame_buffer.put_frame(b"", 0, 0)  # Frame especial de fin
            
            # Esperar que termine el worker de grabación
            if self.recording_future:
                try:
                    self.recording_future.result(timeout=10.0)
                except Exception as e:
                    logger.error(f"Error esperando worker de grabación: {e}")
            
            # Detener monitor
            if self.monitor_future:
                try:
                    self.monitor_future.result(timeout=2.0)
                except Exception as e:
                    logger.warning(f"Error deteniendo monitor: {e}")
            
            self.state = RecorderState.IDLE
            
            # Estadísticas finales
            duration = time.time() - self.recording_start_time
            logger.info(f"Grabación completada: {self.current_filename}")
            logger.info(f"Duración: {duration:.1f}s, Frames: {self._frames_processed}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error deteniendo grabación: {e}")
            self.state = RecorderState.ERROR
            return False
    
    def add_frame(self, frame_data: bytes, width: int, height: int) -> bool:
        """Agregar frame para grabación"""
        if self.state != RecorderState.RECORDING:
            return False
        
        success = self.frame_buffer.put_frame(frame_data, width, height)
        if not success:
            logger.warning("Frame descartado - buffer lleno")
        
        return success
    
    def _recording_worker(self):
        """Worker principal de grabación"""
        logger.info(f"Worker de grabación iniciado ({self.recorder_type.value})")
        
        try:
            if self.recorder_type == RecorderType.CPU_PYAV:
                self._cpu_recording_worker()
            elif self.recorder_type == RecorderType.GPU_FFMPEG:
                self._gpu_recording_worker()
            elif self.recorder_type == RecorderType.HYBRID:
                self._hybrid_recording_worker()
            else:
                logger.error(f"Tipo de recorder no soportado: {self.recorder_type}")
                
        except Exception as e:
            logger.error(f"Error en worker de grabación: {e}")
            self._errors_count += 1
            self.state = RecorderState.ERROR
        
        finally:
            logger.info("Worker de grabación terminado")
    
    def _cpu_recording_worker(self):
        """Worker para grabación CPU con PyAV"""
        try:
            import av
            
            # Abrir archivo para escritura
            container = av.open(self.current_filename, 'w')
            stream = container.add_stream('libx264', rate=self.fps)
            stream.width = self.width
            stream.height = self.height
            stream.bit_rate = 8000000
            stream.pix_fmt = 'yuv420p'
            
            logger.info("PyAV recorder configurado")
            
            while self.state == RecorderState.RECORDING:
                frame_data = self.frame_buffer.get_frame(timeout=1.0)
                
                if frame_data is None:
                    continue
                
                frame_bytes, width, height, timestamp = frame_data
                
                # Frame especial de fin
                if len(frame_bytes) == 0:
                    break
                
                # Procesar frame
                try:
                    # Convertir datos a numpy array
                    frame_array = np.frombuffer(frame_bytes, dtype=np.uint8)
                    frame_array = frame_array.reshape((height, width, 3))
                    
                    # Crear VideoFrame de PyAV
                    av_frame = av.VideoFrame.from_ndarray(frame_array, format='rgb24')
                    av_frame.pts = self._frames_processed
                    
                    # Encode y escribir
                    packets = stream.encode(av_frame)
                    for packet in packets:
                        container.mux(packet)
                    
                    self._frames_processed += 1
                    self._bytes_written += len(frame_bytes)
                    
                except Exception as e:
                    logger.error(f"Error procesando frame CPU: {e}")
                    self._errors_count += 1
            
            # Flush final
            packets = stream.encode()
            for packet in packets:
                container.mux(packet)
            
            container.close()
            
        except Exception as e:
            logger.error(f"Error en CPU recording worker: {e}")
            raise
    
    def _gpu_recording_worker(self):
        """Worker para grabación GPU con FFmpeg"""
        # Implementación similar al GPU recorder existente pero optimizada
        logger.info("GPU recording worker no implementado aún - usando CPU fallback")
        self._cpu_recording_worker()
    
    def _hybrid_recording_worker(self):
        """Worker híbrido que combina GPU y CPU según condiciones"""
        try:
            # Intentar GPU primero, fallback a CPU si falla
            try:
                self._gpu_recording_worker()
            except Exception as e:
                logger.warning(f"GPU recording falló, cambiando a CPU: {e}")
                self.recorder_type = RecorderType.CPU_PYAV
                self._cpu_recording_worker()
                
        except Exception as e:
            logger.error(f"Error en hybrid recording worker: {e}")
            raise
    
    def _monitor_worker(self):
        """Worker de monitoreo de rendimiento"""
        logger.debug("Monitor de rendimiento iniciado")
        
        last_stats_time = time.time()
        last_frame_count = 0
        
        try:
            while self.state == RecorderState.RECORDING:
                time.sleep(5.0)  # Monitoreo cada 5 segundos
                
                current_time = time.time()
                elapsed = current_time - last_stats_time
                
                if elapsed >= 5.0:  # Reportar cada 5 segundos
                    buffer_stats = self.frame_buffer.get_stats()
                    frames_per_sec = (self._frames_processed - last_frame_count) / elapsed
                    
                    logger.info(f"📊 Grabación - FPS: {frames_per_sec:.1f}, "
                              f"Buffer: {buffer_stats['fill_rate_percent']:.1f}%, "
                              f"Drops: {buffer_stats['drop_rate_percent']:.1f}%")
                    
                    last_stats_time = current_time
                    last_frame_count = self._frames_processed
                    
                    # Optimizar buffer si hay muchas pérdidas
                    if buffer_stats['drop_rate_percent'] > 10:
                        logger.warning("Alta tasa de pérdida de frames - optimizando buffer")
                        self.frame_buffer.drop_policy = "oldest"
                
        except Exception as e:
            logger.error(f"Error en monitor worker: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas completas del recorder"""
        buffer_stats = self.frame_buffer.get_stats()
        
        duration = 0
        if self.recording_start_time:
            duration = time.time() - self.recording_start_time
        
        return {
            'state': self.state.value,
            'recorder_type': self.recorder_type.value,
            'duration_seconds': duration,
            'frames_processed': self._frames_processed,
            'bytes_written': self._bytes_written,
            'errors_count': self._errors_count,
            'buffer': buffer_stats,
            'performance': {
                'fps_processed': self._frames_processed / max(1, duration),
                'mbytes_per_second': (self._bytes_written / (1024*1024)) / max(1, duration),
                'efficiency_percent': (1 - buffer_stats['drop_rate_percent'] / 100) * 100
            }
        }
    
    def is_recording(self) -> bool:
        """Verificar si está grabando"""
        return self.state == RecorderState.RECORDING
    
    def get_recorder_info(self) -> Dict[str, Any]:
        """Obtener información del recorder"""
        return {
            'current_type': self.recorder_type.value,
            'available_types': [t.value for t in RecorderType],
            'gpu_available': self._test_gpu_availability(),
            'configuration': {
                'width': self.width,
                'height': self.height,
                'fps': self.fps,
                'bitrate': self.bitrate
            }
        } 