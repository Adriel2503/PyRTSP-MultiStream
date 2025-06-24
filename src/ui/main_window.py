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
from PyQt6.QtGui import QKeySequence, QShortcut

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
from .inspection_form_dialog import InspectionFormDialog

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
        
        # Agregar atajo de teclado para desconectar (Escape)
        self.disconnect_shortcut = QShortcut(QKeySequence("Escape"), self)
        self.disconnect_shortcut.activated.connect(self.disconnect_stream)
        
        logger.debug("UI con pantallas múltiples configurada exitosamente")
    
    def _create_stream_widget(self):
        """Crear widget de streaming con video y controles"""
        widget = QWidget()
        widget.setObjectName("streamWidget")
        
        main_layout = QVBoxLayout(widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # === PANEL DE ESTADÍSTICAS ===
        self.stats_label = self._create_stats_label()
        main_layout.addWidget(self.stats_label)
        
        # === ÁREA PRINCIPAL: VIDEO + BOTÓN ===
        content_layout = QHBoxLayout()
        content_layout.setSpacing(15)
        
        # === ÁREA DE VIDEO (TAMAÑO FIJO) ===
        self.video_widget = VideoWidget()
        # Conectar señal del botón "+" del video widget
        self.video_widget.plus_button_clicked.connect(self.on_plus_button_clicked)
        content_layout.addWidget(self.video_widget)
        
        # === PANEL LATERAL DERECHO ===
        right_panel = self._create_right_panel()
        content_layout.addWidget(right_panel)
        
        # Agregar el layout de contenido al layout principal
        main_layout.addLayout(content_layout)
        
        # Aplicar estilo al widget de stream
        widget.setStyleSheet("""
        QWidget#streamWidget {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #1a1a1a, stop:1 #2d2d2d);
        }
        """)
        
        return widget
    
    def _create_right_panel(self):
        """Crear panel lateral derecho con botón '+' y otros controles"""
        panel = QWidget()
        panel.setObjectName("rightPanel")
        panel.setMinimumWidth(200)
        panel.setMaximumWidth(300)
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # === BOTÓN '+' PRINCIPAL ===
        self.plus_button = QPushButton("+")
        self.plus_button.setObjectName("plusButton")
        self.plus_button.setMinimumSize(70, 70)
        self.plus_button.setMaximumSize(70, 70)
        self.plus_button.clicked.connect(self.on_plus_button_clicked)
        
        # Estilo del botón '+'
        self.plus_button.setStyleSheet("""
        QPushButton#plusButton {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(255, 183, 77, 220), 
                stop:1 rgba(255, 167, 38, 220));
            color: white;
            border: 3px solid rgba(255, 255, 255, 120);
            border-radius: 35px;
            font-size: 32px;
            font-weight: bold;
            font-family: Arial, sans-serif;
        }
        QPushButton#plusButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(255, 167, 38, 250), 
                stop:1 rgba(255, 152, 0, 250));
            border: 3px solid rgba(255, 255, 255, 180);
            transform: scale(1.05);
        }
        QPushButton#plusButton:pressed {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(255, 152, 0, 200), 
                stop:1 rgba(245, 124, 0, 200));
            border: 3px solid rgba(255, 255, 255, 220);
        }
        """)
        
        # === TÍTULO DEL PANEL ===
        title_label = QLabel("CONTROLES")
        title_label.setObjectName("rightPanelTitle")
        title_label.setStyleSheet("""
        QLabel#rightPanelTitle {
            color: rgba(255, 167, 38, 255);
            font-size: 14px;
            font-weight: bold;
            font-family: Arial, sans-serif;
            padding: 5px;
            text-align: center;
        }
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # === DESCRIPCIÓN DEL BOTÓN (REMOVIDA) ===
        # desc_label removido según solicitud del usuario
        
        # === BOTONES DE CONTROL (PAUSAR, FOTO Y DETENER) ===
        control_buttons_layout = QHBoxLayout()
        control_buttons_layout.setSpacing(10)
        
        # Botón PAUSAR
        self.pause_button = QPushButton("⏸️")
        self.pause_button.setObjectName("pauseButton")
        self.pause_button.setMinimumSize(45, 45)
        self.pause_button.setMaximumSize(45, 45)
        self.pause_button.clicked.connect(self.on_pause_clicked)
        
        # Botón CAPTURA FOTO (estilo móvil circular)

        
        # Botón CAPTURA (aro + círculo blanco)
        self.capture_button = QPushButton("")
        self.capture_button.setObjectName("captureButton")
        self.capture_button.setMinimumSize(50, 50)  # Más grande que pausar/detener
        self.capture_button.setMaximumSize(50, 50)
        self.capture_button.setToolTip("Capturar foto")
        self.capture_button.clicked.connect(self.on_capture_clicked)
        
        # Botón DETENER
        self.stop_button = QPushButton("⏹️")
        self.stop_button.setObjectName("stopButton")
        self.stop_button.setMinimumSize(45, 45)
        self.stop_button.setMaximumSize(45, 45)
        self.stop_button.clicked.connect(self.on_stop_clicked)
        
        # Estilos para los botones de control
        control_button_style = """
        QPushButton {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(70, 70, 70, 220), 
                stop:1 rgba(50, 50, 50, 220));
            color: white;
            border: 2px solid rgba(255, 255, 255, 80);
            border-radius: 22px;
            font-size: 16px;
            font-weight: bold;
        }
        QPushButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(90, 90, 90, 250), 
                stop:1 rgba(70, 70, 70, 250));
            border: 2px solid rgba(255, 255, 255, 120);
        }
        QPushButton:pressed {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(40, 40, 40, 200), 
                stop:1 rgba(20, 20, 20, 200));
            border: 2px solid rgba(255, 255, 255, 160);
        }
        """
        
        self.pause_button.setStyleSheet(control_button_style)
        self.stop_button.setStyleSheet(control_button_style)
        
        # Estilo para botón de captura (círculo blanco con efectos premium)
        capture_button_style = """
        QPushButton#captureButton {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #ffffff, stop:0.5 #f8f8f8, stop:1 #f0f0f0);
            border: 1px solid rgba(200, 200, 200, 0.3);
            border-radius: 25px;
            min-width: 50px;
            max-width: 50px;
            min-height: 50px;
            max-height: 50px;
            box-shadow: 0px 2px 4px rgba(0, 0, 0, 0.1);
        }
        QPushButton#captureButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #ffffff, stop:0.3 #FFA726, stop:0.7 #FF9800, stop:1 #f8f8f8);
            border: 1px solid rgba(255, 167, 38, 0.5);
            transform: scale(1.08);
            box-shadow: 0px 4px 8px rgba(255, 167, 38, 0.3);
        }
        QPushButton#captureButton:pressed {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #FF9800, stop:0.5 #FF5722, stop:1 #E64A19);
            border: 1px solid rgba(255, 87, 34, 0.8);
            transform: scale(0.92);
            box-shadow: 0px 1px 2px rgba(0, 0, 0, 0.2);
        }
        """
        
        self.capture_button.setStyleSheet(capture_button_style)

        
        # Agregar botones al layout horizontal
        control_buttons_layout.addWidget(self.pause_button)
        control_buttons_layout.addWidget(self.capture_button)
        control_buttons_layout.addWidget(self.stop_button)
        
        # === ETIQUETAS DE LOS BOTONES DE CONTROL (REMOVIDAS) ===
        # Etiquetas removidas según solicitud del usuario - los emojis son suficientes
        
        # === BOTÓN DE CONFIGURACIONES (ENGRANAJE) ===
        self.settings_button = QPushButton("⚙️")
        self.settings_button.setObjectName("settingsButton")
        self.settings_button.setMinimumSize(50, 50)
        self.settings_button.setMaximumSize(50, 50)
        self.settings_button.clicked.connect(self.on_settings_clicked)
        
        # Estilo del botón engranaje
        self.settings_button.setStyleSheet("""
        QPushButton#settingsButton {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(80, 80, 80, 200), 
                stop:1 rgba(60, 60, 60, 200));
            color: white;
            border: 2px solid rgba(255, 167, 38, 100);
            border-radius: 25px;
            font-size: 20px;
            font-weight: bold;
        }
        QPushButton#settingsButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(255, 167, 38, 220), 
                stop:1 rgba(255, 152, 0, 220));
            border: 2px solid rgba(255, 255, 255, 150);
            transform: scale(1.1);
        }
        QPushButton#settingsButton:pressed {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(255, 152, 0, 180), 
                stop:1 rgba(245, 124, 0, 180));
            border: 2px solid rgba(255, 255, 255, 200);
        }
        """)
        
        # Etiqueta para el botón de configuraciones
        settings_label = QLabel("CONFIGURACIONES")
        settings_label.setObjectName("settingsLabel")
        settings_label.setStyleSheet("""
        QLabel#settingsLabel {
            color: rgba(255, 255, 255, 160);
            font-size: 10px;
            font-family: Arial, sans-serif;
            text-align: center;
            padding: 5px;
        }
        """)
        settings_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Agregar elementos al layout
        layout.addWidget(title_label)
        layout.addWidget(self.plus_button, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(20)  # Espacio entre secciones
        layout.addLayout(control_buttons_layout)
        layout.addStretch()  # Empujar configuraciones hacia abajo
        layout.addWidget(self.settings_button, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(settings_label)
        layout.addSpacing(20)  # Espacio final para que no esté completamente al fondo
        
        # Estilo del panel
        panel.setStyleSheet("""
        QWidget#rightPanel {
            background: rgba(45, 45, 45, 150);
            border-radius: 10px;
            border: 1px solid rgba(255, 167, 38, 80);
        }
        """)
        
        return panel
    
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
            self.stacked_widget.setCurrentWidget(self.stream_widget)
            self.start_stats_monitoring()
            logger.info(f"Transición a pantalla de stream exitosa - Conectado a {ip}")
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
    
    def on_plus_button_clicked(self):
        """Manejar clic en botón flotante '+' - Mostrar formulario de inspección"""
        logger.info("Botón '+' presionado - Abriendo formulario de inspección")
        
        # Crear y mostrar el dialog de formulario de inspección
        dialog = InspectionFormDialog(self)
        
        # Conectar señal para recibir los datos guardados
        dialog.data_saved.connect(self.on_inspection_data_saved)
        
        # Mostrar dialog modal
        dialog.exec()
    
    def on_inspection_data_saved(self, data):
        """Manejar datos guardados del formulario de inspección"""
        logger.info("Datos de inspección recibidos desde el formulario")
        logger.debug(f"Datos completos: {data}")
        
        # Actualizar overlays en el video
        ref_tramo = data.get('ref_tramo', '')
        pozo_desde = data.get('pozo_desde', '')
        pozo_hasta = data.get('pozo_hasta', '')
        
        if self.video_widget:
            self.video_widget.update_ref_tramo(ref_tramo)
            self.video_widget.update_pozo_inicio(pozo_desde)
            self.video_widget.update_pozo_fin(pozo_hasta)
        
        # Mostrar resumen simplificado
        summary = f"""
