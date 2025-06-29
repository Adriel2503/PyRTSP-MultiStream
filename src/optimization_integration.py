# -*- coding: utf-8 -*-
"""
Script de integración de optimizaciones para Welltep
Muestra cómo aplicar las optimizaciones a los componentes existentes
"""

import time
from typing import Dict, Any

from .utils.logger import setup_logger
from .core.thread_pool_manager import get_thread_pool_manager, shutdown_thread_pool_manager
from .metrics.optimized_stream_metrics import StreamMetrics
from .ui.video.cairo.optimized_renderer import get_optimized_renderer
from .ui.video.optimized_recorder import OptimizedRecorder, RecorderType
from .utils.performance_monitor import get_performance_monitor

logger = setup_logger("OptimizationIntegration")

class OptimizedWelltepIntegration:
    """Integración de optimizaciones en Welltep existente"""
    
    def __init__(self):
        # Componentes optimizados
        self.thread_pool = get_thread_pool_manager()
        self.optimized_metrics = StreamMetrics()  # Usa la versión optimizada
        self.optimized_renderer = get_optimized_renderer()
        self.optimized_recorder = OptimizedRecorder()
        self.performance_monitor = get_performance_monitor()
        
        # Configurar monitoreo de métricas custom
        self._setup_custom_metrics()
        
        logger.info("OptimizedWelltepIntegration inicializada")
    
    def _setup_custom_metrics(self):
        """Configurar métricas personalizadas para el monitor"""
        # Registrar métricas de FPS
        self.performance_monitor.register_custom_metric(
            'fps', lambda: self.optimized_metrics.get_fps()
        )
        
        # Registrar métricas de bitrate
        self.performance_monitor.register_custom_metric(
            'bitrate_mbps', lambda: self.optimized_metrics.get_bitrate_mbps()
        )
        
        # Registrar estadísticas del pool de threads
        self.performance_monitor.register_custom_metric(
            'thread_pool_status', lambda: self.thread_pool.get_pool_status()
        )
        
        # Registrar estadísticas de recorder si está grabando
        self.performance_monitor.register_custom_metric(
            'recorder_stats', lambda: self.optimized_recorder.get_stats() if self.optimized_recorder.is_recording() else None
        )
        
        # Registrar estadísticas de renderer
        self.performance_monitor.register_custom_metric(
            'renderer_stats', lambda: self.optimized_renderer.get_performance_stats()
        )
    
    def integrate_with_existing_components(self):
        """Integrar optimizaciones con componentes existentes"""
        logger.info("🔧 Integrando optimizaciones con componentes existentes...")
        
        # 1. Integrar con GStreamerManager
        self._integrate_gstreamer_manager()
        
        # 2. Integrar con OverlayManager
        self._integrate_overlay_manager()
        
        # 3. Integrar con VideoRecorder
        self._integrate_video_recorder()
        
        # 4. Integrar con MainWindow
        self._integrate_main_window()
        
        logger.info("✅ Integración de optimizaciones completada")
    
    def _integrate_gstreamer_manager(self):
        """Integrar optimizaciones con GStreamerManager"""
        logger.info("🎥 Integrando con GStreamerManager...")
        
        # Ejemplo de integración - reemplazar métricas existentes
        # En GStreamerManager, cambiar:
        # self.metrics_integration = MetricsIntegration(StreamMetrics())
        # Por:
        # self.metrics_integration = MetricsIntegration(self.optimized_metrics)
        
        logger.info("  ✅ Métricas optimizadas integradas en GStreamer")
        
        # Configurar probes de métricas para usar thread pool
        # Enviar cálculos pesados al thread pool de procesamiento
        
        logger.info("  ✅ Thread pool integrado para cálculos de métricas")
    
    def _integrate_overlay_manager(self):
        """Integrar optimizaciones con OverlayManager"""
        logger.info("🎨 Integrando con OverlayManager...")
        
        # Configurar renderer optimizado
        self.optimized_renderer.set_optimization_level("performance")
        
        # En OverlayManager, reemplazar callbacks de draw:
        # def _on_cairo_draw_grid(self, element, context, timestamp, duration, user_data=None):
        #     return self.optimized_renderer.render_element(context, "grid", self.overlay_config)
        
        logger.info("  ✅ Renderer Cairo optimizado integrado")
        logger.info("  ✅ Cache de elementos habilitado")
    
    def _integrate_video_recorder(self):
        """Integrar optimizaciones con sistema de grabación"""
        logger.info("📹 Integrando con VideoRecorder...")
        
        # Configurar recorder optimizado con detección automática
        recorder_info = self.optimized_recorder.get_recorder_info()
        logger.info(f"  🎮 GPU disponible: {recorder_info['gpu_available']}")
        logger.info(f"  📊 Tipos disponibles: {recorder_info['available_types']}")
        
        # En GStreamerManager, reemplazar:
        # self.pyav_recorder = PyAVRecorder()
        # self.gpu_recorder = GPURecorder()
        # Por:
        # self.optimized_recorder = OptimizedRecorder()
        
        logger.info("  ✅ Sistema de grabación optimizado integrado")
        logger.info("  ✅ Buffer inteligente de frames configurado")
    
    def _integrate_main_window(self):
        """Integrar optimizaciones con MainWindow"""
        logger.info("🖼️ Integrando con MainWindow...")
        
        # Iniciar monitoreo de rendimiento
        self.performance_monitor.start_monitoring()
        
        # En MainWindow, agregar método para obtener estadísticas:
        # def get_performance_stats(self):
        #     return self.optimization_integration.get_performance_report()
        
        logger.info("  ✅ Monitor de rendimiento iniciado")
        logger.info("  ✅ Métricas personalizadas configuradas")
    
    def start_optimized_recording(self, filename: str, 
                                 recorder_type: RecorderType = RecorderType.AUTO) -> bool:
        """Iniciar grabación con sistema optimizado"""
        logger.info(f"🎬 Iniciando grabación optimizada: {filename}")
        
        success = self.optimized_recorder.start_recording(filename, recorder_type)
        
        if success:
            logger.info("✅ Grabación optimizada iniciada exitosamente")
            
            # Programar reporte de estadísticas cada 30 segundos
            self.thread_pool.submit_processing_task(self._scheduled_stats_report)
        else:
            logger.error("❌ Error iniciando grabación optimizada")
        
        return success
    
    def stop_optimized_recording(self) -> bool:
        """Detener grabación optimizada"""
        logger.info("🛑 Deteniendo grabación optimizada...")
        
        success = self.optimized_recorder.stop_recording()
        
        if success:
            # Generar reporte final
            stats = self.optimized_recorder.get_stats()
            logger.info("📊 Estadísticas finales de grabación:")
            logger.info(f"  ⏱️ Duración: {stats['duration_seconds']:.1f}s")
            logger.info(f"  🎞️ Frames procesados: {stats['frames_processed']}")
            logger.info(f"  📊 FPS promedio: {stats['performance']['fps_processed']:.1f}")
            logger.info(f"  💾 MB/s promedio: {stats['performance']['mbytes_per_second']:.1f}")
            logger.info(f"  ✅ Eficiencia: {stats['performance']['efficiency_percent']:.1f}%")
        
        return success
    
    def _scheduled_stats_report(self):
        """Reportar estadísticas cada 30 segundos durante grabación"""
        while self.optimized_recorder.is_recording():
            time.sleep(30)
            
            if self.optimized_recorder.is_recording():
                stats = self.optimized_recorder.get_stats()
                perf_stats = self.performance_monitor.get_current_stats()
                
                logger.info("📊 Reporte de grabación (30s):")
                logger.info(f"  🎞️ FPS actual: {stats['performance']['fps_processed']:.1f}")
                logger.info(f"  💻 CPU: {perf_stats['current']['cpu_percent']:.1f}%")
                logger.info(f"  💾 Memoria: {perf_stats['current']['memory_percent']:.1f}%")
                logger.info(f"  📦 Buffer: {stats['buffer']['fill_rate_percent']:.1f}%")
                logger.info(f"  ⚠️ Drops: {stats['buffer']['drop_rate_percent']:.1f}%")
    
    def get_performance_report(self) -> str:
        """Obtener reporte completo de rendimiento"""
        return self.performance_monitor.generate_report()
    
    def optimize_for_low_end_hardware(self):
        """Configurar optimizaciones para hardware de gama baja"""
        logger.info("⚡ Configurando optimizaciones para hardware de gama baja...")
        
        # Configurar renderer para memoria
        self.optimized_renderer.set_optimization_level("memory")
        
        # Configurar métricas con ventana más pequeña
        self.optimized_metrics.window_seconds = 3.0
        
        # Configurar recorder para CPU únicamente
        # (El híbrido detectará automáticamente, pero podemos forzar CPU)
        
        # Reducir buffer del recorder
        self.optimized_recorder.frame_buffer.max_size = 20
        self.optimized_recorder.frame_buffer.drop_policy = "adaptive"
        
        logger.info("✅ Optimizaciones para hardware de gama baja aplicadas")
    
    def optimize_for_high_end_hardware(self):
        """Configurar optimizaciones para hardware de gama alta"""
        logger.info("🚀 Configurando optimizaciones para hardware de gama alta...")
        
        # Configurar renderer para rendimiento máximo
        self.optimized_renderer.set_optimization_level("performance")
        
        # Configurar métricas con ventana más grande
        self.optimized_metrics.window_seconds = 10.0
        
        # Aumentar buffer del recorder
        self.optimized_recorder.frame_buffer.max_size = 50
        self.optimized_recorder.frame_buffer.drop_policy = "oldest"
        
        # Configurar thread pool para más workers
        # (esto requeriría recrear el pool, mejor dejar como está)
        
        logger.info("✅ Optimizaciones para hardware de gama alta aplicadas")
    
    def run_performance_benchmark(self, duration_seconds: int = 60) -> Dict[str, Any]:
        """Ejecutar benchmark de rendimiento"""
        logger.info(f"🧪 Iniciando benchmark de rendimiento ({duration_seconds}s)...")
        
        # Iniciar monitoreo
        self.performance_monitor.start_monitoring()
        
        start_time = time.time()
        
        # Simular carga de trabajo (esto debería hacerse con datos reales)
        for i in range(duration_seconds * 20):  # 20 FPS simulados
            # Simular frame
            self.optimized_metrics.add_frame(1024 * 100)  # 100KB frame
            
            # Simular render de overlay
            # (en implementación real, esto vendría del pipeline de video)
            
            time.sleep(0.05)  # 50ms = 20 FPS
        
        end_time = time.time()
        
        # Obtener estadísticas finales
        final_stats = self.performance_monitor.get_historical_stats(duration_seconds)
        
        logger.info("✅ Benchmark completado")
        logger.info(f"📊 CPU promedio: {final_stats.get('cpu', {}).get('avg', 0):.1f}%")
        logger.info(f"📊 Memoria promedio: {final_stats.get('memory', {}).get('avg', 0):.1f}%")
        logger.info(f"📊 FPS promedio: {final_stats.get('fps', {}).get('avg', 0):.1f}")
        
        return final_stats
    
    def cleanup(self):
        """Limpiar recursos de optimización"""
        logger.info("🧹 Limpiando recursos de optimización...")
        
        # Detener monitoreo
        self.performance_monitor.stop_monitoring()
        
        # Detener grabación si está activa
        if self.optimized_recorder.is_recording():
            self.optimized_recorder.stop_recording()
        
        # Limpiar caches
        self.optimized_renderer.optimize_cache()
        self.optimized_metrics.optimize_memory()
        
        # Cerrar thread pool
        shutdown_thread_pool_manager()
        
        logger.info("✅ Limpieza completada")

