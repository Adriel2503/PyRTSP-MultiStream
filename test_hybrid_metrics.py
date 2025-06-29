#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de prueba para el sistema híbrido de métricas
Demuestra las diferencias entre métricas suavizadas e instantáneas
"""

import time
import random
from src.metrics.stream_metrics import HybridStreamMetrics

def simulate_video_stream():
    """Simular un stream de video con variaciones realistas"""
    
    print("🎬 Iniciando simulación de stream híbrido...")
    metrics = HybridStreamMetrics(window_seconds=5.0)
    
    # Simular 30 segundos de streaming con variaciones
    duration = 30
    start_time = time.time()
    frame_count = 0
    
    while time.time() - start_time < duration:
        frame_count += 1
        
        # Simular variaciones en el stream
        if frame_count < 50:
            # Inicio estable
            frame_size = random.randint(1200, 1600)  # Stable
            fps_delay = 1/30  # 30 FPS
        elif frame_count < 100:
            # Congestión de red (frames más grandes, FPS irregular)
            frame_size = random.randint(2000, 3000)  # Bigger frames
            fps_delay = random.uniform(1/20, 1/25)   # Irregular FPS
        elif frame_count < 150:
            # Recuperación gradual
            frame_size = random.randint(1400, 1800)  # Recovering
            fps_delay = 1/28  # Better FPS
        else:
            # Estable otra vez
            frame_size = random.randint(1100, 1500)  # Stable again
            fps_delay = 1/30  # 30 FPS
        
        # Usar el nuevo sistema multi-nivel
        buffer_id = f"frame_{frame_count}"
        
        # Red: Datos llegan del RTSP
        metrics.add_network_data(frame_size, buffer_id)
        
        # Pequeño delay para simular procesamiento
        time.sleep(0.001)  
        
        # Decoder: Frame decodificado
        metrics.add_decoded_frame(buffer_id)
        
        # Pequeño delay para simular rendering
        time.sleep(0.001)
        
        # Display: Frame mostrado
        metrics.add_display_frame(buffer_id)
        
        # Mostrar métricas cada 60 frames
        if frame_count % 60 == 0:
            elapsed = time.time() - start_time
            
            print(f"\n⏱️ Tiempo: {elapsed:.1f}s | Frames: {frame_count}")
            print("=" * 60)
            
            # Comparar métricas suavizadas vs instantáneas
            smooth = metrics.get_metrics(smooth=True)
            instant = metrics.get_metrics(smooth=False)
            
            print("📊 MÉTRICAS SUAVIZADAS (UI-friendly):")
            print(f"   FPS: {smooth['fps']:.1f}")
            print(f"   Bitrate: {smooth['bitrate_kbps']:.1f} Kbps")
            print(f"   Data Rate: {smooth['data_rate_kbps']:.1f} KBps")
            print(f"   Latencia: {smooth['latency_ms']:.1f} ms")
            print(f"   Total: {smooth['total_mb']:.2f} MB")
            
            print("\n⚡ MÉTRICAS INSTANTÁNEAS (Debug):")
            print(f"   FPS: {instant['fps']:.1f}")
            print(f"   Bitrate: {instant['bitrate_kbps']:.1f} Kbps")
            print(f"   Data Rate: {instant['data_rate_kbps']:.1f} KBps")
            print(f"   Latencia: {instant['latency_ms']:.1f} ms")
            print(f"   Total: {instant['total_mb']:.2f} MB")
            
            # Mostrar info de debug
            debug = metrics.get_debug_info()
            print(f"\n🔍 DEBUG:")
            print(f"   Muestras FPS: {debug['fps_samples']}")
            print(f"   Muestras Bitrate: {debug['bitrate_samples']}")
            print(f"   Timestamps pendientes: {debug['pending_network_timestamps']}")
        
        # Delay para simular FPS
        time.sleep(fps_delay)
    
    print(f"\n✅ Simulación completada - {frame_count} frames procesados")
    
    # Resumen final
    final_smooth = metrics.get_metrics(smooth=True)
    final_instant = metrics.get_metrics(smooth=False)
    
    print("\n📋 RESUMEN FINAL:")
    print("=" * 50)
    print(f"Duración sesión: {metrics.get_session_duration():.1f}s")
    print(f"Total frames: {metrics.total_frames}")
    print(f"FPS promedio suavizado: {final_smooth['fps']:.1f}")
    print(f"FPS instantáneo final: {final_instant['fps']:.1f}")
    print(f"Total datos: {final_smooth['total_mb']:.2f} MB")
    print(f"Bitrate promedio: {final_smooth['bitrate_kbps']:.1f} Kbps")


def test_compatibility():
    """Probar compatibilidad con el sistema anterior"""
    
    print("\n🔄 Probando compatibilidad hacia atrás...")
    
    # Usar como antes (debe funcionar igual)
    from src.metrics.stream_metrics import StreamMetrics  # Alias
    
    metrics = StreamMetrics()  # Usa HybridStreamMetrics internamente
    
    # Métodos antiguos deben funcionar
    for i in range(20):
        metrics.add_frame(random.randint(1000, 2000))
        time.sleep(0.05)
    
    print(f"✅ FPS (método antiguo): {metrics.get_fps():.1f}")
    print(f"✅ Bitrate (método antiguo): {metrics.get_bitrate_kbps():.1f} Kbps")
    print(f"✅ Total MB (método antiguo): {metrics.get_total_mb_received():.3f}")
    
    # Nuevos métodos también disponibles
    instant_fps = metrics.get_fps_instant()
    print(f"✅ FPS instantáneo (nuevo): {instant_fps:.1f}")


def compare_systems():
    """Comparar ventajas del sistema híbrido"""
    
    print("\n🆚 Comparando sistemas...")
    
    metrics = HybridStreamMetrics()
    
    # Simular picos de datos
    print("Simulando picos de datos...")
    
    # Frame normal
    metrics.add_frame(1200)
    time.sleep(0.033)  # 30 FPS
    
    # Pico gigante (keyframe)
    metrics.add_frame(15000)  # Keyframe grande
    time.sleep(0.033)
    
    # Frames normales
    for _ in range(5):
        metrics.add_frame(1200)
        time.sleep(0.033)
    
    smooth = metrics.get_metrics(smooth=True)
    instant = metrics.get_metrics(smooth=False)
    
    print(f"📊 Después del pico:")
    print(f"   Bitrate suavizado: {smooth['bitrate_kbps']:.1f} Kbps (estable)")
    print(f"   Bitrate instantáneo: {instant['bitrate_kbps']:.1f} Kbps (refleja pico)")
    print(f"💡 UI usa suavizado, Debug usa instantáneo")


if __name__ == "__main__":
    print("🚀 PRUEBAS DEL SISTEMA HÍBRIDO DE MÉTRICAS")
    print("=" * 50)
    
    # Prueba principal
    simulate_video_stream()
    
    # Prueba de compatibilidad
    test_compatibility()
    
    # Comparación de sistemas
    compare_systems()
    
    print("\n🎯 ¡Todas las pruebas completadas!") 