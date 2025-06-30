# -*- coding: utf-8 -*-
"""
Constantes globales del proyecto PyRTSP-FastStream
"""

# === CONFIGURACIÓN DE APLICACIÓN ===
APP_NAME = "IRIS - WELLTEP"
APP_VERSION = "1.0.0"
APP_TITLE = "IRIS PIPE INSPECTION SOFTWARE"

# === CONFIGURACIÓN DE GSTREAMER ===
DEFAULT_RTSP_URL = "rtsp://admin:Prototipo@192.168.18.5:554/Streaming/Channels/101"

# Pipeline GStreamer optimizado CON OVERLAYS NATIVOS (7 overlays: malla + 5 textos + anotaciones)
GSTREAMER_PIPELINE_TEMPLATE = """
rtspsrc location={url} protocols=tcp latency=0 name=rtspsrc
! rtph264depay name=depay
! avdec_h264 name=decoder
! videoconvert name=convert
! cairooverlay name=cairo_grid
! cairooverlay name=cairo_datetime
! cairooverlay name=cairo_ref_tramo
! cairooverlay name=cairo_pozo_inicio
! cairooverlay name=cairo_distancia
! cairooverlay name=cairo_pozo_fin
! cairooverlay name=cairo_annotation
! tee name=t
t. ! queue ! d3d12videosink name=videosink
t. ! queue ! videoconvert ! video/x-raw,format=RGB ! appsink name=recording_sink emit-signals=true sync=false
"""

# === CONFIGURACIÓN DE OVERLAYS NATIVOS ===

# Configuración para MALLA/GRILLA (se dibuja primero, debajo de los textos)
CAIRO_GRID_CONFIG = {
    'enabled': True,                         # Habilitar/deshabilitar malla
    'line_color': (1.0, 1.0, 1.0, 0.8),    # Blanco semi-transparente RGBA
    'line_width': 1,                         # Grosor de líneas en píxeles
    'grid_spacing_x': 400,                    # Espaciado horizontal entre líneas (80px)
    'grid_spacing_y': 200,                    # Espaciado vertical entre líneas (60px)
    'start_offset_x': 150,                    # Offset inicial horizontal (40px desde borde)
    'start_offset_y': 40,                    # Offset inicial vertical (30px desde borde)
    'changeable_color': True                 # Permitir cambio de color en el futuro
}

# El cairooverlay se configurará programáticamente para el fondo naranja transparente
CAIRO_OVERLAY_CONFIG = {
    'datetime_format': '%Y/%m/%d %H:%M:%S',  # Formato de fecha/hora
    'font_family': 'Arial',
    'font_size': 32,                         # Aumentado de 24 a 32 (MUY GRANDE)
    'font_weight': 'bold',
    'text_color': (1.0, 1.0, 1.0, 1.0),     # Blanco RGBA
    'bg_color': (1.0, 0.65, 0.15, 0.2),     # Naranja MÁS transparente con alpha 0.2
    'padding': 25,                           # Aumentado de 20 a 25 (más espacio)
    'border_radius': 15,                     # Aumentado de 12 a 15 (más redondeado)
    'position': 'top-left'
}

# Configuración para REF. TRAMO (esquina superior derecha)
CAIRO_REF_TRAMO_CONFIG = {
    'font_family': 'Arial',
    'font_size': 32,                         # Mismo tamaño que fecha/hora
    'font_weight': 'bold',
    'text_color': (1.0, 1.0, 1.0, 1.0),     # Blanco RGBA
    'bg_color': (1.0, 0.65, 0.15, 0.2),     # Mismo naranja transparente
    'padding': 25,                           # Mismo padding
    'border_radius': 15,                     # Mismas esquinas redondeadas
    'position': 'top-right',
    'text': ''                               # Texto inicial vacío
}

# Configuración para POZO INICIO (esquina inferior izquierda)
CAIRO_POZO_INICIO_CONFIG = {
    'font_family': 'Arial',
    'font_size': 32,                         # Mismo tamaño que otros overlays
    'font_weight': 'bold',
    'text_color': (1.0, 1.0, 1.0, 1.0),     # Blanco RGBA
    'bg_color': (1.0, 0.65, 0.15, 0.2),     # Mismo naranja transparente
    'padding': 25,                           # Mismo padding
    'border_radius': 15,                     # Mismas esquinas redondeadas
    'position': 'bottom-left',
    'text': ''                               # Texto inicial vacío
}

