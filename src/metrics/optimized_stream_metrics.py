# -*- coding: utf-8 -*-
"""
Sistema de métricas optimizado con mejor rendimiento y gestión de memoria
Utiliza estructuras de datos más eficientes y cálculos optimizados
"""

import time
import collections
import numpy as np
from threading import RLock
from typing import Tuple, Optional

from ..utils.constants import (
    DEFAULT_METRICS_WINDOW_SECONDS,
    MAX_FPS_THEORETICAL,
    NETWORK_OVERHEAD_ESTIMATE
)
from ..utils.logger import setup_logger
from ..core.thread_pool_manager import get_thread_pool_manager

logger = setup_logger("OptimizedStreamMetrics")

class OptimizedStreamMetrics:
    """Sistema de métricas optimizado para alto rendimiento"""
    
    def __init__(self, window_seconds=DEFAULT_METRICS_WINDOW_SECONDS):
        self.window_seconds = window_seconds
        self.min_frame_interval = 1.0 / MAX_FPS_THEORETICAL
        
        # Thread safety
        self._lock = RLock()
        
        # Usar deque para mejor rendimiento O(1) en append/popleft
        self.frame_data = collections.deque(maxlen=1000)  # Límite de memoria
        self.fps_timestamps = collections.deque(maxlen=300)  # ~10 segundos @ 30fps
        self.frame_intervals = collections.deque(maxlen=100)  # Para latencia
        
        # Cache para evitar recálculos
        self._cache = {}
        self._cache_time = 0
        self._cache_ttl = 0.1  # 100ms TTL para cache
        
        # Pre-computed arrays para numpy
        self._np_array_cache = None
        self._np_cache_time = 0
        
        # Pool de threads para cálculos pesados
        self.thread_pool = get_thread_pool_manager()
        
        self.reset()
        logger.info(f"OptimizedStreamMetrics inicializado (ventana: {window_seconds}s)")
    
    def reset(self):
        """Resetear métricas de forma optimizada"""
        with self._lock:
            self.start_time = time.time()
            self.frame_count = 0
            self.total_bytes_received = 0
            
            self.frame_data.clear()
            self.fps_timestamps.clear()
            self.frame_intervals.clear()
            
            self._clear_cache()
            self.last_frame_time = None
            self.last_fps_time = None
            
        logger.debug("Métricas optimizadas reseteadas")
    
    def add_frame(self, frame_size_bytes: int = 0):
        """Agregar frame con optimizaciones de rendimiento"""
        current_time = time.time()
        
        with self._lock:
            self.frame_count += 1
            self.total_bytes_received += frame_size_bytes
            
            # Agregar datos de frame (timestamp, size)
            self.frame_data.append((current_time, frame_size_bytes))
            
            # Filtrado de FPS optimizado
            if (self.last_fps_time is None or 
                (current_time - self.last_fps_time) >= self.min_frame_interval):
                self.fps_timestamps.append(current_time)
                self.last_fps_time = current_time
            
            # Calcular intervalo para latencia
            if self.last_frame_time is not None:
                interval = current_time - self.last_frame_time
                self.frame_intervals.append(interval)
            
            self.last_frame_time = current_time
            
            # Limpiar cache si ha expirado
            if current_time - self._cache_time > self._cache_ttl:
                self._clear_cache()
    
    def _clear_cache(self):
        """Limpiar cache de cálculos"""
        self._cache.clear()
        self._cache_time = time.time()
        self._np_array_cache = None
    
    def _get_cached_or_compute(self, key: str, compute_func, *args):
        """Sistema de cache para evitar recálculos"""
        if key in self._cache:
            return self._cache[key]
        
        result = compute_func(*args)
        self._cache[key] = result
        return result
    
    def _filter_by_window(self, data_deque, current_time: float = None) -> list:
        """Filtrar datos por ventana temporal de forma optimizada"""
        if current_time is None:
            current_time = time.time()
        
        cutoff_time = current_time - self.window_seconds
        
        # Optimización: buscar desde el final (datos más recientes)
        result = []
        for item in reversed(data_deque):
            if isinstance(item, tuple):
                timestamp = item[0]
            else:
                timestamp = item
            
            if timestamp >= cutoff_time:
                result.append(item)
            else:
                break  # Como están ordenados, podemos parar aquí
        
        return list(reversed(result))
    
    def get_fps(self) -> float:
        """FPS optimizado con cache"""
        with self._lock:
            return self._get_cached_or_compute("fps", self._compute_fps)
    
    def _compute_fps(self) -> float:
        """Cálculo interno de FPS optimizado"""
        if len(self.fps_timestamps) < 2:
            return 0.0
        
        current_time = time.time()
        valid_timestamps = self._filter_by_window(self.fps_timestamps, current_time)
        
        if len(valid_timestamps) < 2:
            return 0.0
        
        time_span = valid_timestamps[-1] - valid_timestamps[0]
        if time_span > 0:
            return (len(valid_timestamps) - 1) / time_span
        
        return len(valid_timestamps) / self.window_seconds
    
    def get_bitrate_kbps(self) -> float:
        """Bitrate optimizado con cache"""
        with self._lock:
            return self._get_cached_or_compute("bitrate_kbps", self._compute_bitrate_kbps)
    
    def _compute_bitrate_kbps(self) -> float:
        """Cálculo interno de bitrate optimizado"""
        if len(self.frame_data) < 2:
            return 0.0
        
        current_time = time.time()
        valid_frames = self._filter_by_window(self.frame_data, current_time)
        
        if not valid_frames:
            return 0.0
        
        total_bytes = sum(frame[1] for frame in valid_frames)
        
        if total_bytes > 0 and self.window_seconds > 0:
            bits_per_second = (total_bytes * 8) / self.window_seconds
            return bits_per_second / 1000
        
        return 0.0
    
    def get_bitrate_mbps(self) -> float:
        """Bitrate en Mbps"""
        return self.get_bitrate_kbps() / 1000
    
    def get_data_rate_kbps(self) -> float:
        """Tasa de datos en KBps"""
        bitrate_kbps = self.get_bitrate_kbps()
        return bitrate_kbps / 8  # Convertir bits a bytes
    
    def get_avg_frame_time_ms(self) -> float:
        """Tiempo promedio entre frames optimizado"""
        with self._lock:
            return self._get_cached_or_compute("frame_time_ms", self._compute_frame_time_ms)
    
    def _compute_frame_time_ms(self) -> float:
        """Cálculo interno de tiempo de frame"""
        if not self.frame_intervals:
            return 0.0
        
        # Usar numpy para cálculo más rápido si hay muchos datos
        if len(self.frame_intervals) > 10:
            intervals_array = np.array(list(self.frame_intervals)[-50:])  # Últimos 50
            return float(np.mean(intervals_array) * 1000)
        else:
            avg_interval = sum(self.frame_intervals) / len(self.frame_intervals)
            return avg_interval * 1000
    
    def get_estimated_latency_ms(self) -> float:
        """Latencia estimada total"""
        frame_time = self.get_avg_frame_time_ms()
        return frame_time + NETWORK_OVERHEAD_ESTIMATE
    
    def get_total_mb_received(self) -> float:
        """Total acumulado en MB"""
        with self._lock:
            return self.total_bytes_received / (1024 * 1024)
    
    def get_window_info(self) -> dict:
        """Información de ventana con estadísticas de rendimiento"""
        with self._lock:
            current_time = time.time()
            valid_frames = self._filter_by_window(self.frame_data, current_time)
            
            return {
                'window_seconds': self.window_seconds,
                'frames_in_window': len(valid_frames),
                'total_frames': self.frame_count,
                'cache_hits': len(self._cache),
                'cache_age_ms': (current_time - self._cache_time) * 1000,
                'memory_usage': {
                    'frame_data_count': len(self.frame_data),
                    'fps_timestamps_count': len(self.fps_timestamps),
                    'frame_intervals_count': len(self.frame_intervals)
                }
            }
    
    def get_performance_stats(self) -> dict:
        """Estadísticas de rendimiento del sistema de métricas"""
        with self._lock:
            return {
                'cache_efficiency': len(self._cache) / max(1, self.frame_count) * 100,
                'memory_usage_kb': (
                    len(self.frame_data) * 16 +  # 2 floats por frame
                    len(self.fps_timestamps) * 8 +  # 1 float por timestamp
                    len(self.frame_intervals) * 8    # 1 float por interval
                ) / 1024,
                'data_structures': {
                    'frame_data_maxlen': self.frame_data.maxlen,
                    'fps_timestamps_maxlen': self.fps_timestamps.maxlen,
                    'frame_intervals_maxlen': self.frame_intervals.maxlen
                }
            }
    
    def optimize_memory(self):
        """Optimización manual de memoria"""
        with self._lock:
            # Limpiar datos antiguos más agresivamente
            current_time = time.time()
            cutoff_time = current_time - (self.window_seconds * 2)  # 2x ventana
            
            # Filtrar frame_data
            while self.frame_data and self.frame_data[0][0] < cutoff_time:
                self.frame_data.popleft()
            
            # Filtrar fps_timestamps
            while self.fps_timestamps and self.fps_timestamps[0] < cutoff_time:
                self.fps_timestamps.popleft()
            
            # Limpiar cache
            self._clear_cache()
            
            logger.debug("Optimización de memoria completada")

# Wrapper para compatibilidad con StreamMetrics existente
class StreamMetrics(OptimizedStreamMetrics):
    """Wrapper para mantener compatibilidad con código existente"""
    
    def get_fps_simple(self):
        """Método de compatibilidad"""
        return self.get_fps() 