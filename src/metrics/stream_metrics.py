# -*- coding: utf-8 -*-
"""
Sistema híbrido de métricas de streaming
Monitor de métricas con captura multi-nivel y métricas suavizadas/instantáneas
"""

import time
from collections import deque
from typing import Dict, Optional, Any, Tuple
from ..utils.constants import (
    DEFAULT_METRICS_WINDOW_SECONDS,
    MAX_FPS_THEORETICAL,
    MAX_FRAME_INTERVALS_HISTORY,
    NETWORK_OVERHEAD_ESTIMATE
)
from ..utils.logger import setup_logger

logger = setup_logger("HybridStreamMetrics")

class SlidingWindow:
    """Ventana deslizante para métricas suavizadas"""
    
    def __init__(self, window_seconds: float = 5.0):
        self.window_seconds = window_seconds
        self.data = deque()  # [(timestamp, value), ...]
        
    def add_value(self, value: float, timestamp: Optional[float] = None):
        """Agregar valor con timestamp"""
        if timestamp is None:
            timestamp = time.time()
        
        self.data.append((timestamp, value))
        self._cleanup_old_data(timestamp)
    
    def _cleanup_old_data(self, current_time: float):
        """Eliminar datos fuera de la ventana"""
        cutoff_time = current_time - self.window_seconds
        while self.data and self.data[0][0] < cutoff_time:
            self.data.popleft()
    
    def get_average(self) -> float:
        """Obtener promedio de la ventana"""
        if not self.data:
            return 0.0
        return sum(value for _, value in self.data) / len(self.data)
    
    def get_sum(self) -> float:
        """Obtener suma de la ventana"""
        return sum(value for _, value in self.data)
    
    def get_count(self) -> int:
        """Obtener número de muestras en la ventana"""
        return len(self.data)
    
    def get_rate(self) -> float:
        """Obtener tasa (count / window_time)"""
        if not self.data or self.window_seconds <= 0:
            return 0.0
        
        # Usar tiempo real transcurrido si es menor que window_seconds
        if len(self.data) >= 2:
            actual_time = self.data[-1][0] - self.data[0][0]
            if actual_time > 0:
                return len(self.data) / actual_time
        
        return len(self.data) / self.window_seconds