# Configuración para POZO FIN (esquina inferior derecha)
CAIRO_POZO_FIN_CONFIG = {
    'font_family': 'Arial',
    'font_size': 32,                         # Mismo tamaño que otros overlays
    'font_weight': 'bold',
    'text_color': (1.0, 1.0, 1.0, 1.0),     # Blanco RGBA
    'bg_color': (1.0, 0.65, 0.15, 0.2),     # Mismo naranja transparente
    'padding': 25,                           # Mismo padding
    'border_radius': 15,                     # Mismas esquinas redondeadas
    'position': 'bottom-right',
    'text': ''                               # Texto inicial vacío
}

# Configuración para DISTANCIA (lado derecho inferior, encima de POZO FIN)
CAIRO_DISTANCIA_CONFIG = {
    'font_family': 'Arial',
    'font_size': 32,                         # Mismo tamaño que otros overlays
    'font_weight': 'bold',
    'text_color': (1.0, 1.0, 1.0, 1.0),     # Blanco RGBA
    'bg_color': (1.0, 0.65, 0.15, 0.2),     # Mismo naranja transparente
    'padding': 25,                           # Mismo padding
    'border_radius': 15,                     # Mismas esquinas redondeadas
    'position': 'bottom-right-above',        # Encima de POZO FIN
    'text': '0.0 m',                         # Texto inicial por defecto
    'vertical_offset': 120                   # Separación aumentada del overlay de POZO FIN
}

# Configuración simplificada para timestamp (respaldo si cairo no funciona)
TIMEOVERLAY_CONFIG = {
    'halignment': 'left',        # Alineación horizontal: left, center, right
    'valignment': 'top',         # Alineación vertical: top, center, bottom  
    'time-format': '%Y/%m/%d %H:%M:%S',  # Formato: año/mes/día hora:minuto:segundo
    'font-desc': 'Arial Bold 16',        # Fuente y tamaño
    'color': 0xFFFFFFFF,                 # Color blanco (ARGB)
    'outline-color': 0xFFA726FF,         # Contorno naranja (#FFA726)
    'xpad': 15,                          # Padding horizontal aumentado
    'ypad': 12,                          # Padding vertical aumentado  
    'draw-shadow': True,                 # Sombra para mejor visibilidad
    'draw-outline': True,                # Contorno para mejor contraste
    'shaded-background': True,           # Fondo sombreado
    'auto-resize': True                  # Redimensionar automáticamente
}



# === CONFIGURACIÓN DE MÉTRICAS ===
DEFAULT_METRICS_WINDOW_SECONDS = 5  # Ventana deslizante de 5 segundos
DEFAULT_STATS_UPDATE_INTERVAL = 1000  # Actualizar estadísticas cada 1 segundo
MAX_FPS_THEORETICAL = 120  # FPS máximo teórico para filtrado
MAX_FRAME_INTERVALS_HISTORY = 30  # Máximo de intervalos de frame guardados

# === CONFIGURACIÓN DE UI ===
DEFAULT_WINDOW_SIZE = (1200, 800)
DEFAULT_VIDEO_SIZE = (800, 600)

# === CONFIGURACIÓN DE VIDEO ===
# Para video original de 2560x1440
FULL_HD_VIDEO_SIZE = (2560, 1440)
HALF_HD_VIDEO_SIZE = (1280, 720)    # Submúltiplo ÷2 - sin bandas negras
QUARTER_HD_VIDEO_SIZE = (640, 360)  # Submúltiplo ÷4 - muy compacto

# Opciones de resolución
VIDEO_SCALE_OPTIONS = {
    'full': FULL_HD_VIDEO_SIZE,      # 2560x1440 - Resolución completa
    'half': HALF_HD_VIDEO_SIZE,      # 1280x720  - Mitad, sin bandas negras  
    'quarter': QUARTER_HD_VIDEO_SIZE, # 640x360   - Cuarto, muy compacto
    'auto': DEFAULT_VIDEO_SIZE       # 800x600   - Escalado automático
}

# Cambiar aquí para diferentes tamaños
PREFERRED_VIDEO_SCALE = 'half'  # 'full', 'half', 'quarter', 'auto'

