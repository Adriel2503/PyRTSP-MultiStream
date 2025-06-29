#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de prueba y validación de optimizaciones para Welltep
Ejecuta benchmarks y valida que las optimizaciones funcionan correctamente
"""

import sys
import time
import argparse
import threading
from pathlib import Path

# Agregar src al path si no está
sys.path.insert(0, str(Path(__file__).parent / 'src'))

try:
    from src.core.thread_pool_manager import get_thread_pool_manager, shutdown_thread_pool_manager
    from src.metrics.optimized_stream_metrics import StreamMetrics
    from src.ui.video.cairo.optimized_renderer import get_optimized_renderer
    from src.ui.video.optimized_recorder import OptimizedRecorder, RecorderType
    from src.utils.performance_monitor import get_performance_monitor
    from src.optimization_integration import apply_welltep_optimizations
    from src.utils.logger import setup_logger
except ImportError as e:
    print(f"❌ Error importando módulos optimizados: {e}")
    print("💡 Asegúrate de que todos los archivos de optimización estén en src/")
    sys.exit(1)

logger = setup_logger("TestOptimizations")

class OptimizationValidator:
    """Validador de optimizaciones con benchmarks"""
    
    def __init__(self):
        self.results = {}
        logger.info("🧪 OptimizationValidator inicializado")
    
    def test_thread_pool_manager(self) -> bool:
        """Test del ThreadPoolManager"""
        logger.info("🔧 Probando ThreadPoolManager...")
        
        try:
            thread_pool = get_thread_pool_manager()
            
            # Test de pools básicos
            futures = []
            
            # Test I/O pool
            for i in range(5):
                future = thread_pool.submit_io_task(time.sleep, 0.1)
                futures.append(future)
            
            # Test processing pool
            for i in range(3):
                future = thread_pool.submit_processing_task(lambda x: x**2, i)
                futures.append(future)
            
            # Esperar resultados
            for future in futures:
                future.result(timeout=2.0)
            
            # Test de estadísticas
            stats = thread_pool.get_pool_status()
            assert 'io_pool' in stats
            assert 'processing_pool' in stats
            
            logger.info("  ✅ ThreadPoolManager funcionando correctamente")
            self.results['thread_pool'] = True
            return True
            
        except Exception as e:
            logger.error(f"  ❌ Error en ThreadPoolManager: {e}")
            self.results['thread_pool'] = False
            return False
    
    def test_optimized_metrics(self) -> bool:
        """Test de métricas optimizadas"""
        logger.info("📊 Probando OptimizedStreamMetrics...")
        
        try:
            metrics = StreamMetrics(window_seconds=5.0)
            
            # Simular frames
            start_time = time.time()
            for i in range(100):
                metrics.add_frame(1024 * (i + 1))  # Tamaños variables
                if i % 10 == 0:
                    time.sleep(0.01)  # Simular intervalos
            
            # Test de cálculos
            fps = metrics.get_fps()
            bitrate = metrics.get_bitrate_kbps()
            data_rate = metrics.get_data_rate_kbps()
            latency = metrics.get_avg_frame_time_ms()
            
            # Validaciones básicas
            assert fps > 0, "FPS debe ser positivo"
            assert bitrate > 0, "Bitrate debe ser positivo"
            assert isinstance(data_rate, (int, float)), "Data rate debe ser numérico"
            
            # Test de optimización de memoria
            metrics.optimize_memory()
            
            # Test de estadísticas de rendimiento
            perf_stats = metrics.get_performance_stats()
            assert 'cache_efficiency' in perf_stats
            assert 'memory_usage_kb' in perf_stats
            
            logger.info(f"  📈 FPS: {fps:.1f}, Bitrate: {bitrate:.1f} Kbps")
            logger.info(f"  💾 Uso memoria: {perf_stats['memory_usage_kb']:.1f} KB")
            logger.info("  ✅ OptimizedStreamMetrics funcionando correctamente")
            
            self.results['metrics'] = True
            return True
            
        except Exception as e:
            logger.error(f"  ❌ Error en OptimizedStreamMetrics: {e}")
            self.results['metrics'] = False
            return False
    
    def test_optimized_renderer(self) -> bool:
        """Test del renderer Cairo optimizado"""
        logger.info("🎨 Probando OptimizedCairoRenderer...")
        
        try:
            renderer = get_optimized_renderer()
            
            # Test de configuración de optimización
            renderer.set_optimization_level("performance")
            renderer.set_optimization_level("memory")
            renderer.set_optimization_level("disabled")
            
            # Test de estadísticas
            stats = renderer.get_performance_stats()
            assert 'cache' in stats
            assert 'performance' in stats
            assert 'settings' in stats
            
            # Test de optimización de cache
            renderer.optimize_cache()
            
            logger.info(f"  🎯 Cache enabled: {stats['settings']['cache_enabled']}")
            logger.info(f"  📊 Total renders: {stats['performance']['total_renders']}")
            logger.info("  ✅ OptimizedCairoRenderer funcionando correctamente")
            
            self.results['renderer'] = True
            return True
            
        except Exception as e:
            logger.error(f"  ❌ Error en OptimizedCairoRenderer: {e}")
            self.results['renderer'] = False
            return False
    
    def test_optimized_recorder(self) -> bool:
        """Test del recorder optimizado"""
        logger.info("📹 Probando OptimizedRecorder...")
        
        try:
            recorder = OptimizedRecorder()
            
            # Test de información del recorder
            info = recorder.get_recorder_info()
            assert 'current_type' in info
            assert 'available_types' in info
            assert 'gpu_available' in info
            
            # Test de estadísticas (sin grabación)
            stats = recorder.get_stats()
            assert stats['state'] == 'idle'
            
            logger.info(f"  🎮 GPU disponible: {info['gpu_available']}")
            logger.info(f"  📊 Tipos disponibles: {info['available_types']}")
            logger.info(f"  ⚙️ Configuración: {info['configuration']}")
            logger.info("  ✅ OptimizedRecorder funcionando correctamente")
            
            self.results['recorder'] = True
            return True
            
        except Exception as e:
            logger.error(f"  ❌ Error en OptimizedRecorder: {e}")
            self.results['recorder'] = False
            return False
    
    def test_performance_monitor(self) -> bool:
        """Test del monitor de rendimiento"""
        logger.info("📈 Probando PerformanceMonitor...")
        
        try:
            monitor = get_performance_monitor()
            
            # Test de métricas custom
            monitor.register_custom_metric('test_metric', lambda: 42)
            
            # Iniciar monitoreo por corto tiempo
            monitor.start_monitoring()
            time.sleep(2.0)  # Recopilar algunas muestras
            
            # Test de estadísticas
            current_stats = monitor.get_current_stats()
            
            # Detener monitoreo
            monitor.stop_monitoring()
            
            # Test de reporte
            report = monitor.generate_report()
            assert len(report) > 0, "El reporte debe tener contenido"
            
            # Limpiar métrica de prueba
            monitor.unregister_custom_metric('test_metric')
            
            logger.info("  📊 Monitor ejecutado exitosamente")
            logger.info("  ✅ PerformanceMonitor funcionando correctamente")
            
            self.results['monitor'] = True
            return True
            
        except Exception as e:
            logger.error(f"  ❌ Error en PerformanceMonitor: {e}")
            self.results['monitor'] = False
            return False
    
    def test_integration(self) -> bool:
        """Test de integración completa"""
        logger.info("🔗 Probando integración completa...")
        
        try:
            integration = apply_welltep_optimizations()
            
            # Test de configuración automática
            integration.optimize_for_low_end_hardware()
            integration.optimize_for_high_end_hardware()
            
            # Test de reporte de rendimiento
            report = integration.get_performance_report()
            assert len(report) > 0, "El reporte debe tener contenido"
            
            # Limpiar recursos
            integration.cleanup()
            
            logger.info("  ✅ Integración completa funcionando correctamente")
            
            self.results['integration'] = True
            return True
            
        except Exception as e:
            logger.error(f"  ❌ Error en integración: {e}")
            self.results['integration'] = False
            return False
    
    def run_benchmark(self, duration_seconds: int = 30) -> dict:
        """Ejecutar benchmark de rendimiento"""
        logger.info(f"🚀 Ejecutando benchmark de {duration_seconds} segundos...")
        
        # Aplicar optimizaciones
        integration = apply_welltep_optimizations()
        
        # Configurar para hardware de prueba
        integration.optimize_for_high_end_hardware()
        
        # Obtener componentes
        metrics = integration.optimized_metrics
        renderer = integration.optimized_renderer
        monitor = integration.performance_monitor
        
        # Iniciar monitoreo
        monitor.start_monitoring()
        
        # Registrar métricas custom para benchmark
        monitor.register_custom_metric('fps', lambda: metrics.get_fps())
        monitor.register_custom_metric('bitrate', lambda: metrics.get_bitrate_mbps())
        
        # Simular carga de trabajo
        start_time = time.time()
        frame_count = 0
        
        try:
            while time.time() - start_time < duration_seconds:
                # Simular frame de video
                frame_size = 1024 * 150  # 150KB por frame
                metrics.add_frame(frame_size)
                frame_count += 1
                
                # Simular render cada 5 frames
                if frame_count % 5 == 0:
                    # Test del renderer (sin Cairo real)
                    pass
                
                # Dormir para simular FPS realista
                time.sleep(0.05)  # ~20 FPS
                
        except KeyboardInterrupt:
            logger.info("⏹️ Benchmark interrumpido por usuario")
        
        end_time = time.time()
        actual_duration = end_time - start_time
        
        # Obtener estadísticas finales
        final_stats = monitor.get_historical_stats(int(actual_duration))
        renderer_stats = renderer.get_performance_stats()
        metrics_stats = metrics.get_performance_stats()
        
        # Detener monitoreo
        monitor.stop_monitoring()
        
        # Limpiar
        integration.cleanup()
        
        # Calcular métricas del benchmark
        avg_fps = frame_count / actual_duration
        
        benchmark_results = {
            'duration': actual_duration,
            'frames_processed': frame_count,
            'avg_fps': avg_fps,
            'system_stats': final_stats,
            'renderer_stats': renderer_stats,
            'metrics_stats': metrics_stats
        }
        
        logger.info("📊 Resultados del benchmark:")
        logger.info(f"  ⏱️ Duración: {actual_duration:.1f}s")
        logger.info(f"  🎞️ Frames procesados: {frame_count}")
        logger.info(f"  📈 FPS promedio: {avg_fps:.1f}")
        
        if final_stats and 'cpu' in final_stats:
            logger.info(f"  💻 CPU promedio: {final_stats['cpu']['avg']:.1f}%")
            logger.info(f"  💾 Memoria promedio: {final_stats['memory']['avg']:.1f}%")
        
        if renderer_stats:
            logger.info(f"  🎨 Cache hit rate: {renderer_stats['performance']['cache_hit_rate']:.1f}%")
        
        if metrics_stats:
            logger.info(f"  📊 Eficiencia métricas: {metrics_stats['cache_efficiency']:.1f}%")
        
        return benchmark_results
    
    def run_all_tests(self) -> bool:
        """Ejecutar todos los tests de validación"""
        logger.info("🧪 Iniciando validación completa de optimizaciones...")
        
        tests = [
            ('ThreadPoolManager', self.test_thread_pool_manager),
            ('OptimizedStreamMetrics', self.test_optimized_metrics),
            ('OptimizedCairoRenderer', self.test_optimized_renderer),
            ('OptimizedRecorder', self.test_optimized_recorder),
            ('PerformanceMonitor', self.test_performance_monitor),
            ('Integración Completa', self.test_integration)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            logger.info(f"\n--- {test_name} ---")
            try:
                if test_func():
                    passed += 1
            except Exception as e:
                logger.error(f"💥 Error inesperado en {test_name}: {e}")
        
        # Limpiar recursos globales
        try:
            shutdown_thread_pool_manager()
        except:
            pass
        
        logger.info(f"\n🏁 Validación completada: {passed}/{total} tests pasaron")
        
        if passed == total:
            logger.info("🎉 ¡Todas las optimizaciones funcionan correctamente!")
            return True
        else:
            logger.warning(f"⚠️ {total - passed} optimizaciones tienen problemas")
            return False
    
    def print_summary(self):
        """Imprimir resumen de resultados"""
        print("\n" + "="*60)
        print("📋 RESUMEN DE VALIDACIÓN DE OPTIMIZACIONES")
        print("="*60)
        
        for component, result in self.results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{component:25}: {status}")
        
        passed = sum(self.results.values())
        total = len(self.results)
        
        print(f"\nResultado final: {passed}/{total} componentes funcionando")
        
        if passed == total:
            print("🎉 ¡TODAS LAS OPTIMIZACIONES FUNCIONAN CORRECTAMENTE!")
        else:
            print("⚠️ Algunas optimizaciones necesitan revisión")

def main():
    """Función principal del script"""
    parser = argparse.ArgumentParser(description="Validar optimizaciones de Welltep")
    parser.add_argument('--benchmark', type=int, metavar='SECONDS', 
                       help='Ejecutar benchmark por N segundos')
    parser.add_argument('--test-all', action='store_true',
                       help='Ejecutar todos los tests de validación')
    parser.add_argument('--component', choices=['threads', 'metrics', 'renderer', 'recorder', 'monitor'],
                       help='Probar componente específico')
    
    args = parser.parse_args()
    
    validator = OptimizationValidator()
    
    if args.benchmark:
        print("🚀 MODO BENCHMARK")
        results = validator.run_benchmark(args.benchmark)
        return 0 if results else 1
    
    elif args.component:
        print(f"🔧 PROBANDO COMPONENTE: {args.component}")
        component_tests = {
            'threads': validator.test_thread_pool_manager,
            'metrics': validator.test_optimized_metrics,
            'renderer': validator.test_optimized_renderer,
            'recorder': validator.test_optimized_recorder,
            'monitor': validator.test_performance_monitor
        }
        
        success = component_tests[args.component]()
        validator.print_summary()
        return 0 if success else 1
    
    elif args.test_all:
        print("🧪 MODO VALIDACIÓN COMPLETA")
        success = validator.run_all_tests()
        validator.print_summary()
        return 0 if success else 1
    
    else:
        # Por defecto, ejecutar validación rápida
        print("⚡ VALIDACIÓN RÁPIDA (usa --help para más opciones)")
        success = validator.run_all_tests()
        validator.print_summary()
        
        if success:
            print("\n💡 Para benchmark completo: python test_optimizations.py --benchmark 60")
        
        return 0 if success else 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⏹️ Pruebas interrumpidas por usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Error inesperado: {e}")
        sys.exit(1) 