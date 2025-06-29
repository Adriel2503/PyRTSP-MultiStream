# -*- coding: utf-8 -*-
"""
Sistema de monitoreo de rendimiento para medir impacto de optimizaciones
Proporciona métricas detalladas de CPU, memoria, GPU y throughput
"""

import time
import psutil
import threading
import collections
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass

from .logger import setup_logger

logger = setup_logger("PerformanceMonitor")

@dataclass
class PerformanceSnapshot:
    """Snapshot de métricas de rendimiento en un momento específico"""
    timestamp: float
    cpu_percent: float
    memory_percent: float
    memory_mb: float
    gpu_percent: Optional[float]
    gpu_memory_mb: Optional[float]
    fps: float
    frame_drops: int
    custom_metrics: Dict[str, Any]

class PerformanceMonitor:
    """Monitor de rendimiento en tiempo real con histórico"""
    
    def __init__(self, sample_interval: float = 1.0, history_size: int = 300):
        self.sample_interval = sample_interval
        self.history_size = history_size
        
        # Historia de snapshots
        self.snapshots = collections.deque(maxlen=history_size)
        
        # Control de monitoreo
        self.is_monitoring = False
        self.monitor_thread = None
        self._lock = threading.RLock()
        
        # Callbacks para métricas custom
        self.custom_metric_callbacks = {}
        
        # Estadísticas de sesión
        self.session_start_time = time.time()
        self.total_frames_monitored = 0
        self.peak_cpu = 0.0
        self.peak_memory = 0.0
        
        # Detectar GPU
        self.gpu_available = self._detect_gpu()
        
        logger.info(f"PerformanceMonitor inicializado (GPU: {'Sí' if self.gpu_available else 'No'})")
    
    def _detect_gpu(self) -> bool:
        """Detectar si hay GPU disponible"""
        try:
            # Intentar detectar GPU NVIDIA
            import subprocess
            result = subprocess.run(['nvidia-smi'], capture_output=True, text=True)
            if result.returncode == 0:
                return True
        except:
            pass
        
        try:
            # Intentar detectar GPU AMD
            import subprocess
            result = subprocess.run(['rocm-smi'], capture_output=True, text=True)
            if result.returncode == 0:
                return True
        except:
            pass
        
        # Si no se puede detectar GPU específica, asumir que no hay
        return False
    
    def register_custom_metric(self, name: str, callback: Callable):
        """Registrar callback para métrica personalizada"""
        self.custom_metric_callbacks[name] = callback
        logger.debug(f"Métrica personalizada registrada: {name}")
    
    def unregister_custom_metric(self, name: str):
        """Desregistrar métrica personalizada"""
        if name in self.custom_metric_callbacks:
            del self.custom_metric_callbacks[name]
            logger.debug(f"Métrica personalizada desregistrada: {name}")
        else:
            logger.warning(f"Métrica {name} no encontrada para desregistrar")
    
    def start_monitoring(self):
        """Iniciar monitoreo de rendimiento"""
        with self._lock:
            if self.is_monitoring:
                return
            
            self.is_monitoring = True
            self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
            self.monitor_thread.start()
            logger.info("Monitoreo de rendimiento iniciado")
    
    def stop_monitoring(self):
        """Detener monitoreo de rendimiento"""
        with self._lock:
            self.is_monitoring = False
            if self.monitor_thread:
                self.monitor_thread.join(timeout=2.0)
            logger.info("Monitoreo de rendimiento detenido")
    
    def _monitoring_loop(self):
        """Loop principal de monitoreo"""
        while self.is_monitoring:
            try:
                # Recopilar métricas del sistema
                cpu_percent = psutil.cpu_percent(interval=None)
                memory = psutil.virtual_memory()
                
                # Métricas personalizadas
                custom_metrics = {}
                for name, callback in self.custom_metric_callbacks.items():
                    try:
                        custom_metrics[name] = callback()
                    except Exception as e:
                        logger.warning(f"Error obteniendo métrica {name}: {e}")
                
                # Crear snapshot
                snapshot = PerformanceSnapshot(
                    timestamp=time.time(),
                    cpu_percent=cpu_percent,
                    memory_percent=memory.percent,
                    memory_mb=memory.used / (1024 * 1024),
                    gpu_percent=None,  # Implementar si es necesario
                    gpu_memory_mb=None,
                    fps=0.0,  # Se actualiza externamente
                    frame_drops=0,
                    custom_metrics=custom_metrics
                )
                
                with self._lock:
                    self.snapshots.append(snapshot)
                    self.peak_cpu = max(self.peak_cpu, cpu_percent)
                    self.peak_memory = max(self.peak_memory, memory.percent)
                
                time.sleep(self.sample_interval)
                
            except Exception as e:
                logger.error(f"Error en loop de monitoreo: {e}")
                time.sleep(1.0)
    
    def get_current_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas actuales"""
        with self._lock:
            if not self.snapshots:
                return {
                    'cpu_percent': 0.0,
                    'memory_percent': 0.0,
                    'memory_mb': 0.0,
                    'gpu_available': self.gpu_available,
                    'samples_collected': 0
                }
            
            latest = self.snapshots[-1]
            return {
                'cpu_percent': latest.cpu_percent,
                'memory_percent': latest.memory_percent,
                'memory_mb': latest.memory_mb,
                'gpu_percent': latest.gpu_percent,
                'gpu_memory_mb': latest.gpu_memory_mb,
                'gpu_available': self.gpu_available,
                'custom_metrics': latest.custom_metrics,
                'samples_collected': len(self.snapshots),
                'peak_cpu': self.peak_cpu,
                'peak_memory': self.peak_memory
            }
    
    def get_historical_stats(self, duration_seconds: Optional[int] = None) -> Dict[str, Any]:
        """Obtener estadísticas históricas del monitoreo"""
        with self._lock:
            if not self.snapshots:
                return {
                    'total_samples': 0,
                    'duration_seconds': duration_seconds or 0,
                    'avg_cpu': 0.0,
                    'avg_memory': 0.0,
                    'peak_cpu': 0.0,
                    'peak_memory': 0.0,
                    'cpu_trend': [],
                    'memory_trend': []
                }
            
            # Filtrar snapshots por duración si se especifica
            snapshots_to_analyze = list(self.snapshots)
            if duration_seconds is not None and snapshots_to_analyze:
                current_time = time.time()
                cutoff_time = current_time - duration_seconds
                snapshots_to_analyze = [s for s in snapshots_to_analyze if s.timestamp >= cutoff_time]
            
            if not snapshots_to_analyze:
                return {
                    'total_samples': 0,
                    'duration_seconds': duration_seconds or 0,
                    'avg_cpu': 0.0,
                    'avg_memory': 0.0,
                    'peak_cpu': 0.0,
                    'peak_memory': 0.0,
                    'cpu_trend': [],
                    'memory_trend': []
                }
            
            # Calcular estadísticas agregadas
            cpu_values = [s.cpu_percent for s in snapshots_to_analyze]
            memory_values = [s.memory_percent for s in snapshots_to_analyze]
            
            first_timestamp = snapshots_to_analyze[0].timestamp
            last_timestamp = snapshots_to_analyze[-1].timestamp
            actual_duration = last_timestamp - first_timestamp
            
            return {
                'total_samples': len(snapshots_to_analyze),
                'duration_seconds': duration_seconds or actual_duration,
                'avg_cpu': sum(cpu_values) / len(cpu_values),
                'avg_memory': sum(memory_values) / len(memory_values),
                'peak_cpu': max(cpu_values),
                'peak_memory': max(memory_values),
                'min_cpu': min(cpu_values),
                'min_memory': min(memory_values),
                'cpu_trend': cpu_values[-20:],  # Últimos 20 valores
                'memory_trend': memory_values[-20:],
                'session_duration': time.time() - self.session_start_time,
                'samples_per_second': len(snapshots_to_analyze) / max(actual_duration, 1)
            }
    
    def generate_report(self) -> str:
        """Generar reporte de rendimiento completo"""
        report = []
        report.append("=== REPORTE DE RENDIMIENTO WELLTEP ===")
        report.append(f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("=== FIN DEL REPORTE ===")
        return "\n".join(report)

# Instancia global
_performance_monitor = None

def get_performance_monitor():
    """Obtener instancia singleton del monitor de rendimiento"""
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = PerformanceMonitor()
    return _performance_monitor 