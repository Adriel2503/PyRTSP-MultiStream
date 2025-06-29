#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para crear ejecutable de Welltep
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

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

def create_executable():
    """Crear el ejecutable usando PyInstaller"""
    
    # Comando PyInstaller con configuraciones específicas
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",                    # Un solo archivo ejecutable
        "--windowed",                   # Sin ventana de consola
        "--name=Welltep",              # Nombre del ejecutable
        # "--icon=assets/images/Logo.png", # Icono comentado temporalmente
        
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
        
        # Incluir bibliotecas del sistema
        "--collect-all", "gi",
        "--collect-all", "PyQt6",
        
        # Archivo principal
        "main.py"
    ]
    
    print("🏗️  Creando ejecutable...")
    print("📋 Comando:", " ".join(cmd))
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Ejecutable creado exitosamente!")
        print(f"📁 Ubicación: {os.path.abspath('dist/Welltep.exe')}")
        return True
    except subprocess.CalledProcessError as e:
        print("❌ Error creando ejecutable:")
        print(f"Código de salida: {e.returncode}")
        print(f"Error: {e.stderr}")
        return False

def create_alternative_build():
    """Crear build alternativo con más opciones"""
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
        "main.py"
    ]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Build alternativo creado exitosamente!")
        print(f"📁 Ubicación: {os.path.abspath('dist/Welltep/')}")
        return True
    except subprocess.CalledProcessError as e:
        print("❌ Error en build alternativo:")
        print(f"Error: {e.stderr}")
        return False

def main():
    """Función principal"""
    print("🚀 === Script de Build para Welltep ===")
    print("📦 Creando ejecutable Windows (.exe)")
    print("=" * 50)
    
    # Verificar que estamos en el directorio correcto
    if not os.path.exists('main.py'):
        print("❌ Error: No se encuentra main.py")
        print("   Ejecuta este script desde el directorio raíz del proyecto")
        return 1
    
    # Limpiar builds anteriores
    clean_build_dirs()
    
    # Instalar PyInstaller
    install_pyinstaller()
    
    # Crear ejecutable
    success = create_executable()
    
    if not success:
        print("\n⚠️  El build principal falló, intentando alternativo...")
        success = create_alternative_build()
    
    if success:
        print("\n🎉 ¡BUILD COMPLETADO!")
        print("📋 Archivos generados:")
        if os.path.exists('dist/Welltep.exe'):
            print(f"   • Ejecutable: dist/Welltep.exe")
        if os.path.exists('dist/Welltep/'):
            print(f"   • Directorio: dist/Welltep/")
        
        print("\n📝 Notas importantes:")
        print("   • Asegúrate de que GStreamer esté instalado en el sistema destino")
        print("   • El ejecutable incluye todas las dependencias de Python")
        print("   • Prueba el ejecutable en diferentes sistemas Windows")
        
        return 0
    else:
        print("\n❌ Error: No se pudo crear el ejecutable")
        print("💡 Sugerencias:")
        print("   • Verifica que todas las dependencias estén instaladas")
        print("   • Ejecuta: pip install -r requirements.txt")
        print("   • Revisa los errores mostrados arriba")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 