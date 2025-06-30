#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para generar instalador completo de Welltep
Incluye construcción del ejecutable y creación del instalador
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

class WelltepInstaller:
    def __init__(self):
        self.root_dir = Path(__file__).parent.parent
        self.dist_dir = self.root_dir / "dist"
        self.installers_dir = self.root_dir / "installers"
        
    def clean_build(self):
        """Limpia directorios de build anteriores"""
        print("🧹 Limpiando builds anteriores...")
        
        dirs_to_clean = [
            self.root_dir / "build",
            self.dist_dir,
            self.installers_dir
        ]
        
        for dir_path in dirs_to_clean:
            if dir_path.exists():
                shutil.rmtree(dir_path)
                print(f"   ✅ Eliminado: {dir_path}")
                
        self.installers_dir.mkdir(exist_ok=True)
    
    def build_executable(self):
        """Construye el ejecutable usando PyInstaller"""
        print("🔨 Construyendo ejecutable...")
        
        pyinstaller_cmd = [
            "pyinstaller",
            "--onedir",  # Usar onedir para instalador
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
            "--collect-all", "cairo",
            "--icon", str(self.root_dir / "assets" / "icons" / "welltep.ico") if (self.root_dir / "assets" / "icons" / "welltep.ico").exists() else None,
            str(self.root_dir / "main.py")
        ]
        
        # Filtrar None values
        pyinstaller_cmd = [cmd for cmd in pyinstaller_cmd if cmd is not None]
        
        try:
            result = subprocess.run(pyinstaller_cmd, check=True, cwd=self.root_dir)
            print("   ✅ Ejecutable creado exitosamente")
            return True
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Error al crear ejecutable: {e}")
            return False
    
    def create_installer(self):
        """Crea el instalador usando Inno Setup"""
        print("📦 Creando instalador...")
        
        inno_script = self.root_dir / "docs" / "create_installer.iss"
        
        if not inno_script.exists():
            print(f"   ❌ Script de Inno Setup no encontrado: {inno_script}")
            return False
            
        # Buscar Inno Setup en ubicaciones comunes
        inno_paths = [
            r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
            r"C:\Program Files\Inno Setup 6\ISCC.exe",
            r"C:\Program Files (x86)\Inno Setup 5\ISCC.exe",
            r"C:\Program Files\Inno Setup 5\ISCC.exe"
        ]
        
        inno_exe = None
        for path in inno_paths:
            if os.path.exists(path):
                inno_exe = path
                break
                
        if not inno_exe:
            print("   ❌ Inno Setup no encontrado. Instalarlo desde: https://jrsoftware.org/isinfo.php")
            print("   💡 Alternativa: Usar NSIS o crear ZIP con el ejecutable")
            return False
            
        try:
            result = subprocess.run([inno_exe, str(inno_script)], check=True, cwd=self.root_dir)
            print("   ✅ Instalador creado exitosamente")
            return True
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Error al crear instalador: {e}")
            return False
    
    def create_portable_zip(self):
        """Crea una versión portable en ZIP como alternativa"""
        print("📁 Creando versión portable...")
        
        welltep_dir = self.dist_dir / "Welltep"
        if not welltep_dir.exists():
            print("   ❌ Directorio del ejecutable no encontrado")
            return False
            
        zip_path = self.installers_dir / "Welltep_Portable.zip"
        
        try:
            shutil.make_archive(
                str(zip_path.with_suffix("")),
                'zip',
                str(welltep_dir.parent),
                str(welltep_dir.name)
            )
            print(f"   ✅ Versión portable creada: {zip_path}")
            return True
        except Exception as e:
            print(f"   ❌ Error al crear ZIP: {e}")
            return False
    
    def verify_build(self):
        """Verifica que los archivos se hayan creado correctamente"""
        print("🔍 Verificando build...")
        
        exe_path = self.dist_dir / "Welltep" / "Welltep.exe"
        installer_path = self.installers_dir / "WelltepInstaller.exe"
        portable_path = self.installers_dir / "Welltep_Portable.zip"
        
        results = {
            "Ejecutable": exe_path.exists(),
            "Instalador": installer_path.exists(),
            "Portable": portable_path.exists()
        }
        
        for item, exists in results.items():
            status = "✅" if exists else "❌"
            print(f"   {status} {item}")
            
        return any(results.values())
    
    def show_summary(self):
        """Muestra resumen de archivos generados"""
        print("\n📋 RESUMEN DE DISTRIBUCIÓN:")
        print("=" * 50)
        
        files_info = [
            (self.dist_dir / "Welltep" / "Welltep.exe", "Ejecutable principal"),
            (self.installers_dir / "WelltepInstaller.exe", "Instalador Windows"), 
            (self.installers_dir / "Welltep_Portable.zip", "Versión portable")
        ]
        
        for file_path, description in files_info:
            if file_path.exists():
                size_mb = file_path.stat().st_size / (1024 * 1024)
                print(f"✅ {description}")
                print(f"   📁 {file_path}")
                print(f"   💾 Tamaño: {size_mb:.1f} MB")
                print()
            else:
                print(f"❌ {description} - No creado")
                print()
    
    def run(self):
        """Ejecuta todo el proceso de build"""
        print("🚀 WELLTEP INSTALLER BUILDER")
        print("=" * 50)
        
        try:
            # Paso 1: Limpiar
            self.clean_build()
            
            # Paso 2: Construir ejecutable
            if not self.build_executable():
                print("❌ Falló la construcción del ejecutable")
                return False
                
            # Paso 3: Crear instalador
            installer_success = self.create_installer()
            
            # Paso 4: Crear versión portable (siempre)
            portable_success = self.create_portable_zip()
            
            # Paso 5: Verificar
            if self.verify_build():
                self.show_summary()
                print("🎉 ¡Build completado!")
                
                if not installer_success:
                    print("\n💡 NOTA: El instalador no se pudo crear.")
                    print("   Instala Inno Setup para generar instaladores automáticamente.")
                    print("   Mientras tanto, usa la versión portable.")
                    
                return True
            else:
                print("❌ No se generaron archivos válidos")
                return False
                
        except Exception as e:
            print(f"❌ Error general: {e}")
            return False

def main():
    # Verificar que estamos en el directorio correcto
    if not (Path.cwd() / "main.py").exists():
        print("❌ Ejecuta este script desde el directorio raíz del proyecto")
        sys.exit(1)
        
    installer = WelltepInstaller()
    success = installer.run()
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main() 