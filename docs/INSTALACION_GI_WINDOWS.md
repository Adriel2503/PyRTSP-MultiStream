# 🔧 Guía: Instalación de PyGObject (gi) en Windows

## 🚨 **Problema**

Al ejecutar `python main.py` aparece el error:
```
ModuleNotFoundError: No module named 'gi'
```

**PyGObject** (`gi`) es necesario para **GStreamer** y **GTK** en Welltep, pero es complicado de instalar en Windows porque requiere librerías del sistema.

## 🎯 **Opciones de Instalación**

### **🥇 Opción 1: GTK Runtime para Windows (RECOMENDADO)**

**✅ Mejor para generar .exe con tu Python del sistema**

#### **Paso 1: Instalar GTK Runtime**
1. **Descargar**: https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases
2. **Archivo**: `gtk3-runtime-3.24.31-2022-01-04-ts-win64.exe`
3. **Ejecutar** el instalador (se instala en `C:\Program Files\GTK3-Runtime Win64\`)
4. **Automáticamente** se agrega al PATH del sistema

#### **Paso 2: Instalar PyGObject**
```bash
pip install PyGObject
```

#### **Paso 3: Verificar instalación**
```python
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst
print("✅ PyGObject funcionando!")
```

#### **Paso 4: Generar .exe**
```bash
python docs/build_installer.py
```

---

### **🥈 Opción 2: Conda (ALTERNATIVA)**

**✅ Más fácil pero requiere Conda**

#### **Paso 1: Instalar Miniconda**
- Descargar: https://docs.conda.io/en/latest/miniconda.html

#### **Paso 2: Crear entorno**
```bash
conda create -n welltep python=3.11
conda activate welltep
```

#### **Paso 3: Instalar dependencias**
```bash
conda install pygobject gtk3 gstreamer
pip install pyinstaller
pip install PyQt6 numpy psutil pycairo
```

#### **Paso 4: Generar .exe**
```bash
# Desde el entorno conda:
python docs/build_installer.py
```

---

### **🥉 Opción 3: Todo en MSYS2**

**⚠️ Funciona pero usa Python de MSYS2, no del sistema**

#### **Instalar en MSYS2:**
```bash
# En terminal MSYS2:
pacman -S mingw-w64-x86_64-python-pip
pacman -S mingw-w64-x86_64-python-pyinstaller
pacman -S mingw-w64-x86_64-python-gobject
pacman -S mingw-w64-x86_64-gtk3
pacman -S mingw-w64-x86_64-gstreamer
pacman -S mingw-w64-x86_64-python-pyqt6
```

#### **Generar .exe desde MSYS2:**
```bash
/mingw64/bin/python docs/build_installer.py
```

**❌ Desventaja**: Usas Python de MSYS2, no el del sistema Windows

---

### **🔧 Opción 4: Solución Temporal (TESTING)**

**Para probar si el resto del código funciona sin GStreamer**

#### **Usar el mock temporal:**
```python
# Al inicio de main.py, agregar:
import gi_mock  # El archivo que creamos
```

**⚠️ Solo para testing**, no para producción.

---

## 📋 **Comparación de Opciones**

| Opción | Facilidad | .exe Compatible | Python Sistema | Recomendación |
|--------|-----------|-----------------|----------------|---------------|
| **GTK Runtime** | Media | ✅ | ✅ | ⭐⭐⭐⭐⭐ |
| **Conda** | Fácil | ✅ | ❌ (Conda) | ⭐⭐⭐⭐ |
| **MSYS2** | Media | ✅ | ❌ (MSYS2) | ⭐⭐⭐ |
| **Mock** | Fácil | ❌ | ✅ | ⭐ (solo test) |

## 🚀 **Proceso Completo Recomendado**

### **Para generar .exe de Welltep:**

1. **Instalar GTK Runtime** (Opción 1)
2. **Instalar todas las dependencias**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Verificar funcionamiento**:
   ```bash
   python main.py
   ```
4. **Generar instalador**:
   ```bash
   python docs/build_installer.py
   ```

## 🔍 **Verificación de Instalación**

### **Script de prueba:**
```python
# test_gi.py
try:
    import gi
    print("✅ gi importado correctamente")
    
    gi.require_version('Gst', '1.0')
    from gi.repository import Gst
    print("✅ GStreamer disponible")
    
    Gst.init(None)
    print("✅ GStreamer inicializado")
    
    import PyQt6
    print("✅ PyQt6 disponible")
    
    print("🎉 ¡Todo listo para generar .exe!")
    
except ImportError as e:
    print(f"❌ Error: {e}")
    print("💡 Instala las dependencias según la guía")
```

## 🚨 **Problemas Comunes**

### **Error: "gtk not found"**
- **Solución**: Verificar que GTK Runtime esté en PATH
- **Comando**: `echo $PATH | grep -i gtk`

### **Error: "girepository not found"**
- **Solución**: Reinstalar GTK Runtime completamente
- **Verificar**: `C:\Program Files\GTK3-Runtime Win64\` existe

### **Error: "PyGObject build failed"**
- **Solución**: Usar wheels precompilados con GTK Runtime instalado
- **Alternativa**: Cambiar a Conda

### **Error en el .exe: "DLL not found"**
- **Solución**: Verificar que PyInstaller incluya las DLLs de GTK
- **Comando**: Agregar `--collect-all gi` en PyInstaller

## 📦 **Dependencias Finales para requirements.txt**

```python
# requirements.txt actualizado
PyQt6==6.6.0
PyQt6-Qt6==6.6.0
PyQt6-sip==13.6.0
pygobject==3.46.0
gst-python==1.22.0
pycairo==1.25.1
numpy==1.24.3
Pillow==10.1.0
psutil==5.9.6
colorama==0.4.6
pyinstaller==6.3.0
```

## 📚 **Referencias**

- [GTK for Windows Runtime](https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer)
- [PyGObject Windows Installation](https://pygobject.readthedocs.io/en/latest/getting_started.html#windows)
- [GStreamer Windows Installation](https://gstreamer.freedesktop.org/documentation/installing/on-windows.html)
- [PyInstaller Manual](https://pyinstaller.readthedocs.io/en/stable/)

## 💡 **Próximos Pasos**

1. **Elegir opción** (recomendado: GTK Runtime)
2. **Instalar dependencias**
3. **Probar funcionamiento**: `python main.py`
4. **Generar .exe**: `python docs/build_installer.py`
5. **Probar instalador** en sistema limpio

---

**✅ Con esta guía podrás instalar PyGObject y generar el .exe de Welltep exitosamente** 