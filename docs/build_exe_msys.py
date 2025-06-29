#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para crear ejecutable de Welltep - Versión MSYS64
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def detect_environment():
    """Detectar si estamos en MSYS64"""
    msys_env = os.environ.get('MSYSTEM', '')
    if msys_env:
        print(f"🔍 Detectado entorno MSYS64: {msys_env}")
        return True
    return False

def setup_msys64_paths():
    """Configurar paths específicos para MSYS64"""
    if detect_environment():
        # Agregar paths típicos de MSYS64
        msys64_paths = [
            "/mingw64/bin",
            "/mingw64/lib",
            "/usr/bin",
            "/usr/lib"
        ]
        
        current_path = os.environ.get('PATH', '')
        for path in msys64_paths:
            if path not in current_path:
                os.environ['PATH'] = f"{path}:{current_path}"
                print(f"➕ Agregando al PATH: {path}")
        
        # Variables específicas para GStreamer
        gst_plugin_path = "/mingw64/lib/gstreamer-1.0"
        if os.path.exists(gst_plugin_path):
            os.environ['GST_PLUGIN_PATH'] = gst_plugin_path
            print(f"🎯 GST_PLUGIN_PATH: {gst_plugin_path}")
        
        # PKG_CONFIG_PATH para bibliotecas
        pkg_config_path = "/mingw64/lib/pkgconfig"
        if os.path.exists(pkg_config_path):
            os.environ['PKG_CONFIG_PATH'] = pkg_config_path
            print(f"📦 PKG_CONFIG_PATH: {pkg_config_path}")

def clean_build_dirs():
    """Limpiar directorios de build anteriores"""
    dirs_to_clean = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"🧹 Limpiando directorio: {dir_name}")
            shutil.rmtree(dir_name)
    
    # Limpiar archivos .spec
    for spec_file in Path('.').glob('*.spec'):
        print(f"🧹 Eliminando archivo spec: {spec_file}")
        spec_file.unlink()

def install_pyinstaller():
    """Instalar PyInstaller si no está instalado"""
    try:
        import PyInstaller
        print("✅ PyInstaller ya está instalado")
    except ImportError:
        print("📦 Instalando PyInstaller...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"])

def create_executable_msys64():
    """Crear el ejecutable usando PyInstaller en MSYS64"""
    
    # Configurar paths para MSYS64
    setup_msys64_paths()
    
    # Comando PyInstaller con configuraciones específicas para MSYS64
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",                    # Un solo archivo ejecutable
        "--windowed",                   # Sin ventana de consola
        "--name=Welltep",              # Nombre del ejecutable
        
        # Incluir directorios y archivos necesarios
        "--add-data", "src;src",
        "--add-data", "assets;assets",
        
        # Hooks para PyQt6 y GStreamer
        "--hidden-import", "PyQt6.QtCore",
        "--hidden-import", "PyQt6.QtGui", 
        "--hidden-import", "PyQt6.QtWidgets",
        "--hidden-import", "gi",
        "--hidden-import", "gi.repository.Gst",
        "--hidden-import", "gi.repository.GObject",
        "--hidden-import", "gi.repository.GLib",
        "--hidden-import", "cairo",
        "--hidden-import", "numpy",
        "--hidden-import", "psutil",
        
        # Incluir bibliotecas específicas de MSYS64
        "--collect-all", "gi",
        "--collect-all", "PyQt6",
        
        # Paths específicos para GStreamer en MSYS64
        "--add-binary", "/mingw64/bin/gst-launch-1.0.exe;.",
        "--add-binary", "/mingw64/bin/libgstreamer-1.0-0.dll;.",
        "--add-binary", "/mingw64/bin/libgobject-2.0-0.dll;.",
        "--add-binary", "/mingw64/bin/libglib-2.0-0.dll;.",
        
        # Plugins de GStreamer
        "--add-data", "/mingw64/lib/gstreamer-1.0;gstreamer-1.0",
        
        # Archivo principal
        "main.py"
    ]
    
    print("🏗️  Creando ejecutable para MSYS64...")
    print("📋 Comando:", " ".join(cmd))
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Ejecutable creado exitosamente!")
        print(f"📁 Ubicación: {os.path.abspath('dist/Welltep.exe')}")
        return True
    except subprocess.CalledProcessError as e:
        print("❌ Error creando ejecutable:")
        print(f"Código de salida: {e.returncode}")
        print(f"Stdout: {e.stdout}")
        print(f"Stderr: {e.stderr}")
        return False

