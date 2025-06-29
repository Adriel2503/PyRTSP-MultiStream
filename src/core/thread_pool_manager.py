# -*- coding: utf-8 -*-
"""
Administrador centralizado de pool de threads para optimización de rendimiento
Evita crear/destruir threads constantemente y mejora la gestión de recursos
"""

import threading
import queue
import concurrent.futures
from contextlib import contextmanager
from typing import Callable, Any, Optional

from ..utils.logger import setup_logger

logger = setup_logger("ThreadPoolManager")

class ThreadPoolManager:
    """Administrador centralizado de threads para optimización de rendimiento"""
    
    def __init__(self):
        # Pool para tareas I/O (grabación, archivos)
        self.io_pool = concurrent.futures.ThreadPoolExecutor(
            max_workers=3,
            thread_name_prefix="welltep_io"
        )
        
        # Pool para tareas de procesamiento (métricas, overlays)
        self.processing_pool = concurrent.futures.ThreadPoolExecutor(
            max_workers=2,
            thread_name_prefix="welltep_process"
        )
        
        # Pool para tareas de UI (actualizaciones, eventos)
        self.ui_pool = concurrent.futures.ThreadPoolExecutor(
            max_workers=1,
            thread_name_prefix="welltep_ui"
        )
        
        # Queue para tareas de alta prioridad
        self.priority_queue = queue.PriorityQueue()
        self.priority_worker = None
        self._start_priority_worker()
        
        logger.info("ThreadPoolManager inicializado con pools optimizados")
    
    def _start_priority_worker(self):
        """Iniciar worker para tareas de alta prioridad"""
        def priority_worker():
            while True:
                try:
                    priority, task, args, kwargs = self.priority_queue.get(timeout=1.0)
                    if task is None:  # Señal de cierre
                        break
                    task(*args, **kwargs)
                except queue.Empty:
                    continue
                except Exception as e:
                    logger.error(f"Error en priority worker: {e}")
        
        self.priority_worker = threading.Thread(target=priority_worker, daemon=True)
        self.priority_worker.start()
    
    def submit_io_task(self, func: Callable, *args, **kwargs) -> concurrent.futures.Future:
        """Enviar tarea I/O al pool correspondiente"""
        return self.io_pool.submit(func, *args, **kwargs)
    
    def submit_processing_task(self, func: Callable, *args, **kwargs) -> concurrent.futures.Future:
        """Enviar tarea de procesamiento al pool correspondiente"""
        return self.processing_pool.submit(func, *args, **kwargs)
    
    def submit_ui_task(self, func: Callable, *args, **kwargs) -> concurrent.futures.Future:
        """Enviar tarea UI al pool correspondiente"""
        return self.ui_pool.submit(func, *args, **kwargs)
    
    def submit_priority_task(self, func: Callable, priority: int = 0, *args, **kwargs):
        """Enviar tarea de alta prioridad (menor número = mayor prioridad)"""
        self.priority_queue.put((priority, func, args, kwargs))
    
    @contextmanager
    def batch_submit(self, pool_type: str = "processing"):
        """Context manager para envío en lote de tareas"""
        futures = []
        pool = getattr(self, f"{pool_type}_pool")
        
        def submit_batch(func, *args, **kwargs):
            future = pool.submit(func, *args, **kwargs)
            futures.append(future)
            return future
        
        yield submit_batch
        
        # Esperar a que todas las tareas terminen
        concurrent.futures.wait(futures, timeout=30.0)
    
    def get_pool_status(self) -> dict:
        """Obtener estado de los pools para monitoreo"""
        return {
            "io_pool": {
                "active": self.io_pool._threads,
                "max_workers": self.io_pool._max_workers
            },
            "processing_pool": {
                "active": self.processing_pool._threads,
                "max_workers": self.processing_pool._max_workers
            },
            "ui_pool": {
                "active": self.ui_pool._threads,
                "max_workers": self.ui_pool._max_workers
            },
            "priority_queue_size": self.priority_queue.qsize()
        }
    
    def shutdown(self, wait: bool = True):
        """Cerrar todos los pools de forma ordenada"""
        logger.info("Cerrando ThreadPoolManager...")
        
        # Cerrar priority worker
        self.priority_queue.put((0, None, (), {}))
        if self.priority_worker:
            self.priority_worker.join(timeout=5.0)
        
        # Cerrar pools
        self.io_pool.shutdown(wait=wait)
        self.processing_pool.shutdown(wait=wait)
        self.ui_pool.shutdown(wait=wait)
        
        logger.info("ThreadPoolManager cerrado")

# Singleton global para uso en toda la aplicación
_thread_pool_manager = None

def get_thread_pool_manager() -> ThreadPoolManager:
    """Obtener instancia singleton del ThreadPoolManager"""
    global _thread_pool_manager
    if _thread_pool_manager is None:
        _thread_pool_manager = ThreadPoolManager()
    return _thread_pool_manager

def shutdown_thread_pool_manager():
    """Cerrar el ThreadPoolManager global"""
    global _thread_pool_manager
    if _thread_pool_manager:
        _thread_pool_manager.shutdown()
        _thread_pool_manager = None 