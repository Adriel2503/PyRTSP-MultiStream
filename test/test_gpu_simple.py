#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test simple para GPU recording - Sin dependencias PyQt6
"""

import subprocess
import numpy as np
import time
import os

def check_ffmpeg_gpu_support():
    """Verificar soporte GPU en FFmpeg"""
    print("🔍 Verificando soporte GPU en FFmpeg...")
    
    try:
        result = subprocess.run(
            ['ffmpeg', '-hide_banner', '-encoders'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        gpu_encoders = {
            'h264_nvenc': 'NVIDIA NVENC',
            'h264_amf': 'AMD AMF', 
            'h264_qsv': 'Intel Quick Sync',
            'hevc_nvenc': 'NVIDIA HEVC',
            'av1_nvenc': 'NVIDIA AV1'
        }
        
        available = {}
        for encoder, description in gpu_encoders.items():
            if encoder in result.stdout:
                available[encoder] = description
                print(f"  ✅ {encoder} - {description}")
        
        if available:
            print(f"\n🎉 {len(available)} encoders GPU disponibles!")
            return list(available.keys())[0]  # Retornar el primero
        else:
            print("\n❌ No hay encoders GPU disponibles")
            return None
            
    except Exception as e:
        print(f"❌ Error verificando FFmpeg: {e}")
        return None

def test_gpu_recording(encoder):
    """Probar grabación con encoder GPU específico"""
    print(f"\n🎬 Probando grabación con {encoder}...")
    
    # Configuración
    width, height = 640, 480
    fps = 20
    duration_seconds = 3
    total_frames = fps * duration_seconds
    filename = f"test_{encoder.replace('_', '-')}.mp4"
    
    # Comando FFmpeg
    ffmpeg_cmd = [
        'ffmpeg', '-y',
        '-f', 'rawvideo',
        '-vcodec', 'rawvideo', 
        '-s', f'{width}x{height}',
        '-pix_fmt', 'rgb24',
        '-r', str(fps),
        '-i', '-',
        '-c:v', encoder,
        '-preset', 'fast',
        '-b:v', '2M',
        '-pix_fmt', 'yuv420p',
        '-movflags', '+faststart',
        filename
    ]
    
    print(f"🔧 Comando: {' '.join(ffmpeg_cmd)}")
    
    try:
        # Iniciar proceso FFmpeg
        process = subprocess.Popen(
            ffmpeg_cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=10**8
        )
        
        print(f"📹 Generando {total_frames} frames...")
        
        # Generar y enviar frames
        for i in range(total_frames):
            # Crear frame de prueba
            frame = np.zeros((height, width, 3), dtype=np.uint8)
            
            # Patrón de colores rotativo
            t = i / total_frames
            frame[:, :, 0] = int(255 * (0.5 + 0.5 * np.sin(2 * np.pi * t)))  # Rojo
            frame[:, :, 1] = int(255 * (0.5 + 0.5 * np.sin(2 * np.pi * t + 2.1)))  # Verde  
            frame[:, :, 2] = int(255 * (0.5 + 0.5 * np.sin(2 * np.pi * t + 4.2)))  # Azul
            
            # Agregar texto del frame
            frame[height//2-20:height//2+20, i*width//total_frames:i*width//total_frames+40] = [255, 255, 255]
            
            # Enviar frame
            process.stdin.write(frame.tobytes())
            
            if i % 10 == 0:
                print(f"  Frame {i+1}/{total_frames}")
        
        # Cerrar entrada y esperar
        process.stdin.close()
        stdout, stderr = process.communicate(timeout=30)
        
        if process.returncode == 0:
            if os.path.exists(filename):
                size = os.path.getsize(filename)
                print(f"✅ Grabación exitosa: {filename} ({size} bytes)")
                return True
            else:
                print(f"❌ Archivo no encontrado: {filename}")
                return False
        else:
            print(f"❌ FFmpeg falló (código {process.returncode})")
            if stderr:
                print(f"Error: {stderr.decode()}")
            return False
            
    except Exception as e:
        print(f"❌ Error durante grabación: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 Test GPU Recording Simple")
    print("=" * 50)
    
    # Verificar soporte
    best_encoder = check_ffmpeg_gpu_support()
    
    if best_encoder:
        print("\n" + "=" * 50)
        success = test_gpu_recording(best_encoder)
        
        if success:
            print(f"\n🎉 ¡GPU recording con {best_encoder} funciona perfectamente!")
        else:
            print(f"\n❌ Problemas con {best_encoder}")
    else:
        print("\n⚠️ No hay encoders GPU disponibles")
        print("💡 Verifica drivers NVIDIA/AMD/Intel")

if __name__ == "__main__":
    main() 