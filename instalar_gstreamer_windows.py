#!/usr/bin/env python3
"""
Script automatizado para instalar GStreamer y PyGObject en Windows
"""

import subprocess
import sys
import os
import platform
import urllib.request
import tempfile
from pathlib import Path

def ejecutar_comando(comando, mostrar_salida=True):
    """Ejecutar comando y devolver el resultado"""
    try:
        if mostrar_salida:
            print(f"Ejecutando: {comando}")
        
        resultado = subprocess.run(
            comando, 
            shell=True, 
            capture_output=True, 
            text=True,
            timeout=300  # 5 minutos timeout
        )
        
        if mostrar_salida and resultado.stdout:
            print(resultado.stdout)
        
        if resultado.stderr and mostrar_salida:
            print(f"Errores: {resultado.stderr}")
        
        return resultado.returncode == 0, resultado.stdout, resultado.stderr
    
    except subprocess.TimeoutExpired:
        print("⚠️ Comando timeout - tomó más de 5 minutos")
        return False, "", "Timeout"
    except Exception as e:
        print(f"❌ Error ejecutando comando: {e}")
        return False, "", str(e)

def verificar_sistema():
    """Verificar si estamos en Windows"""
    if platform.system() != "Windows":
        print("❌ Este script está diseñado para Windows")
        return False
    
    print(f"✅ Sistema detectado: Windows {platform.release()}")
    return True

def verificar_conda():
    """Verificar si conda está disponible"""
    exito, salida, _ = ejecutar_comando("conda --version", False)
    if exito:
        print(f"✅ Conda encontrado: {salida.strip()}")
        return True
    else:
        print("❌ Conda no encontrado")
        return False

def verificar_msys2():
    """Verificar si MSYS2 está disponible"""
    msys2_paths = [
        "C:/msys64/mingw64/bin",
        "C:/msys32/mingw32/bin"
    ]
    
    for path in msys2_paths:
        if os.path.exists(path):
            print(f"✅ MSYS2 encontrado en: {path}")
            return True, path
    
    print("❌ MSYS2 no encontrado")
    return False, None

def instalar_con_conda():
    """Intentar instalar usando conda"""
    print("\n🔧 Instalando con Conda...")
    
    comandos = [
        "conda install -c conda-forge pygobject -y",
        "conda install -c conda-forge gtk3 -y", 
        "conda install -c conda-forge gstreamer -y",
        "conda install -c conda-forge gst-plugins-base -y",
        "conda install -c conda-forge gst-plugins-good -y",
        "pip install PyQt6"
    ]
    
    for comando in comandos:
        print(f"\n📦 {comando}")
        exito, _, _ = ejecutar_comando(comando)
        if not exito:
            print(f"❌ Falló: {comando}")
            return False
    
    print("✅ Instalación con Conda completada")
    return True

def instalar_con_msys2(msys2_path):
    """Intentar instalar usando MSYS2"""
    print(f"\n🔧 Instalando con MSYS2 desde {msys2_path}...")
    
    # Agregar MSYS2 al PATH temporalmente
    env = os.environ.copy()
    env['PATH'] = f"{msys2_path};{env['PATH']}"
    
    paquetes = [
        "mingw-w64-x86_64-python3-gobject",
        "mingw-w64-x86_64-gtk3",
        "mingw-w64-x86_64-gstreamer",
        "mingw-w64-x86_64-gst-plugins-base",
        "mingw-w64-x86_64-gst-plugins-good",
        "mingw-w64-x86_64-gst-plugins-bad"
    ]
    
    for paquete in paquetes:
        comando = f"pacman -S {paquete} --noconfirm"
        print(f"\n📦 {comando}")
        
        resultado = subprocess.run(
            comando,
            shell=True,
            env=env,
            capture_output=True,
            text=True
        )
        
        if resultado.returncode != 0:
            print(f"❌ Falló instalando {paquete}")
            print(resultado.stderr)
            return False
    
    print("✅ Instalación con MSYS2 completada")
    return True