def create_alternative_build_msys64():
    """Crear build alternativo para MSYS64"""
    print("\n🔄 Intentando build alternativo (directorio)...")
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onedir",                     # Crear directorio con archivos
        "--windowed",
        "--name=Welltep",
        "--add-data", "src;src",
        "--add-data", "assets;assets",
        "--hidden-import", "PyQt6.QtCore",
        "--hidden-import", "PyQt6.QtGui", 
        "--hidden-import", "PyQt6.QtWidgets",
        "--hidden-import", "gi",
        "--collect-all", "gi",
        "--collect-all", "PyQt6",
        "--add-data", "/mingw64/lib/gstreamer-1.0;gstreamer-1.0",
        "main.py"
    ]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Build alternativo creado exitosamente!")
        print(f"📁 Ubicación: {os.path.abspath('dist/Welltep/')}")
        return True
    except subprocess.CalledProcessError as e:
        print("❌ Error en build alternativo:")
        print(f"Stderr: {e.stderr}")
        return False

def verify_gstreamer():
    """Verificar que GStreamer esté disponible en MSYS64"""
    print("🔍 Verificando GStreamer en MSYS64...")
    
    try:
        result = subprocess.run(['gst-launch-1.0', '--version'], 
                              capture_output=True, text=True, check=True)
        print("✅ GStreamer encontrado:")
        print(result.stdout.strip())
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ GStreamer no encontrado en PATH")
        print("💡 Asegúrate de que GStreamer esté instalado en MSYS64:")
        print("   pacman -S mingw-w64-x86_64-gstreamer")
        print("   pacman -S mingw-w64-x86_64-gst-plugins-base")
        print("   pacman -S mingw-w64-x86_64-gst-plugins-good")
        return False

def main():
    """Función principal"""
    print("🚀 === Script de Build para Welltep (MSYS64) ===")
    print("📦 Creando ejecutable Windows (.exe) desde MSYS64")
    print("=" * 50)
    
    # Verificar que estamos en el directorio correcto
    if not os.path.exists('main.py'):
        print("❌ Error: No se encuentra main.py")
        print("   Ejecuta este script desde el directorio raíz del proyecto")
        return 1
    
    # Verificar entorno MSYS64
    if not detect_environment():
        print("⚠️  No se detectó entorno MSYS64")
        print("💡 Asegúrate de ejecutar desde MSYS64 terminal")
    
    # Verificar GStreamer
    if not verify_gstreamer():
        print("⚠️  Continuando sin verificación de GStreamer...")
    
    # Limpiar builds anteriores
    clean_build_dirs()
    
    # Instalar PyInstaller
    install_pyinstaller()
    
    # Crear ejecutable
    success = create_executable_msys64()
    
    if not success:
        print("\n⚠️  El build principal falló, intentando alternativo...")
        success = create_alternative_build_msys64()
    
    if success:
        print("\n🎉 ¡BUILD COMPLETADO!")
        print("📋 Archivos generados:")
        if os.path.exists('dist/Welltep.exe'):
            print(f"   • Ejecutable: dist/Welltep.exe")
        if os.path.exists('dist/Welltep/'):
            print(f"   • Directorio: dist/Welltep/")
        
        print("\n📝 Notas importantes para MSYS64:")
        print("   • El ejecutable incluye bibliotecas de GStreamer de MSYS64")
        print("   • Debería funcionar en sistemas Windows sin MSYS64")
        print("   • Prueba el ejecutable en un sistema Windows limpio")
        print("   • Si hay problemas, instala GStreamer nativo de Windows")
        
        return 0
    else:
        print("\n❌ Error: No se pudo crear el ejecutable")
        print("💡 Sugerencias para MSYS64:")
        print("   • Verifica que Python esté instalado: python --version")
        print("   • Instala dependencias: pip install -r requirements.txt")
        print("   • Verifica GStreamer: gst-launch-1.0 --version")
        print("   • Intenta desde terminal nativa de Windows")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 