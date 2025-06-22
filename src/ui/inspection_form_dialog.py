# -*- coding: utf-8 -*-
"""
Dialog de formulario para texto en pantalla al inicio de la inspección
Basado en la imagen proporcionada por el usuario
"""

from datetime import datetime
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, 
    QLineEdit, QComboBox, QTextEdit, QPushButton, QFrame,
    QScrollArea, QWidget, QMessageBox, QDateTimeEdit
)
from PyQt6.QtCore import Qt, pyqtSignal, QDateTime
from PyQt6.QtGui import QFont

from ..utils.logger import setup_logger

logger = setup_logger("InspectionFormDialog")

class InspectionFormDialog(QDialog):
    """Dialog modal para formulario de inspección"""
    
    # Señal emitida cuando se guardan los datos
    data_saved = pyqtSignal(dict)  # Envía diccionario con todos los datos
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.populate_defaults()
        logger.info("InspectionFormDialog inicializado")
    
    def setup_ui(self):
        """Configurar interfaz de usuario del formulario"""
        self.setWindowTitle("Inicio de Inspección")
        self.setModal(True)
        self.resize(600, 700)
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Título
        title_label = QLabel("INFORMACIÓN DE INSPECCIÓN")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Área de scroll para el formulario
        scroll_area = QScrollArea()
        scroll_area.setObjectName("scrollArea")
        scroll_widget = QWidget()
        scroll_widget.setObjectName("scrollWidget")
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # === FORMULARIO ===
        form_frame = QFrame()
        form_frame.setObjectName("formFrame")
        form_layout = QGridLayout(form_frame)
        form_layout.setSpacing(10)
        form_layout.setColumnStretch(1, 1)  # Columna de inputs se expande
        
        row = 0
        
        # FECHA Y HORA
        form_layout.addWidget(QLabel("FECHA Y HORA:"), row, 0)
        self.fecha_hora_input = QDateTimeEdit()
        self.fecha_hora_input.setDisplayFormat("yyyy/MM/dd hh:mm")
        self.fecha_hora_input.setCalendarPopup(True)
        self.fecha_hora_input.setMinimumWidth(200)  # Ancho mínimo para el calendario
        form_layout.addWidget(self.fecha_hora_input, row, 1)
        row += 1
        
        # OPERARIO
        form_layout.addWidget(QLabel("OPERARIO:"), row, 0)
        self.operario_input = QLineEdit()
        self.operario_input.setPlaceholderText("NOMBRES Y APELLIDOS")
        form_layout.addWidget(self.operario_input, row, 1)
        row += 1
        
        # CIUDAD
        form_layout.addWidget(QLabel("CIUDAD:"), row, 0)
        self.ciudad_input = QLineEdit()
        self.ciudad_input.setPlaceholderText("NOMBRE DE LA CIUDAD")
        form_layout.addWidget(self.ciudad_input, row, 1)
        row += 1
        
        # DIRECCIÓN
        form_layout.addWidget(QLabel("DIRECCIÓN:"), row, 0)
        self.direccion_input = QLineEdit()
        self.direccion_input.setPlaceholderText("CL XX No XX - XX")
        form_layout.addWidget(self.direccion_input, row, 1)
        row += 1
        
        # LOCALIDAD
        form_layout.addWidget(QLabel("LOCALIDAD:"), row, 0)
        self.localidad_input = QLineEdit()
        self.localidad_input.setPlaceholderText("NOMBRE DE LA LOCALIDAD")
        form_layout.addWidget(self.localidad_input, row, 1)
        row += 1
        
        # SENTIDO
        form_layout.addWidget(QLabel("SENTIDO:"), row, 0)
        self.sentido_combo = QComboBox()
        self.sentido_combo.addItems(["FLUJO", "CONTRAFLUJO"])
        form_layout.addWidget(self.sentido_combo, row, 1)
        row += 1
        
        # TIPO ALCANT.
        form_layout.addWidget(QLabel("TIPO ALCANT.:"), row, 0)
        self.tipo_alcant_combo = QComboBox()
        self.tipo_alcant_combo.addItems(["PLUVIAL", "SANITARIO", "COMBINADO"])
        form_layout.addWidget(self.tipo_alcant_combo, row, 1)
        row += 1
        
        # MATERIAL
        form_layout.addWidget(QLabel("MATERIAL:"), row, 0)
        self.material_input = QLineEdit()
        self.material_input.setPlaceholderText("MATERIAL DE LA TUBERÍA")
        form_layout.addWidget(self.material_input, row, 1)
        row += 1
        
        # DIÁMETRO/TAMAÑO
        form_layout.addWidget(QLabel("DIÁMETRO/TAMAÑO:"), row, 0)
        self.diametro_input = QLineEdit()
        self.diametro_input.setPlaceholderText("DIÁMETRO O TAMAÑO EN MILÍMETROS")
        form_layout.addWidget(self.diametro_input, row, 1)
        row += 1
        
        # POZO DESDE
        form_layout.addWidget(QLabel("POZO DESDE:"), row, 0)
        self.pozo_desde_input = QLineEdit()
        self.pozo_desde_input.setPlaceholderText("IDSIG POZO DESDE")
        form_layout.addWidget(self.pozo_desde_input, row, 1)
        row += 1
        
        # POZO HASTA
        form_layout.addWidget(QLabel("POZO HASTA:"), row, 0)
        self.pozo_hasta_input = QLineEdit()
        self.pozo_hasta_input.setPlaceholderText("IDSIG POZO HASTA")
        form_layout.addWidget(self.pozo_hasta_input, row, 1)
        row += 1
        
        # REF. TRAMO
        form_layout.addWidget(QLabel("REF. TRAMO:"), row, 0)
        self.ref_tramo_input = QLineEdit()
        self.ref_tramo_input.setPlaceholderText("IDSIG TRAMO DE TUBERÍA")
        form_layout.addWidget(self.ref_tramo_input, row, 1)
        row += 1
        
        # INF. ADICIONAL
        form_layout.addWidget(QLabel("INF. ADICIONAL:"), row, 0)
        self.inf_adicional_input = QTextEdit()
        self.inf_adicional_input.setPlaceholderText("INGRESE INFORMACIÓN ADICIONAL")
        self.inf_adicional_input.setMaximumHeight(80)
        form_layout.addWidget(self.inf_adicional_input, row, 1)
        row += 1
        
        scroll_layout.addWidget(form_frame)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        main_layout.addWidget(scroll_area)
        
        # === BOTONES ===
        buttons_layout = QHBoxLayout()
        
        self.cancel_btn = QPushButton("CANCELAR")
        self.cancel_btn.setObjectName("cancelButton")
        self.cancel_btn.clicked.connect(self.reject)
        
        self.save_btn = QPushButton("GUARDAR")
        self.save_btn.setObjectName("saveButton")
        self.save_btn.clicked.connect(self.save_data)
        
        buttons_layout.addWidget(self.cancel_btn)
        buttons_layout.addStretch()  # Espacio entre botones
        buttons_layout.addWidget(self.save_btn)
        main_layout.addLayout(buttons_layout)
        
        # Aplicar estilos
        self.apply_styles()
    
    def populate_defaults(self):
        """Llenar campos con valores por defecto"""
        # Fecha y hora actual
        current_datetime = QDateTime.currentDateTime()
        self.fecha_hora_input.setDateTime(current_datetime)
        
        # Sentido por defecto
        self.sentido_combo.setCurrentText("FLUJO")
        
        # Tipo alcantarilla por defecto
        self.tipo_alcant_combo.setCurrentText("SANITARIO")
        
        logger.debug("Campos poblados con valores por defecto")
    
    def validate_data(self):
        """Validar datos requeridos"""
        required_fields = [
            (self.operario_input, "OPERARIO"),
            (self.direccion_input, "DIRECCIÓN"),
            (self.localidad_input, "LOCALIDAD"),
            (self.material_input, "MATERIAL"),
            (self.diametro_input, "DIÁMETRO/TAMAÑO"),
            (self.pozo_desde_input, "POZO DESDE"),
            (self.pozo_hasta_input, "POZO HASTA"),
            (self.ref_tramo_input, "REF. TRAMO")
        ]
        
        for field, name in required_fields:
            if not field.text().strip():
                self.show_styled_warning("Campo Requerido", 
                                        f"El campo '{name}' es requerido.\n\n"
                                        f"Por favor complete este campo antes de continuar.")
                field.setFocus()
                return False
        
        return True
    
    def show_styled_warning(self, title, message):
        """Mostrar advertencia con estilo personalizado"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("⚠️ " + title)
        msg_box.setText(message)
        # msg_box.setIcon(QMessageBox.Icon.Warning)  # Eliminado para ganar espacio
        
        # Configurar botón personalizado
        msg_box.addButton("OK", QMessageBox.ButtonRole.AcceptRole)
        
        # Estilo personalizado para el mensaje
        msg_box.setStyleSheet("""
        QMessageBox {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #f8f9fa, stop:1 #fff3e0);
            border-radius: 8px;
            min-width: 360px;
            max-height: 120px;
            min-height: 100px;
        }
        
        QMessageBox QLabel {
            font-size: 13px;
            color: #2c3e50;
            padding: 8px;
            font-family: Arial, sans-serif;
            background: transparent;
            min-width: 340px;
            text-align: left;
        }
        
        QMessageBox QPushButton {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #FFB74D, stop:1 #FFA726);
            color: white;
            border: none;
            border-radius: 6px;
            padding: 6px 20px;
            font-size: 12px;
            font-weight: bold;
            font-family: Arial, sans-serif;
            min-width: 70px;
        }
        
        QMessageBox QPushButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #FFA726, stop:1 #FF9800);
        }
        
        QMessageBox QPushButton:pressed {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #FF9800, stop:1 #F57C00);
        }
        """)
        
        # Centrar el diálogo en la pantalla
        msg_box.move(
            self.x() + (self.width() - 360) // 2,
            self.y() + (self.height() - 120) // 2
        )
        
        msg_box.exec()
    
    def show_styled_success(self, title, message):
        """Mostrar mensaje de éxito con estilo personalizado"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("✅ " + title)
        msg_box.setText(message)
        # msg_box.setIcon(QMessageBox.Icon.Information)  # Eliminado para ganar espacio
        
        # Configurar botón personalizado
        msg_box.addButton("OK", QMessageBox.ButtonRole.AcceptRole)
        
        # Estilo personalizado para mensaje de éxito
        msg_box.setStyleSheet("""
        QMessageBox {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #f0f8f0, stop:1 #e8f5e8);
            border-radius: 8px;
            min-width: 380px;
            min-height: 140px;
        }
        
        QMessageBox QLabel {
            font-size: 13px;
            color: #2c3e50;
            padding: 10px;
            font-family: Arial, sans-serif;
            background: transparent;
            min-width: 340px;
        }
        
        QMessageBox QPushButton {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #66BB6A, stop:1 #4CAF50);
            color: white;
            border: none;
            border-radius: 6px;
            padding: 10px 25px;
            font-size: 13px;
            font-weight: bold;
            font-family: Arial, sans-serif;
            min-width: 80px;
        }
        
        QMessageBox QPushButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #4CAF50, stop:1 #388E3C);
        }
        
        QMessageBox QPushButton:pressed {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #388E3C, stop:1 #2E7D32);
        }
        """)
        
        # Centrar el diálogo en la pantalla
        msg_box.move(
            self.x() + (self.width() - 380) // 2,
            self.y() + (self.height() - 140) // 2
        )
        
        msg_box.exec()
    
    def save_data(self):
        """Guardar datos del formulario"""
        if not self.validate_data():
            return
        
        # Recopilar todos los datos
        data = {
            'fecha_hora': self.fecha_hora_input.dateTime().toString("dd/MM/yyyy hh:mm"),
            'operario': self.operario_input.text().strip(),
            'ciudad': self.ciudad_input.text().strip(),
            'direccion': self.direccion_input.text().strip(),
            'localidad': self.localidad_input.text().strip(),
            'sentido': self.sentido_combo.currentText(),
            'tipo_alcant': self.tipo_alcant_combo.currentText(),
            'material': self.material_input.text().strip(),
            'diametro': self.diametro_input.text().strip(),
            'pozo_desde': self.pozo_desde_input.text().strip(),
            'pozo_hasta': self.pozo_hasta_input.text().strip(),
            'ref_tramo': self.ref_tramo_input.text().strip(),
            'inf_adicional': self.inf_adicional_input.toPlainText().strip()
        }
        
        logger.info("Datos de inspección guardados exitosamente")
        logger.debug(f"Datos: {data}")
        
        # Emitir señal con los datos
        self.data_saved.emit(data)
        
        # Mostrar confirmación
        self.show_styled_success("Datos Guardados", 
                                "✅ Información guardada exitosamente\n\n"
                                "La inspección se ha registrado correctamente.\n"
                                "Los overlays ahora se muestran en el video.")
        
        # Cerrar dialog
        self.accept()
    
    def apply_styles(self):
        """Aplicar estilos al formulario"""
        self.setStyleSheet("""
        QDialog {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #f8f9fa, stop:1 #e9ecef);
        }
        
        QLabel#titleLabel {
            font-size: 18px;
            font-weight: bold;
            color: white;
            padding: 10px;
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #FFB74D, stop:1 #FFA726);
            border-radius: 8px;
            margin-bottom: 15px;
        }
        
        QLabel {
            font-weight: bold;
            color: #2c3e50;
            font-size: 11px;
            min-width: 120px;
        }
        
        QLineEdit, QComboBox, QTextEdit, QDateTimeEdit {
            padding: 8px;
            border: 2px solid #ced4da;
            border-radius: 4px;
            background: white;
            color: black;
            font-size: 11px;
        }
        
        QComboBox::drop-down {
            border: none;
            background: transparent;
        }
        
        QComboBox::down-arrow {
            image: none;
            width: 10px;
            height: 10px;
        }
        
        QComboBox QAbstractItemView {
            background: white;
            color: black;
            border: 1px solid #FFA726;
            selection-background-color: #FFE0B2;
            selection-color: black;
        }
        
        QComboBox::item {
            background: white;
            color: black;
            padding: 5px;
        }
        
        QComboBox::item:selected {
            background: #FFE0B2;
            color: black;
        }
        
        /* Estilos básicos para el calendario */
        QCalendarWidget {
            background: white;
            min-width: 300px;
            min-height: 200px;
        }
        
        QCalendarWidget QWidget#qt_calendar_navigationbar {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #FFB74D, stop:1 #FFA726);
        }
        
        QCalendarWidget QToolButton {
            color: white;
            font-weight: bold;
        }
        
        QCalendarWidget QAbstractItemView:enabled {
            color: black;
            selection-background-color: #FFA726;
            selection-color: white;
        }
        
        /* Asegurar que todos los días sean visibles */
        QCalendarWidget QTableView {
            background: white;
            color: black;
        }
        
        /* Días específicos */
        QCalendarWidget QAbstractItemView::item {
            color: black;
            background: white;
        }
        
        /* Días del mes actual */
        QCalendarWidget QAbstractItemView::item:enabled {
            color: black;
            background: white;
        }
        
        /* Headers de días de la semana */
        QCalendarWidget QHeaderView::section {
            color: black;
            background: #f5f5f5;
            padding: 5px;
            font-weight: bold;
            min-width: 35px;
        }
        
        /* Forzar visibilidad de todos los días */
        QCalendarWidget QAbstractItemView::item:disabled {
            color: #666666;
            background: white;
        }
        
        /* Domingos específicamente */
        QCalendarWidget QTableView::item:first-child {
            color: black !important;
            background: white !important;
        }
        
        QLineEdit:focus, QComboBox:focus, QTextEdit:focus, QDateTimeEdit:focus {
            border: 2px solid #FFA726;
            background: #fff8f0;
            color: black;
        }
        
        QPushButton#saveButton {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #FFB74D, stop:1 #FFA726);
            color: white;
            border: none;
            border-radius: 6px;
            padding: 10px 20px;
            font-size: 12px;
            font-weight: bold;
            min-width: 120px;
        }
        
        QPushButton#saveButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #FFA726, stop:1 #FF9800);
        }
        
        QPushButton#cancelButton {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #6c757d, stop:1 #545b62);
            color: white;
            border: none;
            border-radius: 6px;
            padding: 10px 20px;
            font-size: 12px;
            font-weight: bold;
            min-width: 120px;
        }
        
        QPushButton#cancelButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #545b62, stop:1 #4a4f55);
        }
        
        
        QScrollArea#scrollArea {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #FFB74D, stop:1 #FFA726);
            border: none;
        }
        
        QWidget#scrollWidget {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #FFB74D, stop:1 #FFA726);
        }
        
        QFrame#formFrame {
            background: white;
            border-radius: 8px;
            padding: 15px;
            border: none;
        }
        """)  