# 🚀 PyRTSP-FastStream - Estructura del Proyecto

**Sistema Profesional de Streaming RTSP de Ultra Baja Latencia**

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![PyQt6](https://img.shields.io/badge/PyQt6-6.6+-green.svg)
![GStreamer](https://img.shields.io/badge/GStreamer-1.0+-red.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

---

## 📁 Estructura del Proyecto

```
PyRTSP-FastStream/
│
├── 📁 src/                          # Código fuente principal
│   ├── 📁 core/                     # Núcleo de la aplicación
│   │   ├── __init__.py              # Inicialización del módulo
│   │   ├── application.py           # Clase principal de la aplicación
│   │   ├── config_manager.py        # Gestión de configuraciones
│   │   └── exceptions.py            # Excepciones personalizadas
│   │
│   ├── 📁 ui/                       # Interfaz de usuario
│   │   ├── __init__.py              # Inicialización del módulo UI
│   │   ├── main_window.py           # Ventana principal (SimpleStreamViewer)
│   │   ├── video_widget.py          # Widget de video (SimpleGStreamerWidget)
│   │   ├── controls_panel.py        # Panel de controles de stream
│   │   ├── stats_panel.py           # Panel de estadísticas en tiempo real
│   │   ├── dialogs/                 # Diálogos y ventanas modales
│   │   │   ├── __init__.py
│   │   │   ├── connection_dialog.py # Diálogo de configuración de conexión
│   │   │   └── settings_dialog.py   # Diálogo de configuraciones
│   │   └── styles/                  # Estilos CSS/QSS
│   │       ├── __init__.py
│   │       ├── dark_theme.qss       # Tema oscuro (actual)
│   │       └── light_theme.qss      # Tema claro
│   │
│   ├── 📁 streaming/                # Backends de streaming
│   │   ├── __init__.py              # Inicialización del módulo streaming
│   │   ├── base_backend.py          # Clase base abstracta para backends
│   │   ├── gstreamer_backend.py     # Backend GStreamer (ultra baja latencia)
│   │   ├── vlc_backend.py           # Backend VLC (compatibilidad)
│   │   ├── ffmpeg_backend.py        # Backend FFmpeg (balance)
│   │   └── stream_manager.py        # Gestor de streams y backends
│   │
│   ├── 📁 metrics/                  # Sistema de métricas y análisis
│   │   ├── __init__.py              # Inicialización del módulo metrics
│   │   ├── stream_metrics.py        # Métricas de stream (StreamMetrics)
│   │   ├── performance_monitor.py   # Monitor de rendimiento del sistema
│   │   ├── latency_analyzer.py      # Análisis avanzado de latencia
│   │   └── data_collector.py        # Recolector y exportador de datos
│   │
│   ├── 📁 recording/                # Sistema de grabación y anotaciones
│   │   ├── __init__.py              # Inicialización del módulo recording
│   │   ├── video_recorder.py        # Grabación de video con overlays
│   │   ├── annotations.py           # Sistema de anotaciones movibles
│   │   └── export_manager.py        # Exportación de grabaciones
│   │
│   ├── 📁 network/                  # Utilidades de red y conexión
│   │   ├── __init__.py              # Inicialización del módulo network
│   │   ├── rtsp_client.py           # Cliente RTSP optimizado
│   │   ├── connection_tester.py     # Pruebas automáticas de conexión
│   │   └── network_analyzer.py      # Análisis de red y latencia
│   │
│   └── 📁 utils/                    # Utilidades generales
│       ├── __init__.py              # Inicialización del módulo utils
│       ├── logger.py                # Sistema de logging avanzado
│       ├── constants.py             # Constantes globales del proyecto
│       ├── helpers.py               # Funciones auxiliares y utilidades
│       └── validators.py            # Validadores de datos y URLs
│
├── 📁 config/                       # Archivos de configuración
│   ├── __init__.py                  # Configuraciones como módulo Python
│   ├── default_settings.json        # Configuración por defecto
│   ├── camera_profiles.json         # Perfiles para diferentes cámaras
│   └── user_settings.json           # Configuración personalizada del usuario
│
├── 📁 assets/                       # Recursos estáticos
│   ├── 📁 icons/                    # Iconos de la aplicación
│   │   ├── app_icon.png             # Icono principal de la aplicación
│   │   ├── play.svg                 # Icono de reproducir
│   │   ├── stop.svg                 # Icono de detener
│   │   └── settings.svg             # Icono de configuraciones
│   ├── 📁 images/                   # Imágenes y gráficos
│   │   └── logo.png                 # Logo del proyecto
│   └── 📁 fonts/                    # Fuentes personalizadas
│       └── roboto.ttf               # Fuente Roboto para UI
│
├── 📁 docs/                         # Documentación del proyecto
│   ├── README.md                    # Documentación principal
│   ├── INSTALLATION.md              # Guía de instalación
│   ├── API_REFERENCE.md             # Referencia de API
│   ├── CONTRIBUTING.md              # Guía para contribuidores
│   ├── README_OVERLAY_POSITIONING.md    # Sistema de coordenadas de overlays
│   ├── README_OVERLAY_QUICK_REFERENCE.md # Guía rápida de overlays
│   ├── README_ESTRUCTURA.md         # Estructura del proyecto (este archivo)
│   └── 📁 images/                   # Imágenes para documentación
│       ├── architecture.png         # Diagrama de arquitectura
│       └── screenshots/             # Capturas de pantalla
│
├── 📁 tests/                        # Suite de pruebas
│   ├── __init__.py                  # Inicialización del módulo tests
│   ├── 📁 unit/                     # Pruebas unitarias
│   │   ├── test_metrics.py          # Pruebas para sistema de métricas
│   │   ├── test_streaming.py        # Pruebas para backends de streaming
│   │   └── test_ui.py               # Pruebas para componentes UI
│   ├── 📁 integration/              # Pruebas de integración
│   │   ├── test_full_pipeline.py    # Pruebas end-to-end
│   │   └── test_camera_connection.py# Pruebas con cámaras reales
│   └── 📁 fixtures/                 # Datos de prueba
│       └── sample_streams.json      # URLs de streams de prueba
│
├── 📁 scripts/                      # Scripts de utilidad y automatización
│   ├── install_dependencies.py     # Instalador automático de dependencias
│   ├── build_release.py            # Script para crear releases
│   └── performance_benchmark.py    # Benchmark de rendimiento
│
├── 📁 examples/                     # Ejemplos de uso del proyecto
│   ├── basic_usage.py               # Uso básico de la biblioteca
│   ├── custom_backend.py           # Implementar backend personalizado
│   └── metrics_only.py             # Usar solo el sistema de métricas
│
├── 📄 main.py                       # Punto de entrada principal
├── 📄 requirements.txt              # Dependencias de producción
├── 📄 requirements-dev.txt          # Dependencias de desarrollo
├── 📄 setup.py                      # Configuración de instalación (legacy)
├── 📄 pyproject.toml               # Configuración moderna de Python
├── 📄 .gitignore                   # Archivos ignorados por Git
├── 📄 .env.example                 # Variables de entorno de ejemplo
├── 📄 LICENSE                      # Licencia del proyecto (MIT)
└── 📄 CHANGELOG.md                 # Registro de cambios y versiones
```

---

## 🎯 Descripción de Módulos

### 📦 **src/core/** - Núcleo de la Aplicación
**Responsabilidad**: Gestión central de la aplicación, configuraciones y excepciones.

- `application.py`: Clase principal que coordina todos los módulos
- `config_manager.py`: Carga, guarda y gestiona todas las configuraciones
- `exceptions.py`: Excepciones personalizadas para manejo de errores

### 🖥️ **src/ui/** - Interfaz de Usuario
**Responsabilidad**: Toda la interfaz gráfica basada en PyQt6.

- `main_window.py`: Ventana principal que contiene todos los componentes
- `video_widget.py`: Widget especializado para mostrar video con overlays
- `controls_panel.py`: Controles de conexión, grabación y configuración
- `stats_panel.py`: Panel de estadísticas en tiempo real
- `dialogs/`: Ventanas modales para configuración y ajustes
- `styles/`: Hojas de estilo QSS para temas visuales

### 📡 **src/streaming/** - Backends de Streaming
**Responsabilidad**: Diferentes implementaciones para streaming de video.

- `base_backend.py`: Interfaz común para todos los backends
- `gstreamer_backend.py`: Implementación GStreamer (50-100ms latencia)
- `vlc_backend.py`: Implementación VLC (200-500ms latencia)
- `ffmpeg_backend.py`: Implementación FFmpeg (80-150ms latencia)
- `stream_manager.py`: Gestiona y cambia entre backends dinámicamente

### 📊 **src/metrics/** - Sistema de Métricas
**Responsabilidad**: Análisis de rendimiento y métricas en tiempo real.

- `stream_metrics.py`: Métricas básicas de stream (FPS, bitrate, latencia)
- `performance_monitor.py`: Monitor del rendimiento del sistema
- `latency_analyzer.py`: Análisis avanzado de latencia y jitter
- `data_collector.py`: Recolección y exportación de datos históricos

### 🎬 **src/recording/** - Grabación y Anotaciones
**Responsabilidad**: Grabación de video con overlays y sistema de anotaciones.

- `video_recorder.py`: Grabación de video con metadatos
- `annotations.py`: Sistema de anotaciones movibles y editables
- `export_manager.py`: Exportación en diferentes formatos

### 🌐 **src/network/** - Utilidades de Red
**Responsabilidad**: Manejo de conexiones de red y análisis.

- `rtsp_client.py`: Cliente RTSP optimizado para baja latencia
- `connection_tester.py`: Pruebas automáticas de conectividad
- `network_analyzer.py`: Análisis de red, pérdida de paquetes, jitter

### 🔧 **src/utils/** - Utilidades Generales
**Responsabilidad**: Funciones auxiliares y utilidades compartidas.

- `logger.py`: Sistema de logging con diferentes niveles
- `constants.py`: Constantes del proyecto (URLs, configuraciones)
- `helpers.py`: Funciones auxiliares reutilizables
- `validators.py`: Validación de URLs, configuraciones, etc.

---

## 🚀 Ventajas de Esta Arquitectura

### ✅ **Modularidad**
- Cada módulo tiene una responsabilidad específica
- Fácil mantenimiento y extensión
- Componentes intercambiables

### ✅ **Escalabilidad**
- Fácil agregar nuevos backends de streaming
- Sistema de plugins para extensiones
- Arquitectura preparada para crecimiento

### ✅ **Testabilidad**
- Cada módulo puede probarse independientemente
- Mocks y fixtures organizados
- Cobertura de pruebas granular

### ✅ **Profesionalidad**
- Sigue estándares de Python (PEP 8, PEP 20)
- Documentación integrada
- Preparado para CI/CD

---

## 📋 Próximos Pasos de Implementación

### 🎯 **Fase 1: Estructura Base**
1. Crear estructura de carpetas
2. Migrar código actual a módulos correspondientes
3. Configurar `__init__.py` en cada módulo

### 🎯 **Fase 2: Separación de Responsabilidades**
1. Extraer `StreamMetrics` → `src/metrics/stream_metrics.py`
2. Extraer `SimpleGStreamerWidget` → `src/ui/video_widget.py`
3. Extraer `SimpleStreamViewer` → `src/ui/main_window.py`

### 🎯 **Fase 3: Abstracción de Backends**
1. Crear `BaseBackend` abstracto
2. Implementar `GStreamerBackend`
3. Agregar `VLCBackend` y `FFmpegBackend`

### 🎯 **Fase 4: Sistema de Configuración**
1. Implementar `ConfigManager`
2. Crear archivos JSON de configuración
3. Sistema de perfiles de cámara

### 🎯 **Fase 5: Testing y Documentación**
1. Crear suite de pruebas unitarias
2. Documentar APIs públicas
3. Ejemplos de uso

---

## 🛠️ Tecnologías Utilizadas

- **🐍 Python 3.8+**: Lenguaje principal
- **🖥️ PyQt6**: Interfaz gráfica moderna
- **📺 GStreamer**: Backend de ultra baja latencia
- **🎬 VLC**: Backend de compatibilidad universal
- **⚡ FFmpeg**: Backend de balance perfecto
- **📊 Métricas**: Sistema de análisis en tiempo real
- **🎯 RTSP/TCP**: Protocolo optimizado para streaming

---

## 📐 Documentación de Overlays

El sistema de overlays de IRIS - WELLTEP cuenta con documentación especializada:

### 📚 **Documentos Disponibles**

1. **[README_OVERLAY_POSITIONING.md](README_OVERLAY_POSITIONING.md)**
   - 📐 Sistema de coordenadas completo
   - 🎯 Posicionamiento en frame 2560x1440
   - 🔧 Guía de configuración y personalización
   - 🏗️ Arquitectura de renderers Cairo
   - 🛠️ Ejemplos de implementación

2. **[README_OVERLAY_QUICK_REFERENCE.md](README_OVERLAY_QUICK_REFERENCE.md)**
   - 🚀 Guía rápida de referencia
   - 📊 Tabla de coordenadas
   - ⚡ Comandos de modificación rápida
   - 🐛 Solución de problemas comunes

### 🎨 **Sistema de Overlays**

El sistema utiliza **coordenadas fijas** en el frame original de 2560x1440:

```python
# Coordenadas base
DISTANCIA_FIJA_BORDE_X = 150px  # Margen horizontal
DISTANCIA_FIJA_BORDE_Y = 50px   # Margen vertical

# Overlays principales
FECHA/HORA:    (150px, 50px)    # Superior izquierda
REF. TRAMO:    (2410px, 50px)   # Superior derecha
POZO INICIO:   (150px, 1340px)  # Inferior izquierda
POZO FIN:      (2410px, 1340px) # Inferior derecha
```

### 🔧 **Archivos de Overlays**

```
src/ui/video/cairo/
├── datetime_renderer.py     # Fecha/hora
├── tramo_renderer.py       # REF. Tramo  
├── pozos_renderer.py       # Pozos + Distancia
├── grid_renderer.py        # Cuadrícula
└── annotation_renderer.py  # Anotaciones
```

---

## 📞 Próximos Pasos

Una vez que confirmes hasta qué punto implementar esta estructura, procederemos a:

1. **Crear la estructura de carpetas**
2. **Migrar el código actual**
3. **Implementar las abstracciones necesarias**
4. **Configurar el sistema de imports**
5. **Crear el punto de entrada principal**

¿Hasta qué fase quieres que implementemos inicialmente? 