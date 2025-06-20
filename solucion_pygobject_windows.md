# Solución para Instalar PyGObject en Windows

## Error Encontrado
```
ERROR: Dependency 'girepository-2.0' is required but not found.
Did not find pkg-config by name 'pkg-config'
```

Este error es típico en Windows porque PyGObject requiere dependencias del sistema que no están disponibles por defecto.

## Soluciones (en orden de recomendación)

### Método 1: MSYS2 (RECOMENDADO)

1. **Instalar MSYS2:**
   - Descargar desde: https://www.msys2.org/
   - Ejecutar el instalador y seguir las instrucciones

2. **Abrir terminal MSYS2 y ejecutar:**
   ```bash
   pacman -S mingw-w64-x86_64-python3
   pacman -S mingw-w64-x86_64-python3-gobject
   pacman -S mingw-w64-x86_64-gtk3
   pacman -S mingw-w64-x86_64-gstreamer
   pacman -S mingw-w64-x86_64-gst-plugins-base
   pacman -S mingw-w64-x86_64-gst-plugins-good
   pacman -S mingw-w64-x86_64-gst-plugins-bad
   pacman -S mingw-w64-x86_64-gst-plugins-ugly
   ```

3. **Agregar MSYS2 al PATH de Windows:**
   - Agregar `C:\msys64\mingw64\bin` al PATH del sistema

### Método 2: Conda/Miniconda (MÁS FÁCIL)

1. **Instalar Miniconda:**
   - Descargar desde: https://docs.conda.io/en/latest/miniconda.html

2. **Crear entorno con conda:**
   ```bash
   conda create -n gstreamer_env python=3.11
   conda activate gstreamer_env
   conda install -c conda-forge pygobject gtk3 gstreamer gst-plugins-base gst-plugins-good
   pip install PyQt6
   ```

### Método 3: Paquetes Precompilados

1. **Descargar paquetes desde:**
   - https://github.com/pygobject/pygobject/releases
   - Buscar archivos .whl para Windows

2. **Instalar manualmente:**
   ```bash
   pip install [archivo_descargado].whl
   ```

### Método 4: GTK Development Environment

1. **Descargar GTK para Windows:**
   - https://github.com/wingtk/gvsbuild/releases

2. **Instalar y configurar variables de entorno**

## Verificación Post-Instalación

Después de cualquier método, verificar con:
```python
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst
print("PyGObject instalado correctamente!")
```

## Alternativas si PyGObject sigue fallando

Si ningún método funciona, puedes usar solo FFmpeg:

1. **Instalar FFmpeg:**
   - Descargar desde: https://ffmpeg.org/download.html
   - Agregar al PATH

2. **Usar solo la implementación de FFmpeg:**
   - Ejecutar `ffmpeg_ultra_fast.py` en lugar de los que requieren GStreamer

## Comando de Prueba Rápida

Para probar si GStreamer está disponible en el sistema:
```bash
gst-launch-1.0 --version
```

## Notas Importantes

- En Windows, **Conda** es generalmente la opción más fácil y confiable
- Si usas MSYS2, asegúrate de usar la terminal MSYS2 MinGW64
- FFmpeg es más simple de instalar y ofrece latencia similar (80-150ms)
- Para desarrollo profesional, considera usar Linux o macOS donde GStreamer es más fácil de configurar 