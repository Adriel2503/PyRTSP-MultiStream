# -*- coding: utf-8 -*-
"""
Ventana principal de la aplicación PyRTSP-FastStream
Extrae la funcionalidad de SimpleStreamViewer del código original
"""

import sys
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QMessageBox, QStackedWidget
)
from PyQt6.QtCore import QTimer, Qt

from ..utils.constants import (
    APP_TITLE,
    DEFAULT_RTSP_URL,
    DEFAULT_WINDOW_SIZE,
    DEFAULT_STATS_UPDATE_INTERVAL,
    CONNECT_BUTTON_STYLE,
    DISCONNECT_BUTTON_STYLE,
    STATS_LABEL_STYLE_TEMPLATE,
    LATENCY_COLOR_EXCELLENT,
    LATENCY_COLOR_GOOD,
    LATENCY_COLOR_POOR,
    LATENCY_THRESHOLD_EXCELLENT,
    LATENCY_THRESHOLD_GOOD,
    STATUS_MESSAGES
)
from ..utils.logger import setup_logger
from .video_widget import VideoWidget
from .login_screen import LoginScreen

logger = setup_logger("MainWindow")

class MainWindow(QMainWindow):
    """Ventana principal de la aplicación con interfaz moderna"""
    
    def __init__(self):
        super().__init__()
        self.video_widget = None
        self.stats_timer = None
        self.login_screen = None
        self.stream_widget = None
        self.setup_ui()
        logger.info("MainWindow inicializada")
        
    def setup_ui(self):
        """Configurar interfaz de usuario moderna con pantallas múltiples"""
        self.setWindowTitle("🚀 Welltep RTSP Viewer - Sistema Profesional")
        self.setGeometry(100, 100, 1200, 700)
        self.setMinimumSize(800, 600)  # Tamaño mínimo, pero redimensionable
        
        # Usar QStackedWidget para cambiar entre pantallas
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        # === PANTALLA 1: LOGIN ===
        self.login_screen = LoginScreen()
        self.login_screen.connection_requested.connect(self.on_connection_requested)
        self.stacked_widget.addWidget(self.login_screen)
        
        # === PANTALLA 2: STREAM ===
        self.stream_widget = self._create_stream_widget()
        self.stacked_widget.addWidget(self.stream_widget)
        
        # Mostrar pantalla de login inicialmente
        self.stacked_widget.setCurrentWidget(self.login_screen)
        
        logger.debug("UI con pantallas múltiples configurada exitosamente")
    
    def _create_stream_widget(self):
        """Crear widget de streaming con video y controles"""
        widget = QWidget()
        widget.setObjectName("streamWidget")
        
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # === BARRA SUPERIOR CON CONTROLES ===
        top_bar = self._create_top_bar()
        
        # === PANEL DE ESTADÍSTICAS ===
        self.stats_label = self._create_stats_label()
        
        # === ÁREA DE VIDEO (EXPANDIDA) ===
        self.video_widget = VideoWidget()
        
        # Agregar componentes
        layout.addWidget(top_bar)
        layout.addWidget(self.stats_label)
        layout.addWidget(self.video_widget)
        
        # Aplicar estilo al widget de stream
        widget.setStyleSheet("""
        QWidget#streamWidget {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #1a1a1a, stop:1 #2d2d2d);
        }
        """)
        
        return widget
    
    def _create_top_bar(self):
        """Crear barra superior con información y botón desconectar"""
        bar = QWidget()
        bar.setObjectName("topBar")
        
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(20, 10, 20, 10)
        
        # Información de conexión
        self.connection_info = QLabel("🔗 Conectado")
        self.connection_info.setObjectName("connectionInfo")
        
        # Spacer
        layout.addWidget(self.connection_info)
        layout.addStretch()
        
        # Botón desconectar
        self.disconnect_btn = QPushButton("⏹️ DESCONECTAR")
        self.disconnect_btn.setObjectName("disconnectButton")
        self.disconnect_btn.clicked.connect(self.disconnect_stream)
        
        layout.addWidget(self.disconnect_btn)
        
        # Estilo para la barra superior
        bar.setStyleSheet("""
        QWidget#topBar {
            background: rgba(42, 42, 42, 200);
            border-radius: 8px;
            margin: 5px;
        }
        
        QLabel#connectionInfo {
            color: #4CAF50;
            font-size: 16px;
            font-weight: bold;
            font-family: Arial, sans-serif;
        }
        
        QPushButton#disconnectButton {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #f44336, stop:1 #d32f2f);
            color: white;
            border: none;
            border-radius: 6px;
            padding: 8px 16px;
            font-size: 14px;
            font-weight: bold;
            font-family: Arial, sans-serif;
        }
        
        QPushButton#disconnectButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #d32f2f, stop:1 #b71c1c);
        }
        """)
        
        return bar
    
    def on_connection_requested(self, ip, user, password, rtsp_url):
        """Manejar solicitud de conexión desde login screen"""
        logger.info(f"Solicitud de conexión recibida: {rtsp_url}")
        
        if self.video_widget.start_stream(rtsp_url):
            # Conexión exitosa - cambiar a pantalla de stream
            self.connection_info.setText(f"🔗 Conectado a {ip}")
            self.stacked_widget.setCurrentWidget(self.stream_widget)
            self.start_stats_monitoring()
            logger.info("Transición a pantalla de stream exitosa")
        else:
            # Error de conexión - mostrar mensaje
            QMessageBox.critical(self.login_screen, "Error de Conexión", 
                               "No se pudo conectar a la cámara IP.\n\n"
                               "Verifique:\n"
                               "• Dirección IP correcta\n"
                               "• Credenciales válidas\n"
                               "• Conexión de red\n"
                               "• Cámara accesible")
            logger.error("Error al conectar - permaneciendo en pantalla de login")
    

    
    def _create_stats_label(self):
        """Crear label de estadísticas en tiempo real"""
        stats_label = QLabel(STATUS_MESSAGES['waiting'])
        stats_label.setStyleSheet(STATS_LABEL_STYLE_TEMPLATE.format(color=LATENCY_COLOR_EXCELLENT))
        stats_label.setMaximumHeight(40)
        return stats_label
    

    
    def disconnect_stream(self):
        """Desconectar stream y volver a login"""
        self.video_widget.stop_stream()
        self.stop_stats_monitoring()
        
        # Volver a pantalla de login
        self.stacked_widget.setCurrentWidget(self.login_screen)
        logger.info("Stream desconectado - volviendo a pantalla de login")
    

    
    def start_stats_monitoring(self):
        """Iniciar monitoreo de estadísticas en tiempo real"""
        self.stats_timer = QTimer()
        self.stats_timer.timeout.connect(self.update_stats)
        self.stats_timer.start(DEFAULT_STATS_UPDATE_INTERVAL)
        logger.debug("Monitoreo de estadísticas iniciado")
    
    def stop_stats_monitoring(self):
        """Detener monitoreo de estadísticas"""
        if self.stats_timer:
            self.stats_timer.stop()
            self.stats_timer = None
        logger.debug("Monitoreo de estadísticas detenido")
    
    def update_stats(self):
        """Actualizar estadísticas en tiempo real"""
        if not self.video_widget or not self.video_widget.metrics:
            return
        
        metrics = self.video_widget.get_metrics()
        
        # Obtener todas las métricas
        fps = metrics.get_fps()
        bitrate_kbps = metrics.get_bitrate_kbps()
        bitrate_mbps = metrics.get_bitrate_mbps()
        data_rate_kbps = metrics.get_data_rate_kbps()
        latency = metrics.get_estimated_latency_ms()
        frames = metrics.frame_count
        data_mb = metrics.get_total_mb_received()
        window_info = metrics.get_window_info()
        
        # Formatear display de bitrate
        if bitrate_mbps >= 1.0:
            bitrate_display = f"{bitrate_mbps:.2f} Mbps"
        else:
            bitrate_display = f"{bitrate_kbps:.0f} Kbps"
        
        # Crear texto de estadísticas
        stats_text = (
            f"📊 FPS: {fps:.1f} | "
            f"📡 {bitrate_display} | "
            f"💾 {data_rate_kbps:.0f} KBps | "
            f"⚡ ~{latency:.0f}ms | "
            f"🎬 {frames} frames | "
            f"📦 {data_mb:.1f} MB | "
            f"🔄 {window_info['packets_in_window']}buf/5s"
        )
        
        # Determinar color según latencia
        if latency < LATENCY_THRESHOLD_EXCELLENT:
            color = LATENCY_COLOR_EXCELLENT
        elif latency < LATENCY_THRESHOLD_GOOD:
            color = LATENCY_COLOR_GOOD
        else:
            color = LATENCY_COLOR_POOR
        
        # Actualizar estilo con color dinámico
        self.stats_label.setStyleSheet(STATS_LABEL_STYLE_TEMPLATE.format(color=color))
        self.stats_label.setText(stats_text)
    
    def closeEvent(self, event):
        """Manejar cierre de aplicación"""
        if self.video_widget:
            self.video_widget.stop_stream()
        self.stop_stats_monitoring()
        logger.info("Aplicación cerrada correctamente")
        event.accept() 