# -*- coding: utf-8 -*-
"""
Configuraciones de baja latencia para streaming de cámaras IP
Estos parámetros están optimizados para reducir la latencia al mínimo posible
"""

# ✅ CONFIGURACIONES VLC PARA ULTRA BAJA LATENCIA
VLC_ULTRA_LOW_LATENCY_ARGS = [
    # === BUFFERS MÍNIMOS ===
    '--network-caching=0',          # Sin buffer de red
    '--live-caching=0',             # Sin cache en vivo
    '--file-caching=0',             # Sin cache de archivo
    '--sout-mux-caching=0',         # Sin cache de multiplexor
    '--disc-caching=0',             # Sin cache de disco
    '--avi-interleaved',            # Intercalado AVI
    
    # === TIMING Y SINCRONIZACIÓN ===
    '--clock-synchro=0',            # Sin sincronización de reloj
    '--clock-jitter=0',             # Sin corrección de jitter
    '--no-drop-late-frames',        # No descartar frames tardíos automáticamente
    '--avcodec-hurry-up',           # Acelerar decodificación
    
    # === PROTOCOLOS DE RED ===
    '--rtsp-tcp',                   # RTSP sobre TCP (más confiable)
    '--rtsp-frame-buffer-size=1',   # Buffer de frame mínimo
    '--no-audio',                   # Desactivar audio completamente
    
    # === DECODIFICACIÓN OPTIMIZADA ===
    '--avcodec-fast',               # Decodificación rápida
    '--avcodec-skiploopfilter=4',   # Saltar todos los filtros de bucle
    '--avcodec-skip-frame=0',       # No saltar frames
    '--avcodec-skip-idct=0',        # No saltar IDCT
    '--avcodec-threads=0',          # Auto-detectar hilos disponibles
    '--avcodec-thread-type=3',      # Hilos para frame y slice
    
    # === FILTROS DE VIDEO ===
    '--no-video-title-show',        # No mostrar título en video
    '--no-osd',                     # Sin overlay de información
    '--no-stats',                   # Sin estadísticas
    '--no-video-deco',              # Sin decoraciones de ventana
    
    # === INTERFAZ MÍNIMA ===
    '--intf=dummy',                 # Interfaz dummy
    '--extraintf=',                 # Sin interfaces extra
    '--quiet',                      # Modo silencioso
    
    # === OPTIMIZACIONES ESPECÍFICAS ===
    '--drop-late-frames',           # Descartar frames tardíos
    '--skip-frames',                # Permitir saltar frames
    '--low-delay',                  # Modo de baja latencia
    '--real-time-priority',         # Prioridad de tiempo real
]

# ✅ CONFIGURACIONES OPENCV PARA ULTRA BAJA LATENCIA
OPENCV_ULTRA_LOW_LATENCY_PROPS = {
    # === BUFFERS Y TIMEOUTS ===
    'CAP_PROP_BUFFERSIZE': 1,                    # Buffer de 1 frame solamente
    'CAP_PROP_OPEN_TIMEOUT_MSEC': 2000,          # 2s timeout para abrir
    'CAP_PROP_READ_TIMEOUT_MSEC': 500,           # 500ms timeout para leer
    
    # === FORMATOS Y CÓDECS ===
    'CAP_PROP_FOURCC': 'H264',                   # Forzar H.264
    'CAP_PROP_FPS': 30,                          # 30 FPS fijo
    'CAP_PROP_MODE': 0,                          # Modo por defecto
    
    # === CONFIGURACIONES ESPECÍFICAS DE BACKEND ===
    'backend': 'CAP_FFMPEG',                     # Usar FFmpeg backend
}

# ✅ CONFIGURACIONES FFMPEG ESPECÍFICAS PARA RTSP
FFMPEG_RTSP_OPTIONS = {
    # Protocolo de transporte
    'rtsp_transport': 'tcp',        # TCP es más confiable que UDP
    'rtsp_flags': 'prefer_tcp',     # Preferir TCP
    
    # Buffers y timeouts
    'buffer_size': 1024,            # Buffer pequeño
    'max_delay': 0,                 # Sin delay máximo
    'fflags': 'nobuffer+fastseek+flush_packets',
    
    # Análisis de stream
    'analyzeduration': 1000000,     # 1 segundo de análisis máximo
    'probesize': 1000000,           # 1MB de probe máximo
    
    # Threading
    'threads': 0,                   # Auto-detectar hilos
    'thread_type': 'frame+slice',   # Tipos de hilos
}