class HybridStreamMetrics:
    """Monitor híbrido de métricas con captura multi-nivel"""
    
    def __init__(self, window_seconds: float = DEFAULT_METRICS_WINDOW_SECONDS):
        self.window_seconds = window_seconds
        
        # Métricas suavizadas (con ventana deslizante)
        self.fps_window = SlidingWindow(window_seconds)
        self.bitrate_window = SlidingWindow(window_seconds)
        self.frame_size_window = SlidingWindow(window_seconds)
        self.latency_window = SlidingWindow(window_seconds)
        
        # Métricas instantáneas
        self.current_fps = 0.0
        self.current_bitrate_kbps = 0.0
        self.current_latency_ms = 0.0
        self.current_frame_size = 0
        
        # Métricas acumulativas (sin ventana)
        self.total_mb_received = 0.0
        self.total_frames = 0
        self.session_start_time = time.time()
        
        # Para cálculo de latencia multi-nivel
        self.network_timestamps = {}  # {buffer_id: network_time}
        self.decoder_timestamps = {}  # {buffer_id: decode_time}
        self.display_timestamps = {}  # {buffer_id: display_time}
        
        # Control de FPS filtrado
        self.last_fps_time = None
        self.min_frame_interval = 1.0 / MAX_FPS_THEORETICAL
        
        # Frame timing para latencia
        self.frame_intervals = deque(maxlen=MAX_FRAME_INTERVALS_HISTORY)
        self.last_frame_time = None
        
        logger.info(f"HybridStreamMetrics inicializado (ventana: {window_seconds}s)")
    
    # =================================================================
    # PROPIEDADES DE COMPATIBILIDAD HACIA ATRÁS
    # =================================================================
    
    @property
    def frame_count(self):
        """Compatibilidad: número total de frames procesados"""
        return self.total_frames
    
    @property
    def total_bytes(self):
        """Compatibilidad: total de bytes recibidos"""
        return int(self.total_mb_received * 1024 * 1024)
    
    @property
    def start_time(self):
        """Compatibilidad: tiempo de inicio de sesión"""
        return self.session_start_time
    
    def reset(self):
        """Resetear todas las métricas"""
        self.fps_window = SlidingWindow(self.window_seconds)
        self.bitrate_window = SlidingWindow(self.window_seconds)
        self.frame_size_window = SlidingWindow(self.window_seconds)
        self.latency_window = SlidingWindow(self.window_seconds)
        
        self.current_fps = 0.0
        self.current_bitrate_kbps = 0.0
        self.current_latency_ms = 0.0
        self.current_frame_size = 0
        
        self.total_mb_received = 0.0
        self.total_frames = 0
        self.session_start_time = time.time()
        
        self.network_timestamps.clear()
        self.decoder_timestamps.clear()
        self.display_timestamps.clear()
        
        self.last_fps_time = None
        self.frame_intervals.clear()
        self.last_frame_time = None
        
        logger.debug("Métricas híbridas reseteadas")
    
    # =================================================================
    # MÉTODOS DE CAPTURA MULTI-NIVEL
    # =================================================================
    
    def add_network_data(self, buffer_size: int, buffer_id: Optional[str] = None):
        """Capturar datos del nivel de red (rtspsrc)"""
        current_time = time.time()
        
        # Actualizar métricas acumulativas
        self.total_mb_received += buffer_size / (1024 * 1024)
        
        # Agregar a ventana deslizante para bitrate suavizado
        self.bitrate_window.add_value(buffer_size * 8)  # bits
        self.frame_size_window.add_value(buffer_size)
        
        # Calcular bitrate instantáneo
        self.current_bitrate_kbps = (buffer_size * 8) / 1000  # Kbps aproximado
        self.current_frame_size = buffer_size
        
        # Guardar timestamp para latencia multi-nivel
        if buffer_id:
            self.network_timestamps[buffer_id] = current_time
        
        logger.debug(f"Red: {buffer_size} bytes, bitrate: {self.current_bitrate_kbps:.1f} Kbps")
    
    def add_decoded_frame(self, buffer_id: Optional[str] = None):
        """Capturar frame decodificado (decoder)"""
        current_time = time.time()
        
        # Control de FPS filtrado para evitar falsos positivos
        if self.last_fps_time is None or (current_time - self.last_fps_time) >= self.min_frame_interval:
            self.total_frames += 1
            
            # Agregar frame a ventana FPS
            self.fps_window.add_value(1.0)  # 1 frame
            
            # Calcular FPS instantáneo basado en intervalo
            if self.last_fps_time:
                frame_interval = current_time - self.last_fps_time
                self.current_fps = 1.0 / frame_interval if frame_interval > 0 else 0
                
                # Agregar intervalo para latencia promedio
                self.frame_intervals.append(frame_interval)
            
            self.last_fps_time = current_time
        
        # Timestamp para latencia multi-nivel
        if buffer_id:
            self.decoder_timestamps[buffer_id] = current_time
        
        logger.debug(f"Frame decodificado, FPS actual: {self.current_fps:.1f}")
    
    def add_display_frame(self, buffer_id: Optional[str] = None):
        """Capturar frame mostrado (videosink)"""
        current_time = time.time()
        
        # Timestamp para latencia multi-nivel
        if buffer_id:
            self.display_timestamps[buffer_id] = current_time
            
            # Calcular latencia end-to-end si tenemos todos los timestamps
            if buffer_id in self.network_timestamps:
                network_time = self.network_timestamps[buffer_id]
                latency_ms = (current_time - network_time) * 1000
                
                self.current_latency_ms = latency_ms
                self.latency_window.add_value(latency_ms)
                
                # Limpiar timestamps antiguos
                self.network_timestamps.pop(buffer_id, None)
                self.decoder_timestamps.pop(buffer_id, None)
                self.display_timestamps.pop(buffer_id, None)
                
                logger.debug(f"Latencia end-to-end: {latency_ms:.1f}ms")
    
    # =================================================================
    # COMPATIBILIDAD CON SISTEMA ANTERIOR
    # =================================================================
    
    def add_frame(self, frame_size_bytes: int = 0):
        """Método compatible para agregar frame (como antes)"""
        # Simular captura multi-nivel con un solo método
        buffer_id = f"frame_{int(time.time() * 1000000)}"  # Microsecond ID
        
        if frame_size_bytes > 0:
            self.add_network_data(frame_size_bytes, buffer_id)
        
        self.add_decoded_frame(buffer_id)
        self.add_display_frame(buffer_id)
    
    # =================================================================
    # MÉTRICAS PÚBLICAS
    # =================================================================
    
    def get_metrics(self, smooth: bool = True) -> Dict[str, Any]:
        """Obtener métricas (suavizadas o instantáneas)"""
        if smooth:
            return self.get_smooth_metrics()
        else:
            return self.get_instant_metrics()
    
    def get_smooth_metrics(self) -> Dict[str, Any]:
        """Métricas suavizadas con ventana deslizante"""
        # FPS suavizado
        fps = self.fps_window.get_rate()
        
        # Bitrate suavizado (promedio de bits en ventana)
        if self.fps_window.get_count() > 0:
            total_bits = self.bitrate_window.get_sum()
            bitrate_kbps = (total_bits / self.window_seconds) / 1000
            bitrate_mbps = bitrate_kbps / 1000
        else:
            bitrate_kbps = 0
            bitrate_mbps = 0
        
        # Data rate suavizado
        data_rate_kbps = bitrate_kbps / 8  # KBps
        
        # Latencia suavizada
        latency_ms = self.latency_window.get_average()
        if latency_ms == 0:  # Fallback a estimación
            latency_ms = self.get_estimated_latency_ms()
        
        return {
            'fps': fps,
            'bitrate_kbps': bitrate_kbps,
            'bitrate_mbps': bitrate_mbps,
            'data_rate_kbps': data_rate_kbps,
            'latency_ms': latency_ms,
            'total_mb': self.total_mb_received,
            'type': 'smooth'
        }
    
    def get_instant_metrics(self) -> Dict[str, Any]:
        """Métricas instantáneas (sin suavizar)"""
        return {
            'fps': self.current_fps,
            'bitrate_kbps': self.current_bitrate_kbps,
            'bitrate_mbps': self.current_bitrate_kbps / 1000,
            'data_rate_kbps': self.current_bitrate_kbps / 8,
            'latency_ms': self.current_latency_ms,
            'total_mb': self.total_mb_received,
            'type': 'instant'
        }
    
    # =================================================================
    # MÉTODOS INDIVIDUALES (COMPATIBILIDAD)
    # =================================================================
    
    def get_fps(self) -> float:
        """FPS suavizado (método compatible)"""
        return self.fps_window.get_rate()
    
    def get_fps_instant(self) -> float:
        """FPS instantáneo"""
        return self.current_fps
    
    def get_bitrate_kbps(self) -> float:
        """Bitrate suavizado en Kbps"""
        if self.fps_window.get_count() > 0:
            total_bits = self.bitrate_window.get_sum()
            return (total_bits / self.window_seconds) / 1000
        return 0
    
    def get_bitrate_mbps(self) -> float:
        """Bitrate suavizado en Mbps"""
        return self.get_bitrate_kbps() / 1000
    
    def get_data_rate_kbps(self) -> float:
        """Data rate suavizado en KBps"""
        return self.get_bitrate_kbps() / 8
    
    def get_estimated_latency_ms(self) -> float:
        """Latencia estimada basada en frame intervals"""
        if self.frame_intervals:
            avg_interval = sum(self.frame_intervals) / len(self.frame_intervals)
            return (avg_interval * 1000) + NETWORK_OVERHEAD_ESTIMATE
        return NETWORK_OVERHEAD_ESTIMATE
    
    def get_latency_ms(self) -> float:
        """Latencia suavizada o estimada"""
        latency = self.latency_window.get_average()
        return latency if latency > 0 else self.get_estimated_latency_ms()
    
    def get_total_mb_received(self) -> float:
        """Total acumulado en MB"""
        return self.total_mb_received
    
    def get_session_duration(self) -> float:
        """Duración de la sesión en segundos"""
        return time.time() - self.session_start_time
    
    def get_debug_info(self) -> Dict[str, Any]:
        """Información de debug"""
        return {
            'window_seconds': self.window_seconds,
            'fps_samples': self.fps_window.get_count(),
            'bitrate_samples': self.bitrate_window.get_count(),
            'total_frames': self.total_frames,
            'session_duration': self.get_session_duration(),
            'pending_network_timestamps': len(self.network_timestamps),
            'pending_decoder_timestamps': len(self.decoder_timestamps),
            'pending_display_timestamps': len(self.display_timestamps)
        }

    def get_window_info(self) -> Dict[str, Any]:
        """Información de ventana con estadísticas (compatibilidad)"""
        return {
            'window_seconds': self.window_seconds,
            'packets_in_window': self.fps_window.get_count(),  # Compatible con UI existente
            'frames_in_window': self.fps_window.get_count(),
            'total_frames': self.total_frames,
            'total_mb': self.total_mb_received,
            'session_duration': self.get_session_duration(),
            'memory_usage': {
                'fps_window_count': self.fps_window.get_count(),
                'bitrate_window_count': self.bitrate_window.get_count(),
                'latency_window_count': self.latency_window.get_count(),
                'frame_intervals_count': len(self.frame_intervals)
            }
        }


# Alias para compatibilidad hacia atrás
StreamMetrics = HybridStreamMetrics 