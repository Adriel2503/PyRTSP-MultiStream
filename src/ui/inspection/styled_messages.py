# -*- coding: utf-8 -*-
"""
Mensajes estilizados para formularios de inspección
Maneja ventanas de advertencia y éxito con estilos personalizados
"""

from PyQt6.QtWidgets import QMessageBox

from .inspection_styles import WARNING_MESSAGE_STYLE, SUCCESS_MESSAGE_STYLE
from ...utils.logger import setup_logger

logger = setup_logger("StyledMessages")

class StyledMessages:
    """Maneja mensajes estilizados para formularios de inspección"""
    
    def __init__(self, parent_widget):
        self.parent = parent_widget
        logger.debug("StyledMessages inicializado")
    
    def show_warning(self, title, message):
        """Mostrar advertencia con estilo personalizado"""
        msg_box = QMessageBox(self.parent)
        msg_box.setWindowTitle("⚠️ " + title)
        msg_box.setText(message)
        
        # Configurar botón personalizado
        msg_box.addButton("OK", QMessageBox.ButtonRole.AcceptRole)
        
        # Aplicar estilo personalizado
        msg_box.setStyleSheet(WARNING_MESSAGE_STYLE)
        
        # Centrar el diálogo en la pantalla
        msg_box.move(
            self.parent.x() + (self.parent.width() - 360) // 2,
            self.parent.y() + (self.parent.height() - 120) // 2
        )
        
        logger.warning(f"Advertencia mostrada: {title}")
        msg_box.exec()
    
    def show_success(self, title, message):
        """Mostrar mensaje de éxito con estilo personalizado"""
        msg_box = QMessageBox(self.parent)
        msg_box.setWindowTitle("✅ " + title)
        msg_box.setText(message)
        
        # Configurar botón personalizado
        msg_box.addButton("OK", QMessageBox.ButtonRole.AcceptRole)
        
        # Aplicar estilo personalizado
        msg_box.setStyleSheet(SUCCESS_MESSAGE_STYLE)
        
        # Centrar el diálogo en la pantalla
        msg_box.move(
            self.parent.x() + (self.parent.width() - 380) // 2,
            self.parent.y() + (self.parent.height() - 140) // 2
        )
        
        logger.info(f"Éxito mostrado: {title}")
        msg_box.exec()
    
    def show_confirmation(self, title, message):
        """Mostrar confirmación con botones Sí/No"""
        msg_box = QMessageBox(self.parent)
        msg_box.setWindowTitle("❓ " + title)
        msg_box.setText(message)
        
        # Configurar botones
        yes_btn = msg_box.addButton("Sí", QMessageBox.ButtonRole.YesRole)
        no_btn = msg_box.addButton("No", QMessageBox.ButtonRole.NoRole)
        
        # Aplicar estilo similar al de advertencia
        msg_box.setStyleSheet(WARNING_MESSAGE_STYLE)
        
        # Centrar el diálogo
        msg_box.move(
            self.parent.x() + (self.parent.width() - 360) // 2,
            self.parent.y() + (self.parent.height() - 120) // 2
        )
        
        logger.info(f"Confirmación mostrada: {title}")
        result = msg_box.exec()
        
        # Devolver True si se presionó "Sí"
        return msg_box.clickedButton() == yes_btn 