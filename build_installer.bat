@echo off
echo ========================================
echo   WELLTEP INSTALLER BUILDER
echo ========================================
echo.

REM Verificar si Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python no está instalado o no está en PATH
    echo    Descarga Python desde: https://python.org
    pause
    exit /b 1
)

REM Verificar si PyInstaller está instalado
python -m pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo 📦 Instalando PyInstaller...
    python -m pip install pyinstaller
)

REM Ejecutar el script de construcción
echo 🚀 Iniciando construcción...
python docs\build_installer.py

if errorlevel 1 (
    echo.
    echo ❌ Error durante la construcción
    pause
    exit /b 1
) else (
    echo.
    echo 🎉 Construcción completada exitosamente!
    echo.
    echo 📋 Archivos generados:
    echo    - dist\Welltep\Welltep.exe (Ejecutable)
    echo    - installers\WelltepInstaller.exe (Instalador)
    echo    - installers\Welltep_Portable.zip (Versión portable)
    echo.
    echo 💡 Para crear instaladores automáticamente en el futuro,
    echo    instala Inno Setup desde: https://jrsoftware.org/isinfo.php
)

pause 