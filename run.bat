@echo off
echo 📹 Iniciando Visor de Camara IP...
echo.

REM Activar entorno virtual si existe
if exist "venv\Scripts\activate.bat" (
    echo Activando entorno virtual...
    call venv\Scripts\activate.bat
)

REM Verificar si Python está disponible
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Python no está instalado o no está en PATH
    echo Instala Python desde: https://python.org
    pause
    exit /b 1
)

REM Verificar si las dependencias están instaladas
python -c "import PyQt6" >nul 2>&1
if errorlevel 1 (
    echo 📦 Instalando dependencias...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ Error instalando dependencias
        pause
        exit /b 1
    )
)

REM Ejecutar aplicación
echo 🚀 Iniciando aplicación...
python camara_ip_viewer.py

REM Si hay error
if errorlevel 1 (
    echo.
    echo ❌ Error ejecutando la aplicación
    echo Verifica que:
    echo - VLC Media Player esté instalado
    echo - Todas las dependencias estén instaladas
    echo - No hay conflictos de versiones de Python
    pause
)

pause 