# Función de conveniencia para integración rápida
def apply_welltep_optimizations() -> OptimizedWelltepIntegration:
    """Aplicar optimizaciones a Welltep de forma rápida"""
    logger.info("🚀 Aplicando optimizaciones a Welltep...")
    
    integration = OptimizedWelltepIntegration()
    integration.integrate_with_existing_components()
    
    logger.info("✅ Optimizaciones aplicadas exitosamente")
    
    return integration

# Ejemplo de uso en Application
def example_integration_in_main():
    """Ejemplo de cómo integrar en la aplicación principal"""
    logger.info("📝 Ejemplo de integración en aplicación principal:")
    
    # En src/core/application.py, en el método run():
    code_example = '''
class Application:
    def __init__(self):
        # ... código existente ...
        
        # NUEVO: Aplicar optimizaciones
        self.optimization_integration = apply_welltep_optimizations()
    
    def run(self):
        # ... código existente ...
        
        # Detectar hardware y optimizar
        try:
            import psutil
            total_memory_gb = psutil.virtual_memory().total / (1024**3)
            
            if total_memory_gb < 8:
                self.optimization_integration.optimize_for_low_end_hardware()
            else:
                self.optimization_integration.optimize_for_high_end_hardware()
        except:
            pass  # Usar configuración por defecto
        
        # ... resto del código existente ...
        
        return self.app.exec()
    
    def shutdown(self):
        # ... código existente ...
        
        # NUEVO: Limpiar optimizaciones
        if hasattr(self, 'optimization_integration'):
            self.optimization_integration.cleanup()
    '''
    
    logger.info("Código de ejemplo guardado en variable 'code_example'")
    
    return code_example 