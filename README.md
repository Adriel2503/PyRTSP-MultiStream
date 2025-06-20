# 📹 Visor de Cámara IP Profesional

Aplicación moderna con PyQt6 para visualizar, grabar y anotar transmisiones de cámaras IP en tiempo real.

## 🚀 Características

### 📡 **Conexión a Cámara IP**
- Conexión RTSP/HTTP a cámaras IP
- Autenticación con usuario y contraseña
- Soporte para múltiples protocolos

### 🎬 **Grabación Avanzada**
- Grabación en formato MP4
- Anotaciones integradas al video
- Overlays con timestamps precisos

### ✏️ **Sistema de Anotaciones**
- Cuadros de anotación **movibles** sobre el video
- Texto superpuesto en tiempo real
- Timeline con historial de anotaciones
- Duración automática de anotaciones

### 🎨 **Interfaz Moderna**
- Tema oscuro profesional
- Controles intuitivos
- Diseño responsive
- Iconos modernos

## 📦 Instalación

### 1. **Clonar o descargar**
```bash
# Si tienes git
git clone <tu-repositorio>
cd camara-ip-viewer

# O simplemente descarga los archivos
```

### 2. **Crear entorno virtual (recomendado)**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

### 4. **Ejecutar aplicación**
```bash
python camara_ip_viewer.py
```

## 🔧 Uso

### **1. Conectar a Cámara**
1. Ingresa la **IP de tu cámara** (ej: `192.168.1.100`)
2. Escribe **usuario** y **contraseña**
3. Clic en **🚀 CONECTAR**

### **2. Ver Transmisión**
- El video aparecerá en el panel derecho
- Usa controles de play/pause si necesario

### **3. Grabar Video**
1. Clic **🔴 INICIAR GRABACIÓN**
2. El archivo se guarda automáticamente con timestamp
3. Clic **⏹️ DETENER Y GUARDAR** para finalizar

### **4. Hacer Anotaciones**
1. Durante la transmisión, clic **📝 ANOTAR**
2. **Arrastra** el cuadro donde quieras en el video
3. **Escribe** tu observación
4. Clic **💾 Guardar** 

**¡Las anotaciones aparecen en el video grabado!**

## 📹 Formatos de Cámara Compatibles

### **URLs Comunes:**
```
RTSP: rtsp://usuario:password@IP:554/stream
HTTP: http://IP/video.cgi
ONVIF: rtsp://IP:554/onvif1
```

### **Marcas Probadas:**
- ✅ Hikvision
- ✅ Dahua  
- ✅ Axis
- ✅ Foscam
- ✅ D-Link

## 🛠️ Tecnologías

- **PyQt6** - Interfaz gráfica moderna
- **VLC Python** - Reproducción de streams
- **OpenCV** - Procesamiento de video
- **FFmpeg** - Codificación MP4
- **QDarkStyle** - Tema oscuro

## 📁 Archivos Generados

```
grabacion_20240115_143052.mp4  # Video con anotaciones
anotaciones_log.json           # Log de anotaciones
```

## ⚠️ Requisitos del Sistema

- **Python 3.8+**
- **VLC Media Player** instalado
- **Windows 10+** / **Linux** / **macOS**
- **4GB RAM** mínimo
- **Conexión de red** estable

## 🔧 Solución de Problemas

### **Error de conexión:**
- Verifica IP, usuario y contraseña
- Prueba la URL en VLC primero
- Revisa firewall/red

### **Video no aparece:**
- Instala VLC Media Player
- Verifica codec de la cámara
- Prueba diferentes URLs

### **Grabación falla:**
- Verifica espacio en disco
- Permisos de escritura
- Codec compatible

## 📞 Soporte

Si tienes problemas:
1. Revisa el archivo `requirements.txt`
2. Verifica que VLC esté instalado
3. Prueba con una cámara IP conocida

## 🎯 Próximas Funciones

- [ ] Múltiples cámaras simultáneas
- [ ] Detección de movimiento
- [ ] Alertas automáticas
- [ ] Streaming a la nube
- [ ] App móvil

---

**¡Disfruta grabando y anotando tus cámaras IP! 📹✨** 