# Estilos CSS
STATS_LABEL_STYLE_TEMPLATE = """
QLabel {{
    background: #2c3e50; color: {color}; padding: 8px;
    border-radius: 4px; font-family: 'Courier New', monospace;
    font-size: 11px; font-weight: bold;
}}
"""

CONNECT_BUTTON_STYLE = """
QPushButton {
    background: #4CAF50; color: white; padding: 8px 16px;
    border-radius: 4px; font-weight: bold;
}
QPushButton:hover { background: #45a049; }
"""

DISCONNECT_BUTTON_STYLE = """
QPushButton {
    background: #f44336; color: white; padding: 8px 16px;
    border-radius: 4px; font-weight: bold;
}
QPushButton:hover { background: #da190b; }
"""

VIDEO_WIDGET_STYLE = """
QFrame {
    background-color: black;
    border: 2px solid #4CAF50;
}
"""

# === COLORES PARA LATENCIA ===
LATENCY_COLOR_EXCELLENT = "#27ae60"  # Verde - < 100ms
LATENCY_COLOR_GOOD = "#f39c12"       # Naranja - 100-200ms  
LATENCY_COLOR_POOR = "#e74c3c"       # Rojo - > 200ms

# === UMBRALES DE RENDIMIENTO ===
LATENCY_THRESHOLD_EXCELLENT = 100  # ms
LATENCY_THRESHOLD_GOOD = 200        # ms

# === CONFIGURACIÓN DE RED ===
NETWORK_OVERHEAD_ESTIMATE = 30  # ms de overhead de red estimado

# === CONFIGURACIÓN DE DEBUG ===
DEBUG_SHOW_FIRST_BUFFERS = 5  # Mostrar primeros N buffers para debug
DEBUG_BUFFER_INFO = True       # Mostrar información de buffers

# === MENSAJES DE ESTADO ===
STATUS_MESSAGES = {
    'waiting': "📊 Esperando conexión...",
    'connecting': "🚀 Conectando...",
    'connected': "✅ Conectado - streaming activo",
    'disconnected': "📊 Desconectado",
    'error': "❌ Error de conexión"
}

# === CONFIGURACIÓN DE LOGGING ===
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_LEVEL = "INFO"  # Nivel normal de logging

# === CONFIGURACIÓN INICIAL DE ELEMENTOS OVERLAY ===
# ✅ FUENTE ÚNICA DE VERDAD para configuración de elementos
DEFAULT_OVERLAY_ELEMENTS = {
    'grid_enabled': True,              # ✅ Cuadrículas habilitadas
    'fecha_enabled': True,             # ✅ Fecha y hora habilitada  
    'tramo_enabled': False,            # ❌ Referencia tramo deshabilitada
    'pozo_inicial_enabled': False,     # ❌ Pozo desde deshabilitado
    'distancia_enabled': True,         # ✅ Distancia habilitada
    'pozo_final_enabled': False        # ❌ Pozo hasta deshabilitado
}

# Elementos que requieren formulario de inspección para ser habilitados
FORM_DEPENDENT_ELEMENTS = {
    'tramo_enabled',
    'pozo_inicial_enabled', 
    'pozo_final_enabled'
}

# Configuración cuando se llena el formulario - activa elementos dependientes
FORM_FILLED_OVERLAY_ELEMENTS = {
    'grid_enabled': True,              # ✅ Cuadrículas habilitadas
    'fecha_enabled': True,             # ✅ Fecha y hora habilitada  
    'tramo_enabled': True,             # ✅ Referencia tramo habilitada
    'pozo_inicial_enabled': True,      # ✅ Pozo desde habilitado
    'distancia_enabled': True,         # ✅ Distancia habilitada
    'pozo_final_enabled': True         # ✅ Pozo hasta habilitado
}

# Mapeo de elementos UI con sus configuraciones
OVERLAY_ELEMENTS_UI_CONFIG = [
    ("Fecha y Hora", "fecha_enabled"),
    ("Referencia Tramo", "tramo_enabled"), 
    ("Pozo Desde", "pozo_inicial_enabled"),
    ("Pozo Hasta", "pozo_final_enabled"),
    ("Cuadrículas", "grid_enabled"),
    ("Distancia", "distancia_enabled")
] 