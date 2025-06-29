#!/bin/bash
# Script para crear ejecutable de Welltep en MSYS64

echo "🚀 === WELLTEP - GENERADOR DE EJECUTABLE (MSYS64) ==="
echo "📦 Creando ejecutable Windows (.exe) desde MSYS64"
echo "================================================="
echo

# Verificar que estamos en el directorio correcto
if [ ! -f "main.py" ]; then
    echo "❌ Error: No se encuentra main.py"
    echo "   Ejecuta este script desde el directorio raíz del proyecto"
    exit 1
fi

# Verificar entorno MSYS64
if [ -z "$MSYSTEM" ]; then
    echo "⚠️  No se detectó entorno MSYS64 (variable MSYSTEM no definida)"
    echo "💡 Asegúrate de ejecutar desde MSYS64 terminal"
else
    echo "✅ Entorno MSYS64 detectado: $MSYSTEM"
fi

# Verificar Python
echo "🔍 Verificando Python..."
if ! command -v python &> /dev/null; then
    echo "❌ Error: Python no está instalado o no está en PATH"
    echo "💡 Instala Python en MSYS64: pacman -S python"
    exit 1
fi

python_version=$(python --version)
echo "✅ $python_version encontrado"

# Verificar GStreamer
echo "🔍 Verificando GStreamer..."
if command -v gst-launch-1.0 &> /dev/null; then
    gst_version=$(gst-launch-1.0 --version 2>&1 | head -n1)
    echo "✅ GStreamer encontrado: $gst_version"
else
    echo "❌ GStreamer no encontrado en PATH"
    echo "💡 Instala GStreamer en MSYS64:"
    echo "   pacman -S mingw-w64-x86_64-gstreamer"
    echo "   pacman -S mingw-w64-x86_64-gst-plugins-base"
    echo "   pacman -S mingw-w64-x86_64-gst-plugins-good"
    echo "   pacman -S mingw-w64-x86_64-gst-plugins-bad"
    echo "   pacman -S mingw-w64-x86_64-gst-plugins-ugly"
    echo "⚠️  Continuando sin verificación completa..."
fi

# Verificar pip
echo "🔍 Verificando pip..."
if ! command -v pip &> /dev/null; then
    echo "❌ Error: pip no está instalado"
    echo "💡 Instala pip: python -m ensurepip --upgrade"
    exit 1
fi
echo "✅ pip encontrado"

# Instalar dependencias
echo
echo "📦 Instalando dependencias de Python..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "⚠️  Algunas dependencias podrían no haberse instalado correctamente"
    echo "💡 Continuando con el build..."
fi

# Instalar PyInstaller si no está instalado
echo
echo "📦 Verificando PyInstaller..."
if ! python -c "import PyInstaller" 2>/dev/null; then
    echo "📦 Instalando PyInstaller..."
    pip install pyinstaller
else
    echo "✅ PyInstaller ya está instalado"
fi

echo
echo "🏗️  Iniciando proceso de build..."
echo

# Ejecutar script de build específico para MSYS64
python build_exe_msys.py

exit_code=$?

echo
if [ $exit_code -eq 0 ]; then
    echo "✨ ¡Proceso completado exitosamente!"
    echo "📁 Revisa la carpeta 'dist' para encontrar el ejecutable"
    
    if [ -f "dist/Welltep.exe" ]; then
        file_size=$(stat -f%z "dist/Welltep.exe" 2>/dev/null || stat -c%s "dist/Welltep.exe" 2>/dev/null)
        if [ ! -z "$file_size" ]; then
            size_mb=$((file_size / 1024 / 1024))
            echo "📊 Tamaño del ejecutable: ${size_mb}MB"
        fi
    fi
    
    echo
    echo "📝 Notas importantes:"
    echo "   • El ejecutable incluye bibliotecas de GStreamer de MSYS64"
    echo "   • Debería funcionar en sistemas Windows sin MSYS64"
    echo "   • Prueba el ejecutable en un sistema Windows limpio"
    echo "   • Si hay problemas, instala GStreamer nativo de Windows"
else
    echo "❌ Error durante el proceso de build"
    echo "💡 Revisa los mensajes de error arriba"
    echo "💡 Puedes intentar ejecutar: python build_exe.py (versión estándar)"
fi

echo
read -p "Presiona Enter para continuar..." 