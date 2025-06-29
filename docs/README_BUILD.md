# 🚀 Guía para Generar Ejecutable (.exe) de Welltep

Esta guía te explica cómo crear un archivo ejecutable (.exe) de tu aplicación Welltep para distribución en Windows.

## 📋 Requisitos Previos

### 1. Python 3.8 o superior
```bash
python --version
```

### 2. Dependencias del sistema (Windows)
- **GStreamer**: Descarga e instala desde [gstreamer.freedesktop.org](https://gstreamer.freedesktop.org/download/)
- **Microsoft Visual C++ Redistributable**: Para PyQt6
- **Git Bash** (opcional): Para mejor experiencia en terminal

### 3. Dependencias de Python
Se instalarán automáticamente, pero puedes verificar:
```bash
pip install -r requirements.txt
```

## 🛠️ Métodos de Build

### Método 1: Automático (Recomendado)
Simplemente ejecuta el archivo batch:
```bash
# En Windows
build_exe.bat
```

### Método 2: Script Python
```bash
python build_exe.py
```

### Método 3: Manual con PyInstaller
```bash
# Instalar PyInstaller
pip install pyinstaller

# Crear ejecutable
pyinstaller --onefile --windowed --name=Welltep \
  --add-data "src;src" \
  --add-data "assets;assets" \
  --hidden-import PyQt6.QtCore \
  --hidden-import PyQt6.QtGui \
  --hidden-import PyQt6.QtWidgets \
  --hidden-import gi \
  --collect-all gi \
  --collect-all PyQt6 \
  main.py
```

## 📁 Archivos Generados

Después del build exitoso encontrarás:

```
dist/
├── Welltep.exe          # Ejecutable principal (--onefile)
└── Welltep/             # Directorio completo (--onedir)
    ├── Welltep.exe
    ├── _internal/       # Bibliotecas y dependencias
    └── ...
```

## 🔧 Configuración Avanzada

### Personalizar el Build
Edita `build_exe.py` para:
- Cambiar el nombre del ejecutable
- Agregar iconos personalizados
- Incluir archivos adicionales
- Modificar opciones de PyInstaller

### Opciones de PyInstaller
- `--onefile`: Un solo archivo ejecutable (más lento al iniciar)
- `--onedir`: Directorio con bibliotecas (más rápido al iniciar)
- `--windowed`: Sin ventana de consola
- `--console`: Con ventana de consola (útil para debug)

## 🚨 Solución de Problemas

### Error: "No module named 'gi'"
```bash
# Instalar PyGObject
pip install PyGObject
```

### Error: "GStreamer not found"
- Verifica la instalación de GStreamer
- Asegúrate de que esté en PATH
- Reinstala GStreamer con todas las opciones

### Error: "PyQt6 not found"
```bash
pip install PyQt6
```

### Ejecutable muy grande
- Usa `--onedir` en lugar de `--onefile`
- Excluye módulos innecesarios con `--exclude-module`

### Ejecutable no inicia
- Prueba con `--console` para ver errores
- Verifica que todas las dependencias estén incluidas
- Asegúrate de que GStreamer esté instalado en el sistema destino

## 📦 Distribución

### Para distribución local:
- Copia `dist/Welltep.exe` donde necesites
- Asegúrate de que GStreamer esté instalado en el sistema destino

### Para distribución completa:
- Usa la versión `--onedir` (carpeta `dist/Welltep/`)
- Incluye un instalador de GStreamer
- Crea un script de instalación que configure todo

## 🔍 Verificación del Ejecutable

Después de crear el ejecutable:

1. **Prueba básica**: Ejecuta `dist/Welltep.exe`
2. **Prueba en sistema limpio**: Sin Python instalado
3. **Prueba funcionalidades**: Video, audio, interfaces
4. **Prueba rendimiento**: Comparar con versión Python

## 📝 Notas Importantes

- **GStreamer**: Debe estar instalado en el sistema destino
- **Tamaño**: El ejecutable puede ser grande (~100-300MB)
- **Rendimiento**: Ligeramente más lento que ejecutar con Python
- **Compatibilidad**: Solo funciona en Windows del mismo architecture (x64/x86)

## 🆘 Soporte

Si encuentras problemas:
1. Revisa los logs de error en la consola
2. Verifica que todas las dependencias estén instaladas
3. Prueba con versiones específicas de las librerías
4. Consulta la documentación de PyInstaller

## 📚 Referencias

- [PyInstaller Documentation](https://pyinstaller.readthedocs.io/)
- [GStreamer Windows Installation](https://gstreamer.freedesktop.org/documentation/installing/on-windows.html)
- [PyQt6 Documentation](https://doc.qt.io/qtforpython/)

---

¡Buena suerte con tu build! 🎉 