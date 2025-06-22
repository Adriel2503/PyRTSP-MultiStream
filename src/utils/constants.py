# -*- coding: utf-8 -*-
"""
Constantes globales del proyecto PyRTSP-FastStream
"""

# === CONFIGURACIÓN DE APLICACIÓN ===
APP_NAME = "PyRTSP-FastStream"
APP_VERSION = "1.0.0"
APP_TITLE = "🚀 Cámara IP - GStreamer + PyQt6 (D3D11 Overlay)"

# === CONFIGURACIÓN DE GSTREAMER ===
DEFAULT_RTSP_URL = "rtsp://admin:Prototipo@192.168.18.5:554/Streaming/Channels/101"

# Pipeline GStreamer optimizado
GSTREAMER_PIPELINE_TEMPLATE = """
rtspsrc location={url} protocols=tcp latency=0 name=rtspsrc
! rtph264depay name=depay
! avdec_h264 name=decoder
! videoconvert name=convert
! d3d11videosink name=videosink
"""

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