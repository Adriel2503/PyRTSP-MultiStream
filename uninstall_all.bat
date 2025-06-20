@echo off
echo 🧹 Desinstalando todos los paquetes...
echo.

REM Crear archivo temporal sin pip, setuptools, wheel
echo Creando lista temporal...
findstr /v "pip==" installed_packages.txt | findstr /v "setuptools==" | findstr /v "wheel==" > temp_uninstall.txt

REM Mostrar qué se va a desinstalar
echo.
echo 📋 Paquetes a desinstalar:
type temp_uninstall.txt
echo.

REM Confirmar
set /p confirm="¿Estás seguro de desinstalar todos estos paquetes? (s/n): "
if /i "%confirm%" NEQ "s" (
    echo Cancelado.
    del temp_uninstall.txt
    pause
    exit /b 0
)

echo.
echo 🗑️ Desinstalando paquetes...
pip uninstall -r temp_uninstall.txt -y

REM Limpiar archivo temporal
del temp_uninstall.txt

echo.
echo ✅ ¡Desinstalación completada!
echo.
echo 📦 Paquetes restantes:
pip list
pause 