# -*- coding: utf-8 -*-
"""
Pantalla de login moderna para PyRTSP-FastStream
Inspirada en el diseño de Welltep RTSP Viewer
"""

import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QFrame, QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QFont

from ..utils.constants import DEFAULT_RTSP_URL
from ..utils.logger import setup_logger

logger = setup_logger("LoginScreen")

class LoginScreen(QWidget):
    """Pantalla de login moderna con diseño profesional"""
    
    # Señal emitida cuando se hace clic en conectar
    connection_requested = pyqtSignal(str, str, str, str)  # ip, usuario, password, url_completa
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.apply_styles()
        logger.info("LoginScreen inicializada")
    
    def setup_ui(self):
        """Configurar interfaz de usuario"""
        self.resize(1200, 700)  # Tamaño inicial, pero redimensionable
        
        # Layout principal horizontal
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # === PANEL IZQUIERDO - IMAGEN/LOGO ===
        left_panel = self.create_left_panel()
        
        # === PANEL DERECHO - FORMULARIO ===
        right_panel = self.create_right_panel()
        
        # Agregar paneles al layout principal
        main_layout.addWidget(left_panel, 2)  # 60% del ancho
        main_layout.addWidget(right_panel, 1)  # 40% del ancho
    
    def create_left_panel(self):
        """Crear panel izquierdo con imagen/logo"""
        panel = QFrame()
        panel.setObjectName("leftPanel")
        
        layout = QVBoxLayout(panel)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Intentar cargar logo
        logo_label = QLabel()
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Buscar Logo.png con orden de prioridad organizado
        logo_paths = [
            "assets/images/Logo.png",    # 📍 UBICACIÓN RECOMENDADA
            "assets/Logo.png",           # Alternativa en assets/
            "Logo.png",                  # Raíz del proyecto (compatibilidad)
            "../Logo.png",               # Directorio padre
            "assets/images/logo.png",    # Minúsculas (Linux)
            "assets/logo.png"            # Minúsculas alternativa
        ]
        
        logo_loaded = False
        for path in logo_paths:
            if os.path.exists(path):
                pixmap = QPixmap(path)
                if not pixmap.isNull():
                    # Escalar imagen manteniendo proporción - MÁXIMA CALIDAD
                    # Imagen original: 2730x1030, usamos tamaño grande para aprovechar resolución
                    scaled_pixmap = pixmap.scaled(
                        1200, 515, 
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    logo_label.setPixmap(scaled_pixmap)
                    logo_loaded = True
                    logger.info(f"✅ Logo cargado exitosamente desde: {path}")
                    break
        
        if not logo_loaded:
            # Logo alternativo con texto
            logo_label.setText("🚀\nPyRTSP\nFastStream")
            logo_label.setObjectName("logoText")
            logger.warning("⚠️ Logo.png no encontrado en ninguna ubicación, usando texto alternativo")
            logger.info("💡 Coloca Logo.png en: assets/images/Logo.png para cargar tu logo personalizado")
        
        layout.addWidget(logo_label)
        
        return panel
    
    def create_right_panel(self):
        """Crear panel derecho con formulario de login"""
        panel = QFrame()
        panel.setObjectName("rightPanel")
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(40, 60, 40, 60)
        layout.setSpacing(20)
        
        # Título
        title = QLabel("ACCESO AL SISTEMA")
        title.setObjectName("loginTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(title)
        layout.addItem(QSpacerItem(20, 30, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))
        
        # === CAMPOS DE ENTRADA ===
        
        # IP de la cámara
        ip_label = QLabel("📹 Dirección IP:")
        ip_label.setObjectName("fieldLabel")
        self.ip_input = QLineEdit("192.168.18.5")
        self.ip_input.setObjectName("fieldInput")
        self.ip_input.setPlaceholderText("192.168.1.100")
        
        # Usuario
        user_label = QLabel("👤 Usuario:")
        user_label.setObjectName("fieldLabel")
        self.user_input = QLineEdit("admin")
        self.user_input.setObjectName("fieldInput")
        self.user_input.setPlaceholderText("admin")
        
        # Contraseña
        pass_label = QLabel("🔒 Contraseña:")
        pass_label.setObjectName("fieldLabel")
        self.password_input = QLineEdit("Prototipo")
        self.password_input.setObjectName("fieldInput")
        self.password_input.setPlaceholderText("********")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        # Agregar campos al layout
        for label, field in [
            (ip_label, self.ip_input),
            (user_label, self.user_input), 
            (pass_label, self.password_input)
        ]:
            layout.addWidget(label)
            layout.addWidget(field)
        
        layout.addItem(QSpacerItem(20, 30, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))
        
        # === BOTÓN CONECTAR ===
        self.connect_btn = QPushButton("CONECTAR")
        self.connect_btn.setObjectName("connectButton")
        self.connect_btn.clicked.connect(self.on_connect_clicked)
        layout.addWidget(self.connect_btn)
        
        # Spacer inferior
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        
        return panel
    
    def on_connect_clicked(self):
        """Manejar clic en botón conectar"""
        ip = self.ip_input.text().strip()
        user = self.user_input.text().strip()
        password = self.password_input.text().strip()
        # Valores fijos - no editables por el usuario
        port = "554"
        channel = "101"
        
        if not ip:
            return
        
        # Construir URL RTSP
        if user and password:
            rtsp_url = f"rtsp://{user}:{password}@{ip}:{port}/Streaming/Channels/{channel}"
        else:
            rtsp_url = f"rtsp://{ip}:{port}/Streaming/Channels/{channel}"
        
        logger.info(f"Intentando conectar a: {rtsp_url}")
        
        # Emitir señal con credenciales
        self.connection_requested.emit(ip, user, password, rtsp_url)
    
    def apply_styles(self):
        """Aplicar estilos CSS modernos"""
        style = """
        /* === PANEL IZQUIERDO === */
        QFrame#leftPanel {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #1a1a1a, stop:0.5 #2d2d2d, stop:1 #1a1a1a);
            border-right: 3px solid #FFA726;
        }
        
        QLabel#logoText {
            color: #FFA726;
            font-size: 48px;
            font-weight: bold;
            font-family: 'Arial Black', Arial, sans-serif;
            text-align: center;
            line-height: 1.2;
        }
        

        
        /* === PANEL DERECHO === */
        QFrame#rightPanel {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #f8f9fa, stop:1 #e9ecef);
            border: none;
        }
        
        QLabel#loginTitle {
            color: #1a1a1a;
            font-size: 28px;
            font-weight: bold;
            font-family: 'Arial Black', Arial, sans-serif;
            margin-bottom: 10px;
        }
        

        
        /* === CAMPOS DE ENTRADA === */
        QLabel#fieldLabel {
            color: #495057;
            font-size: 14px;
            font-weight: bold;
            font-family: Arial, sans-serif;
            margin-bottom: 5px;
        }
        
        QLineEdit#fieldInput {
            background: white;
            border: 2px solid #dee2e6;
            border-radius: 8px;
            padding: 14px 16px;
            font-size: 15px;
            font-family: Arial, sans-serif;
            color: #495057;
            min-height: 18px;
            line-height: 1.3;
        }
        
        QLineEdit#fieldInput:focus {
            border-color: #FFA726;
            background: #fff;
        }
        
        QLineEdit#fieldInput:hover {
            border-color: #adb5bd;
        }
        
        /* === BOTÓN CONECTAR === */
        QPushButton#connectButton {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #FFB74D, stop:1 #FFA726);
            color: white;
            border: none;
            border-radius: 12px;
            padding: 16px 24px;
            font-size: 18px;
            font-weight: bold;
            font-family: 'Arial Black', Arial, sans-serif;
            min-height: 20px;
        }
        
        QPushButton#connectButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #FFA726, stop:1 #FF9800);
        }
        
        QPushButton#connectButton:pressed {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #FF9800, stop:1 #F57C00);
        }
        
        QPushButton#connectButton:disabled {
            background: #adb5bd;
            color: #6c757d;
        }
        """
        
        self.setStyleSheet(style) 