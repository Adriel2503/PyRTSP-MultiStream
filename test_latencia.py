# -*- coding: utf-8 -*-
"""
Script de prueba para medir latencia en streaming de cámaras IP
Compara diferentes configuraciones y mide el rendimiento
"""

import cv2
import time
import vlc
import sys
import threading
from datetime import datetime
from low_latency_config import (
    VLC_ULTRA_LOW_LATENCY_ARGS,
    apply_opencv_ultra_low_latency,
    LatencyMonitor
)

def test_opencv_latency(url, duration=30):
    """
    Prueba de latencia con OpenCV optimizado
    """
    print(f"\n🧪 === PRUEBA OPENCV OPTIMIZADO ===")
    print(f"URL: {url}")
    print(f"Duración: {duration} segundos")
    
    # Configuración optimizada
    cap = cv2.VideoCapture(url, cv2.CAP_FFMPEG)
    cap = apply_opencv_ultra_low_latency(cap)
    
    if not cap.isOpened():
        print("❌ Error: No se pudo conectar al stream")
        return None
    
    # Monitor de latencia
    monitor = LatencyMonitor()
    
    print("🔄 Midiendo latencia...")
    start_time = time.time()
    frame_count = 0
    successful_reads = 0
    
    while time.time() - start_time < duration:
        frame_start = time.time()
        ret, frame = cap.read()
        frame_end = time.time()
        
        if ret:
            successful_reads += 1
            frame_time = frame_end - frame_start
            monitor.add_frame_time(frame_time)
            
            # Mostrar progreso cada 5 segundos
            if frame_count % 150 == 0:  # ~5 segundos a 30fps
                elapsed = time.time() - start_time
                avg_latency = monitor.get_average_latency_ms()
                max_latency = monitor.get_max_latency_ms()
                print(f"⏱️  {elapsed:.1f}s | Promedio: {avg_latency:.1f}ms | Máximo: {max_latency:.1f}ms")
        
        frame_count += 1
    
    cap.release()
    
    # Resultados finales
    total_time = time.time() - start_time
    fps_real = successful_reads / total_time
    avg_latency = monitor.get_average_latency_ms()
    max_latency = monitor.get_max_latency_ms()
    success_rate = (successful_reads / frame_count) * 100 if frame_count > 0 else 0
    
    results = {
        'fps_real': fps_real,
        'avg_latency_ms': avg_latency,
        'max_latency_ms': max_latency,
        'success_rate': success_rate,
        'total_frames': frame_count,
        'successful_frames': successful_reads
    }
    
    print(f"\n📊 === RESULTADOS OPENCV ===")
    print(f"🎬 FPS Real: {fps_real:.2f}")
    print(f"⚡ Latencia Promedio: {avg_latency:.1f}ms")
    print(f"🔥 Latencia Máxima: {max_latency:.1f}ms")
    print(f"✅ Tasa de Éxito: {success_rate:.1f}%")
    print(f"📋 Frames: {successful_reads}/{frame_count}")
    
    return results

def test_vlc_latency(url, duration=30):
    """
    Prueba de latencia con VLC optimizado
    """
    print(f"\n🧪 === PRUEBA VLC OPTIMIZADO ===")
    print(f"URL: {url}")
    print(f"Duración: {duration} segundos")
    
    # Crear instancia VLC optimizada
    instance = vlc.Instance(VLC_ULTRA_LOW_LATENCY_ARGS)
    player = instance.media_player_new()
    
    # Configurar media
    media = instance.media_new(url)
    media.add_option(':network-caching=0')
    media.add_option(':live-caching=0')
    media.add_option(':rtsp-tcp')
    player.set_media(media)
    
    # Variables de medición
    start_time = time.time()
    connection_start = time.time()
    connected = False
    
    # Iniciar reproducción
    player.play()
    
    print("🔄 Esperando conexión...")
    
    # Esperar a que se conecte (máximo 10 segundos)
    while time.time() - connection_start < 10:
        state = player.get_state()
        if state == vlc.State.Playing:
            connected = True
            connection_time = time.time() - connection_start
            print(f"✅ Conectado en {connection_time:.2f} segundos")
            break
        elif state == vlc.State.Error:
            print("❌ Error de conexión VLC")
            player.release()
            return None
        time.sleep(0.1)
    
    if not connected:
        print("❌ Timeout de conexión VLC")
        player.release()
        return None
    
    # Medir rendimiento durante la duración especificada
    print("📊 Midiendo rendimiento VLC...")
    measurement_start = time.time()
    
    while time.time() - measurement_start < duration:
        state = player.get_state()
        if state != vlc.State.Playing:
            print(f"⚠️  Estado VLC: {state}")
        
        # Mostrar progreso cada 5 segundos
        elapsed = time.time() - measurement_start
        if int(elapsed) % 5 == 0 and elapsed > 0:
            print(f"⏱️  {elapsed:.1f}s - Estado: {state}")
            time.sleep(1)  # Evitar spam
        
        time.sleep(0.1)
    
    # Detener reproducción
    player.stop()
    total_time = time.time() - start_time
    
    results = {
        'connection_time': connection_time if connected else None,
        'total_time': total_time,
        'connected': connected,
        'final_state': player.get_state()
    }
    
    print(f"\n📊 === RESULTADOS VLC ===")
    print(f"🔗 Tiempo de Conexión: {connection_time:.2f}s" if connected else "❌ No conectado")
    print(f"⏱️  Tiempo Total: {total_time:.2f}s")
    print(f"🎬 Estado Final: {results['final_state']}")
    
    player.release()
    return results

