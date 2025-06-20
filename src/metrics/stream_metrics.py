# -*- coding: utf-8 -*-
"""
Sistema de métricas de streaming con ventanas deslizantes
Monitor de métricas de streaming en tiempo real con ventanas deslizantes
"""

import time
from ..utils.constants import (
    DEFAULT_METRICS_WINDOW_SECONDS,
    MAX_FPS_THEORETICAL,
    MAX_FRAME_INTERVALS_HISTORY,
    NETWORK_OVERHEAD_ESTIMATE
)
from ..utils.logger import setup_logger

logger = setup_logger("StreamMetrics")

class StreamMetrics:
    """Monitor de métricas de streaming en tiempo real con ventanas deslizantes"""
    
    def __init__(self, window_seconds=DEFAULT_METRICS_WINDOW_SECONDS):
        self.window_seconds = window_seconds  # Ventana de cálculo en segundos
        self.reset()
        logger.info(f"StreamMetrics inicializado con ventana de {window_seconds}s")
        
    def reset(self):
        """Resetear todas las métricas"""
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
        
        logger.debug("Métricas reseteadas")
        
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
        min_frame_interval = 1.0 / MAX_FPS_THEORETICAL  # Máximo FPS teórico
        
        if self.last_fps_time is None or (current_time - self.last_fps_time) >= min_frame_interval:
            self.fps_timestamps.append(current_time)
            self.last_fps_time = current_time
            
            # Limpiar timestamps antiguos
            self.fps_timestamps = [t for t in self.fps_timestamps if t >= cutoff_time]
        
        # Calcular intervalos entre frames para latencia
        if self.last_frame_time:
            frame_interval = current_time - self.last_frame_time
            self.frame_times.append(frame_interval)
            
            # Mantener solo últimos intervalos configurados
            if len(self.frame_times) > MAX_FRAME_INTERVALS_HISTORY:
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
        return frame_time + NETWORK_OVERHEAD_ESTIMATE
    
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