📋 DATOS DE INSPECCIÓN GUARDADOS:

📅 Fecha/Hora: {data['fecha_hora']}
👤 Operario: {data['operario']}
🏙️ Ciudad: {data['ciudad']}
📍 Dirección: {data['direccion']}
🏘️ Localidad: {data['localidad']}
🔄 Sentido: {data['sentido']}
🚰 Tipo Alcant.: {data['tipo_alcant']}
🔧 Material: {data['material']}
📏 Diámetro: {data['diametro']}
⬇️ Pozo Desde: {data['pozo_desde']}
⬆️ Pozo Hasta: {data['pozo_hasta']}
🔗 Ref. Tramo: {data['ref_tramo']}
📝 Info Adicional: {data['inf_adicional'][:50]}{'...' if len(data['inf_adicional']) > 50 else ''}

🎬 Los overlays ahora se muestran en el video:
   📍 Superior: FECHA/HORA y REF. TRAMO
   📍 Inferior: POZO INICIO y POZO FIN
        """.strip()
        
        # Mostrar resumen
        QMessageBox.information(self, "✅ Datos Guardados", summary)
    
    def on_pause_clicked(self):
        """Manejar clic del botón PAUSAR"""
        logger.debug("Botón PAUSAR clickeado")
        if self.video_widget and hasattr(self.video_widget, 'pause_stream'):
            self.video_widget.pause_stream()
            logger.info("Stream pausado")
        else:
            logger.warning("No se puede pausar - video widget no disponible o función no implementada")
            QMessageBox.information(self, "Pausar Stream", "Función de pausa en desarrollo")

    def on_capture_clicked(self):
        """Manejar clic del botón CAPTURA (aro + círculo)"""
        logger.info("📷 Botón CAPTURA presionado")
        QMessageBox.information(self, "📷 Captura", "Función de captura en desarrollo")
    
    def on_stop_clicked(self):
        """Manejar clic del botón DETENER"""
        logger.debug("Botón DETENER clickeado")
        if self.video_widget and hasattr(self.video_widget, 'stop_stream'):
            self.video_widget.stop_stream()
            logger.info("Stream detenido")
            # Volver a pantalla de login después de detener
            self.disconnect_stream()
        else:
            logger.warning("No se puede detener - video widget no disponible")
    
    def on_settings_clicked(self):
        """Manejar clic en botón de configuraciones"""
        logger.info("⚙️ Botón CONFIGURACIONES presionado")
        
        # Mostrar panel de configuraciones temporal
        msg = QMessageBox(self)
        msg.setWindowTitle("⚙️ Configuraciones del Sistema")
        msg.setText("🎛️ Panel de Configuraciones")
        msg.setInformativeText(
            "Próximamente disponible:\n\n"
            "⏰ Formato de fecha/hora\n"
            "🎨 Colores y transparencias\n"
            "📐 Tamaño de textos\n"
            "🎯 Posición de overlays\n"
            "📊 Configuración de métricas\n"
            "🎥 Resolución de video\n"
            "🔧 Configuración de cámara\n"
            "💾 Opciones de grabación"
        )
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        
        # Estilo personalizado para el mensaje
        msg.setStyleSheet("""
        QMessageBox {
            background-color: #2d2d2d;
            color: white;
            font-family: Arial, sans-serif;
        }
        QMessageBox QLabel {
            color: white;
            font-size: 12px;
        }
        QMessageBox QPushButton {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(255, 167, 38, 220), 
                stop:1 rgba(255, 152, 0, 220));
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
            font-size: 12px;
        }
        QPushButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(255, 152, 0, 250), 
                stop:1 rgba(245, 124, 0, 250));
        }
        """)
        
        msg.exec()
    
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