def test_opencv_standard(url, duration=30):
    """
    Prueba con configuración estándar de OpenCV (para comparación)
    """
    print(f"\n🧪 === PRUEBA OPENCV ESTÁNDAR (COMPARACIÓN) ===")
    
    # Configuración estándar (sin optimizaciones)
    cap = cv2.VideoCapture(url)
    
    if not cap.isOpened():
        print("❌ Error: No se pudo conectar al stream")
        return None
    
    monitor = LatencyMonitor()
    start_time = time.time()
    frame_count = 0
    successful_reads = 0
    
    while time.time() - start_time < duration:
        frame_start = time.time()
        ret, frame = cap.read()
        frame_end = time.time()
        
        if ret:
            successful_reads += 1
            frame_time = frame_end - frame_start
            monitor.add_frame_time(frame_time)
        
        frame_count += 1
    
    cap.release()
    
    total_time = time.time() - start_time
    fps_real = successful_reads / total_time
    avg_latency = monitor.get_average_latency_ms()
    max_latency = monitor.get_max_latency_ms()
    success_rate = (successful_reads / frame_count) * 100 if frame_count > 0 else 0
    
    results = {
        'fps_real': fps_real,
        'avg_latency_ms': avg_latency,
        'max_latency_ms': max_latency,
        'success_rate': success_rate,
        'total_frames': frame_count,
        'successful_frames': successful_reads
    }
    
    print(f"\n📊 === RESULTADOS OPENCV ESTÁNDAR ===")
    print(f"🎬 FPS Real: {fps_real:.2f}")
    print(f"⚡ Latencia Promedio: {avg_latency:.1f}ms")
    print(f"🔥 Latencia Máxima: {max_latency:.1f}ms")
    print(f"✅ Tasa de Éxito: {success_rate:.1f}%")
    
    return results

def compare_results(standard_results, optimized_results):
    """
    Comparar resultados entre configuración estándar y optimizada
    """
    if not standard_results or not optimized_results:
        print("❌ No se pueden comparar resultados incompletos")
        return
    
    print(f"\n🔥 === COMPARACIÓN DE RENDIMIENTO ===")
    
    # Comparar latencia
    latency_improvement = standard_results['avg_latency_ms'] - optimized_results['avg_latency_ms']
    latency_percent = (latency_improvement / standard_results['avg_latency_ms']) * 100
    
    print(f"⚡ LATENCIA:")
    print(f"   Estándar: {standard_results['avg_latency_ms']:.1f}ms")
    print(f"   Optimizada: {optimized_results['avg_latency_ms']:.1f}ms")
    print(f"   Mejora: -{latency_improvement:.1f}ms ({latency_percent:+.1f}%)")
    
    # Comparar FPS
    fps_improvement = optimized_results['fps_real'] - standard_results['fps_real']
    fps_percent = (fps_improvement / standard_results['fps_real']) * 100
    
    print(f"\n🎬 FPS:")
    print(f"   Estándar: {standard_results['fps_real']:.2f}")
    print(f"   Optimizada: {optimized_results['fps_real']:.2f}")
    print(f"   Mejora: +{fps_improvement:.2f} ({fps_percent:+.1f}%)")
    
    # Comparar tasa de éxito
    success_improvement = optimized_results['success_rate'] - standard_results['success_rate']
    
    print(f"\n✅ TASA DE ÉXITO:")
    print(f"   Estándar: {standard_results['success_rate']:.1f}%")
    print(f"   Optimizada: {optimized_results['success_rate']:.1f}%")
    print(f"   Mejora: {success_improvement:+.1f}%")

def main():
    """
    Función principal para ejecutar todas las pruebas
    """
    print("🚀 === PRUEBAS DE LATENCIA PARA CÁMARAS IP ===")
    print("Este script comparará diferentes configuraciones de streaming")
    
    # URL de prueba (reemplaza con tu cámara IP)
    url = input("\n📹 Ingresa la URL de tu cámara IP (RTSP): ").strip()
    if not url:
        print("❌ URL requerida")
        return
    
    duration = 15  # Duración de cada prueba en segundos
    
    print(f"\n⏱️  Cada prueba durará {duration} segundos")
    print("🔄 Iniciando pruebas...\n")
    
    # Ejecutar pruebas
    standard_results = test_opencv_standard(url, duration)
    optimized_results = test_opencv_latency(url, duration)
    vlc_results = test_vlc_latency(url, duration)
    
    # Comparar resultados
    if standard_results and optimized_results:
        compare_results(standard_results, optimized_results)
    
    print(f"\n🎯 === RESUMEN FINAL ===")
    print("✅ Pruebas completadas")
    if optimized_results:
        print(f"🏆 Mejor configuración: OpenCV Optimizado")
        print(f"   - Latencia promedio: {optimized_results['avg_latency_ms']:.1f}ms")
        print(f"   - FPS real: {optimized_results['fps_real']:.2f}")
        print(f"   - Tasa de éxito: {optimized_results['success_rate']:.1f}%")
    
    print("\n💡 RECOMENDACIONES:")
    print("1. Usa las configuraciones optimizadas en tu aplicación principal")
    print("2. Ajusta la URL de tu cámara para usar TCP: ?tcp=1 o &tcp=1")
    print("3. Reduce la resolución de la cámara si la latencia sigue alta")
    print("4. Considera usar una conexión Ethernet en lugar de WiFi")

if __name__ == "__main__":
    main() 