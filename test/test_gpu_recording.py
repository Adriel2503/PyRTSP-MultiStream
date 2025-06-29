#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script para verificar soporte de GPU recording
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from ui.video.gpu_recorder import GPURecorder
from ui.video.pyav_recorder import PyAVRecorder
import numpy as np
import time

def test_gpu_support():
    """Probar soporte de GPU"""
    print("🔍 Verificando soporte de GPU...")
    
    gpu_recorder = GPURecorder()
    
    # Verificar NVENC
    nvenc_support = gpu_recorder.check_nvenc_support()
    print(f"NVENC disponible: {'✅ Sí' if nvenc_support else '❌ No'}")
    
    return nvenc_support

def test_recording(use_gpu=True):
    """Probar grabación con GPU o CPU"""
    print(f"\n🎬 Probando grabación {'GPU' if use_gpu else 'CPU'}...")
    
    # Crear recorder
    if use_gpu:
        recorder = GPURecorder()
    else:
        recorder = PyAVRecorder()
    
    # Configurar archivo de salida
    filename = f"test_{'gpu' if use_gpu else 'cpu'}.mp4"
    
    try:
        # Iniciar grabación
        success = recorder.start_recording(filename)
        if not success:
            print(f"❌ Error iniciando grabación {'GPU' if use_gpu else 'CPU'}")
            return False
        
        print(f"✅ Grabación {'GPU' if use_gpu else 'CPU'} iniciada")
        
        # Generar frames de prueba
        width, height = 640, 480
        frames_to_record = 50
        
        print(f"📹 Generando {frames_to_record} frames de prueba...")
        
        for i in range(frames_to_record):
            # Crear frame de prueba (gradiente)
            frame = np.zeros((height, width, 3), dtype=np.uint8)
            
            # Gradiente horizontal
            for x in range(width):
                frame[:, x, 0] = int(255 * x / width)  # Rojo
                frame[:, x, 1] = int(255 * (1 - x / width))  # Verde
                frame[:, x, 2] = 128  # Azul constante
            
            # Agregar número de frame
            frame[height//2-10:height//2+10, i*width//frames_to_record:i*width//frames_to_record+20] = [255, 255, 255]
            
            # Enviar frame
            recorder.add_frame(frame.tobytes(), width, height)
            
            if i % 10 == 0:
                print(f"  Frame {i+1}/{frames_to_record}")
            
            time.sleep(0.05)  # 20 FPS
        
        # Detener grabación
        print("🛑 Deteniendo grabación...")
        success = recorder.stop_recording()
        
        if success:
            print(f"✅ Grabación {'GPU' if use_gpu else 'CPU'} completada: {filename}")
            
            # Verificar archivo
            if os.path.exists(filename):
                size = os.path.getsize(filename)
                print(f"📁 Archivo generado: {size} bytes")
                return True
            else:
                print(f"❌ Archivo no encontrado: {filename}")
                return False
        else:
            print(f"❌ Error deteniendo grabación {'GPU' if use_gpu else 'CPU'}")
            return False
            
    except Exception as e:
        print(f"❌ Error durante grabación {'GPU' if use_gpu else 'CPU'}: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 Test de GPU Recording")
    print("=" * 50)
    
    # Verificar soporte GPU
    gpu_support = test_gpu_support()
    
    # Probar grabación CPU (siempre disponible)
    print("\n" + "=" * 50)
    cpu_success = test_recording(use_gpu=False)
    
    # Probar grabación GPU si está disponible
    if gpu_support:
        print("\n" + "=" * 50)
        gpu_success = test_recording(use_gpu=True)
    else:
        print("\n⚠️ Saltando test GPU (no disponible)")
        gpu_success = False
    
    # Resumen
    print("\n" + "=" * 50)
    print("📊 RESUMEN:")
    print(f"GPU Support: {'✅' if gpu_support else '❌'}")
    print(f"CPU Recording: {'✅' if cpu_success else '❌'}")
    print(f"GPU Recording: {'✅' if gpu_success else '❌' if gpu_support else '⚠️ N/A'}")
    
    if gpu_support and gpu_success:
        print("\n🎉 ¡GPU recording funcionando perfectamente!")
        print("💡 Recomendación: Usar GPU recording para mejor rendimiento")
    elif cpu_success:
        print("\n✅ CPU recording funcionando")
        print("💡 Recomendación: Usar CPU recording (GPU no disponible)")
    else:
        print("\n❌ Problemas con recording")
        print("💡 Revisar logs para más detalles")

if __name__ == "__main__":
    main() 