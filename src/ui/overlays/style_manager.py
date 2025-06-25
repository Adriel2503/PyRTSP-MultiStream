# -*- coding: utf-8 -*-
"""
Gestor de estilos centralizados para overlays
Contiene todos los estilos CSS reutilizables
"""

from ...utils.logger import setup_logger

logger = setup_logger("StyleManager")

class StyleManager:
    """Gestor centralizado de estilos para componentes de overlay"""
    
    @staticmethod
    def get_dialog_style():
        """Estilo principal del diálogo"""
        return """
        QDialog {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #2c3e50, stop:1 #34495e);
        }
        """
    
    @staticmethod
    def get_group_box_style(color="#4CAF50"):
        """Estilo para group boxes"""
        return f"""
        QGroupBox {{
            font-weight: bold;
            font-size: 13px;
            color: {color};
            border: 2px solid rgba(76, 175, 80, 100);
            border-radius: 10px;
            margin-top: 15px;
            padding-top: 15px;
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 15px;
            padding: 0 10px 0 10px;
            color: {color};
        }}
        """
    
    @staticmethod
    def get_slider_style():
        """Estilo para sliders"""
        return """
        QSlider::groove:horizontal {
            background: #555555;
            height: 8px;
            border-radius: 4px;
        }
        QSlider::handle:horizontal {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #FFA726, stop:1 #FF9800);
            border: 2px solid #FF9800;
            width: 18px;
            margin: -5px 0;
            border-radius: 9px;
        }
        QSlider::handle:horizontal:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #FFB74D, stop:1 #FFA726);
        }
        QSlider::sub-page:horizontal {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #FFA726, stop:1 #FF9800);
            border-radius: 4px;
        }
        """
    
    @staticmethod
    def get_spinbox_style():
        """Estilo para spinboxes"""
        return """
        QSpinBox {
            background: #34495e;
            color: white;
            padding: 8px;
            border: 2px solid #555555;
            border-radius: 6px;
            font-weight: bold;
        }
        QSpinBox:focus {
            border: 2px solid #FFA726;
        }
        """
    
    @staticmethod
    def get_label_style(color="white", font_size="11px"):
        """Estilo para etiquetas"""
        return f"""
        QLabel {{
            color: {color};
            font-weight: bold;
            font-size: {font_size};
        }}
        """
    
    @staticmethod
    def get_datetime_label_style():
        """Estilo específico para label de fecha/hora"""
        return """
        QLabel {
            background: #34495e;
            color: white;
            padding: 8px;
            border-radius: 6px;
            font-family: 'Courier New', monospace;
            font-weight: bold;
        }
        """
    
    @staticmethod
    def get_datetime_display_style():
        """Estilo para display dinámico de fecha/hora"""
        return """
        QLabel {
            background: #34495e;
            color: #FFA726;
            padding: 8px;
            border-radius: 6px;
            font-family: 'Courier New', monospace;
            font-weight: bold;
            font-size: 12px;
        }
        """
    
    @staticmethod
    def get_datetime_display_style():
        """Estilo para display dinámico de fecha/hora"""
        return """
        QLabel {
            background: #34495e;
            color: #FFA726;
            padding: 8px;
            border-radius: 6px;
            font-family: 'Courier New', monospace;
            font-weight: bold;
            font-size: 12px;
        }
        """
    
    @staticmethod
    def get_value_label_style():
        """Estilo para labels de valores (sliders)"""
        return """
        QLabel {
            color: #FFA726; 
            font-weight: bold;
        }
        """
    
    @staticmethod
    def get_color_hex_style(bg_color="white", text_color="black"):
        """Estilo para labels de código hexadecimal"""
        return f"""
        QLabel {{
            color: {text_color}; 
            background: {bg_color}; 
            padding: 5px; 
            border-radius: 4px; 
            font-weight: bold; 
            font-family: 'Courier New';
        }}
        """
    
    @staticmethod
    def get_button_style(bg_color="#6c757d", hover_color="#757575"):
        """Estilo para botones principales"""
        return f"""
        QPushButton {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {bg_color}, stop:1 {hover_color});
            color: white;
            border: none;
            border-radius: 8px;
            font-weight: bold;
            font-size: 12px;
        }}
        QPushButton:hover {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {hover_color}, stop:1 #616161);
        }}
        """
    
    @staticmethod
    def get_apply_button_style():
        """Estilo específico para botón aplicar"""
        return """
        QPushButton {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #FFB74D, stop:1 #FFA726);
            color: white;
            border: none;
            border-radius: 8px;
            font-weight: bold;
            font-size: 12px;
        }
        QPushButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #FFA726, stop:1 #FF9800);
        }
        """
    
    @staticmethod
    def get_element_widget_style():
        """Estilo para contenedores de elementos - SIN bordes, rectángulos ni hover effects"""
        return """
        QWidget {
            background: transparent;
            border: none;
        }
        """
    
    @staticmethod
    def get_status_icon_style(enabled=True):
        """Estilo para iconos de estado"""
        if enabled:
            return """
            QLabel {
                color: #4CAF50;
                font-size: 16px;
                font-weight: bold;
                border-radius: 10px;
                background: rgba(76, 175, 80, 30);
            }
            """
        else:
            return """
            QLabel {
                color: #757575;
                font-size: 16px;
                font-weight: bold;
                border-radius: 10px;
                background: rgba(117, 117, 117, 30);
            }
            """
    
    @staticmethod
    def get_scroll_area_style():
        """Estilo para área de scroll"""
        return """
        QScrollArea {
            border: none;
            background: transparent;
        }
        """
    
    @classmethod
    def apply_theme(cls, theme_name="default"):
        """Aplicar tema específico (para futura implementación)"""
        logger.info(f"Aplicando tema: {theme_name}")
        # Aquí se puede implementar lógica para diferentes temas
        return cls 