# -*- coding: utf-8 -*-
"""
Widgets personalizados para configuración de overlays
Extraído de overlay_config_dialog.py para reutilización
"""

from PyQt6.QtWidgets import QCheckBox, QPushButton, QColorDialog
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QColor

from ...utils.logger import setup_logger

logger = setup_logger("CustomWidgets")

class ToggleSwitch(QCheckBox):
    """Switch toggle personalizado con estilo iOS"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(50, 25)
        self.setStyleSheet("""
        QCheckBox {
            border: none;
            outline: none;
        }
        QCheckBox::indicator {
            width: 50px;
            height: 25px;
            border-radius: 12px;
            background-color: #555555;
            border: 2px solid #333333;
        }
        QCheckBox::indicator:checked {
            background-color: #4CAF50;
            border: 2px solid #45a049;
        }
        QCheckBox::indicator:checked:after {
            content: "";
            width: 19px;
            height: 19px;
            border-radius: 9px;
            background-color: white;
            margin: 1px;
            position: absolute;
            right: 2px;
        }
        QCheckBox::indicator:unchecked:after {
            content: "";
            width: 19px;
            height: 19px;
            border-radius: 9px;
            background-color: white;
            margin: 1px;
            position: absolute;
            left: 2px;
        }
        """)
        logger.debug("ToggleSwitch creado")

class ColorButton(QPushButton):
    """Botón selector de color personalizado"""
    
    color_changed = pyqtSignal(QColor)
    
    def __init__(self, initial_color=QColor(255, 167, 38), parent=None):
        super().__init__(parent)
        self.current_color = initial_color
        self.setFixedSize(40, 30)
        self.update_style()
        self.clicked.connect(self.choose_color)
        logger.debug(f"ColorButton creado con color inicial: {initial_color.name()}")
    
    def update_style(self):
        """Actualizar el estilo del botón con el color actual"""
        rgb = f"rgb({self.current_color.red()}, {self.current_color.green()}, {self.current_color.blue()})"
        hex_color = self.current_color.name()
        self.setStyleSheet(f"""
        QPushButton {{
            background-color: {rgb};
            border: 2px solid #000000;
            border-radius: 6px;
            padding: 2px;
        }}
        QPushButton:hover {{
            border: 2px solid #FFA726;
        }}
        QPushButton:pressed {{
            border: 3px solid #FF9800;
            background-color: {rgb};
            box-shadow: inset 0 2px 4px rgba(0,0,0,0.3);
        }}
        """)
        self.setToolTip(f"Color: {hex_color.upper()}")
    
    def choose_color(self):
        """Abrir diálogo de selección de color"""
        color = QColorDialog.getColor(self.current_color, self, "Seleccionar Color")
        if color.isValid():
            self.current_color = color
            self.update_style()
            self.color_changed.emit(color)
            logger.debug(f"Color cambiado a: {color.name()}")
    
    def get_color(self):
        """Obtener color actual"""
        return self.current_color
    
    def set_color(self, color):
        """Establecer color"""
        self.current_color = color
        self.update_style()
        logger.debug(f"Color establecido: {color.name()}")


class EyeToggleButton(QPushButton):
    """Botón toggle con icono de ojo abierto/cerrado"""
    
    toggled = pyqtSignal(bool)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._checked = True  # Estado interno
        self.setFixedSize(35, 25)
        self.setCheckable(True)
        self.setChecked(True)
        self.clicked.connect(self._on_clicked)
        self.update_appearance()
        logger.debug("EyeToggleButton creado")
    
    def _on_clicked(self):
        """Manejar click del botón"""
        self._checked = not self._checked
        self.update_appearance()
        self.toggled.emit(self._checked)
    
    def update_appearance(self):
        """Actualizar apariencia según estado"""
        if self._checked:
            # Ojo abierto - elemento visible
            self.setText("👁")
            self.setStyleSheet("""
            QPushButton {
                background: #4CAF50;
                color: white;
                border: 2px solid #45a049;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #45a049;
                border: 2px solid #4CAF50;
            }
            """)
            self.setToolTip("Elemento visible - Click para ocultar")
        else:
            # Ojo cerrado - elemento oculto
            self.setText("👁‍🗨")
            self.setStyleSheet("""
            QPushButton {
                background: #757575;
                color: white;
                border: 2px solid #616161;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #616161;
                border: 2px solid #757575;
            }
            """)
            self.setToolTip("Elemento oculto - Click para mostrar")
    
    def isChecked(self):
        """Obtener estado actual"""
        return self._checked
    
    def setChecked(self, checked):
        """Establecer estado"""
        if self._checked != checked:
            self._checked = checked
            self.update_appearance()
            self.toggled.emit(self._checked)