def instalar_ffmpeg():
    """Instalar FFmpeg como alternativa"""
    print("\n🎥 Instalando FFmpeg como alternativa...")
    
    # Verificar si ya está instalado
    exito, salida, _ = ejecutar_comando("ffmpeg -version", False)
    if exito:
        print("✅ FFmpeg ya está instalado")
        return True
    
    # Intentar instalar con chocolatey
    exito, _, _ = ejecutar_comando("choco install ffmpeg -y", False)
    if exito:
        print("✅ FFmpeg instalado con Chocolatey")
        return True
    
    # Intentar instalar con winget
    exito, _, _ = ejecutar_comando("winget install ffmpeg", False)
    if exito:
        print("✅ FFmpeg instalado con winget")
        return True
    
    print("❌ No se pudo instalar FFmpeg automáticamente")
    print("💡 Descárgalo manualmente desde: https://ffmpeg.org/download.html")
    return False

def verificar_instalacion():
    """Verificar que la instalación funcionó"""
    print("\n🔍 Verificando instalación...")
    
    # Verificar PyGObject
    try:
        import gi
        gi.require_version('Gst', '1.0')
        from gi.repository import Gst
        print("✅ PyGObject y GStreamer funcionando")
        return True
    except ImportError as e:
        print(f"❌ PyGObject falló: {e}")
    except Exception as e:
        print(f"❌ GStreamer falló: {e}")
    
    # Verificar FFmpeg como alternativa
    exito, _, _ = ejecutar_comando("ffmpeg -version", False)
    if exito:
        print("✅ FFmpeg disponible como alternativa")
        return True
    
    return False

def mostrar_instrucciones_manuales():
    """Mostrar instrucciones para instalación manual"""
    print("""
🔧 INSTRUCCIONES PARA INSTALACIÓN MANUAL:

1. OPCIÓN CONDA (MÁS FÁCIL):
   - Instalar Miniconda: https://docs.conda.io/en/latest/miniconda.html
   - Ejecutar:
     conda create -n gstreamer_env python=3.11
     conda activate gstreamer_env
     conda install -c conda-forge pygobject gtk3 gstreamer gst-plugins-base
     pip install PyQt6

2. OPCIÓN MSYS2:
   - Instalar MSYS2: https://www.msys2.org/
   - Abrir terminal MSYS2 MinGW64
   - Ejecutar: pacman -S mingw-w64-x86_64-python3-gobject mingw-w64-x86_64-gstreamer

3. OPCIÓN SOLO FFMPEG:
   - Descargar FFmpeg: https://ffmpeg.org/download.html
   - Agregar al PATH de Windows
   - Usar solo ffmpeg_ultra_fast.py

4. USAR LA APLICACIÓN ORIGINAL:
   - Si solo necesitas funcionalidad básica, usa camara_ip_viewer.py
   - No requiere GStreamer, solo OpenCV y VLC
""")

def main():
    print("🚀 Instalador Automático de GStreamer para Windows")
    print("=" * 50)
    
    if not verificar_sistema():
        return
    
    instalacion_exitosa = False
    
    # Intentar con Conda primero
    if verificar_conda():
        if instalar_con_conda():
            instalacion_exitosa = True
    
    # Si Conda falló, intentar MSYS2
    if not instalacion_exitosa:
        msys2_disponible, msys2_path = verificar_msys2()
        if msys2_disponible:
            if instalar_con_msys2(msys2_path):
                instalacion_exitosa = True
    
    # Instalar FFmpeg como alternativa
    instalar_ffmpeg()
    
    # Verificar instalación
    if verificar_instalacion():
        print("\n🎉 ¡INSTALACIÓN EXITOSA!")
        print("Ahora puedes ejecutar:")
        print("  - gstreamer_viewer.py (latencia ultra baja)")
        print("  - ffmpeg_ultra_fast.py (alternativa confiable)")
        print("  - camara_ip_viewer.py (original con VLC)")
    else:
        print("\n❌ Instalación automática falló")
        mostrar_instrucciones_manuales()

if __name__ == "__main__":
    main() 