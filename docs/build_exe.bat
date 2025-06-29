@echo off
echo ========================================
echo    WELLTEP - GENERADOR DE EJECUTABLE
echo ========================================
echo.

REM Verificar si Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Python no está instalado o no está en PATH
    echo 💡 Instala Python desde https://python.org
    pause
    exit /b 1
)

echo ✅ Python encontrado
echo.

REM Instalar dependencias
echo 📦 Instalando dependencias...
pip install -r requirements.txt
if errorlevel 1 (
    echo ⚠️  Algunas dependencias podrían no haberse instalado correctamente
    echo 💡 Continuando con el build...
)

echo.
echo 🏗️  Iniciando proceso de build...
echo.

REM Ejecutar script de build
python build_exe.py

echo.
echo ✨ Proceso completado
echo 📁 Revisa la carpeta 'dist' para encontrar el ejecutable
echo.
pause 