# ✅ COMANDOS FFMPEG PARA CASOS EXTREMOS
def get_ffmpeg_ultra_low_latency_cmd(input_url, output_file):
    """
    Generar comando FFmpeg optimizado para ultra baja latencia
    """
    return [
        'ffmpeg',
        '-y',                                    # Sobrescribir archivo de salida
        '-fflags', 'nobuffer+fastseek+flush_packets',
        '-flags', 'low_delay',
        '-strict', 'experimental',
        
        # === INPUT OPTIONS ===
        '-rtsp_transport', 'tcp',
        '-buffer_size', '1024',
        '-max_delay', '0',
        '-analyzeduration', '1000000',
        '-probesize', '1000000',
        '-i', input_url,
        
        # === OUTPUT OPTIONS ===
        '-c:v', 'libx264',                       # Códec H.264
        '-preset', 'ultrafast',                  # Preset más rápido
        '-tune', 'zerolatency',                  # Tune para latencia cero
        '-crf', '23',                            # Calidad constante
        '-g', '1',                               # Keyframe cada frame (sin GOP)
        '-keyint_min', '1',                      # Intervalo mínimo de keyframes
        '-sc_threshold', '0',                    # Sin detección de cambio de escena
        '-bf', '0',                              # Sin B-frames
        '-refs', '1',                            # 1 frame de referencia
        '-me_method', 'dia',                     # Método de estimación de movimiento rápido
        '-subq', '1',                            # Calidad de submuestreo mínima
        '-trellis', '0',                         # Sin trellis
        '-aq-mode', '0',                         # Sin quantización adaptativa
        '-x264opts', 'nal-hrd=cbr:force-cfr=1:no-mbtree:sliced-threads:sync-lookahead=0',
        
        # === FILTROS ===
        '-avoid_negative_ts', 'make_zero',
        '-fflags', '+genpts',
        
        output_file
    ]

# ✅ FUNCIONES DE UTILIDAD
def apply_opencv_ultra_low_latency(cap):
    """
    Aplicar todas las configuraciones de ultra baja latencia a un objeto VideoCapture
    """
    import cv2
    
    for prop_name, value in OPENCV_ULTRA_LOW_LATENCY_PROPS.items():
        if prop_name == 'backend':
            continue
        
        # Convertir string a constante de OpenCV
        if isinstance(prop_name, str) and hasattr(cv2, prop_name):
            prop_const = getattr(cv2, prop_name)
            if prop_name == 'CAP_PROP_FOURCC' and isinstance(value, str):
                value = cv2.VideoWriter_fourcc(*value)
            cap.set(prop_const, value)
    
    return cap

def get_vlc_minimal_latency_args():
    """
    Obtener argumentos VLC para latencia absolutamente mínima
    Advertencia: Puede causar inestabilidad en algunos sistemas
    """
    return VLC_ULTRA_LOW_LATENCY_ARGS

# ✅ CONFIGURACIONES POR TIPO DE CÁMARA
CAMERA_SPECIFIC_CONFIGS = {
    'hikvision': {
        'vlc_extra_args': ['--rtsp-caching=0'],
        'opencv_props': {'CAP_PROP_BUFFERSIZE': 1},
        'url_suffix': '?tcp'
    },
    'dahua': {
        'vlc_extra_args': ['--network-caching=50'],
        'opencv_props': {'CAP_PROP_BUFFERSIZE': 1},
        'url_suffix': '&tcp=1'
    },
    'axis': {
        'vlc_extra_args': ['--rtsp-tcp', '--network-caching=0'],
        'opencv_props': {'CAP_PROP_BUFFERSIZE': 1},
        'url_suffix': '?tcp=1&buffer=0'
    },
    'generic': {
        'vlc_extra_args': VLC_ULTRA_LOW_LATENCY_ARGS,
        'opencv_props': OPENCV_ULTRA_LOW_LATENCY_PROPS,
        'url_suffix': ''
    }
}

def get_optimized_config(camera_brand='generic'):
    """
    Obtener configuración optimizada según la marca de cámara
    """
    return CAMERA_SPECIFIC_CONFIGS.get(camera_brand.lower(), CAMERA_SPECIFIC_CONFIGS['generic'])

# ✅ MONITOREO DE LATENCIA
class LatencyMonitor:
    """
    Monitor simple de latencia en tiempo real
    """
    def __init__(self, window_size=30):
        self.times = []
        self.window_size = window_size
    
    def add_frame_time(self, frame_time):
        """Agregar tiempo de procesamiento de frame"""
        self.times.append(frame_time)
        if len(self.times) > self.window_size:
            self.times.pop(0)
    
    def get_average_latency_ms(self):
        """Obtener latencia promedio en milisegundos"""
        if not self.times:
            return 0
        return sum(self.times) * 1000 / len(self.times)
    
    def get_max_latency_ms(self):
        """Obtener latencia máxima en milisegundos"""
        if not self.times:
            return 0
        return max(self.times) * 1000
    
    def reset(self):
        """Resetear estadísticas"""
        self.times.clear() 