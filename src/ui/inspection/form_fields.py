# -*- coding: utf-8 -*-
"""
Campos del formulario de inspección
Maneja la creación y configuración de todos los campos de entrada
"""

from PyQt6.QtWidgets import (
    QGridLayout, QLabel, QLineEdit, QComboBox, QTextEdit, QFrame
)
from PyQt6.QtCore import Qt

from ...utils.logger import setup_logger

logger = setup_logger("FormFields")

class FormFields:
    """Maneja todos los campos del formulario de inspección"""
    
    def __init__(self):
        # Referencias a todos los campos
        self.operario_input = None
        self.ciudad_input = None
        self.direccion_input = None
        self.localidad_input = None
        self.sentido_combo = None
        self.tipo_alcant_combo = None
        self.material_input = None
        self.diametro_input = None
        self.pozo_desde_input = None
        self.pozo_hasta_input = None
        self.ref_tramo_input = None
        self.inf_adicional_input = None
        
        logger.debug("FormFields inicializado")
    
    def create_form_layout(self):
        """Crear layout completo del formulario con todos los campos"""
        form_frame = QFrame()
        form_frame.setObjectName("formFrame")
        form_layout = QGridLayout(form_frame)
        form_layout.setSpacing(10)
        form_layout.setColumnStretch(1, 1)  # Columna de inputs se expande
        
        # Crear todos los campos
        self._create_operario_field(form_layout, 0)
        self._create_ciudad_field(form_layout, 1)
        self._create_direccion_field(form_layout, 2)
        self._create_localidad_field(form_layout, 3)
        self._create_sentido_field(form_layout, 4)
        self._create_tipo_alcant_field(form_layout, 5)
        self._create_material_field(form_layout, 6)
        self._create_diametro_field(form_layout, 7)
        self._create_pozo_desde_field(form_layout, 8)
        self._create_pozo_hasta_field(form_layout, 9)
        self._create_ref_tramo_field(form_layout, 10)
        self._create_inf_adicional_field(form_layout, 11)
        
        logger.info("Layout del formulario creado con 12 campos")
        return form_frame
    
    def _create_operario_field(self, layout, row):
        """Crear campo OPERARIO"""
        layout.addWidget(QLabel("OPERARIO:"), row, 0)
        self.operario_input = QLineEdit()
        self.operario_input.setPlaceholderText("NOMBRES Y APELLIDOS")
        layout.addWidget(self.operario_input, row, 1)
    
    def _create_ciudad_field(self, layout, row):
        """Crear campo CIUDAD"""
        layout.addWidget(QLabel("CIUDAD:"), row, 0)
        self.ciudad_input = QLineEdit()
        self.ciudad_input.setPlaceholderText("NOMBRE DE LA CIUDAD")
        layout.addWidget(self.ciudad_input, row, 1)
    
    def _create_direccion_field(self, layout, row):
        """Crear campo DIRECCIÓN"""
        layout.addWidget(QLabel("DIRECCIÓN:"), row, 0)
        self.direccion_input = QLineEdit()
        self.direccion_input.setPlaceholderText("CL XX No XX - XX")
        layout.addWidget(self.direccion_input, row, 1)
    
    def _create_localidad_field(self, layout, row):
        """Crear campo LOCALIDAD"""
        layout.addWidget(QLabel("LOCALIDAD:"), row, 0)
        self.localidad_input = QLineEdit()
        self.localidad_input.setPlaceholderText("NOMBRE DE LA LOCALIDAD")
        layout.addWidget(self.localidad_input, row, 1)
    
    def _create_sentido_field(self, layout, row):
        """Crear campo SENTIDO"""
        layout.addWidget(QLabel("SENTIDO:"), row, 0)
        self.sentido_combo = QComboBox()
        self.sentido_combo.addItems(["FLUJO", "CONTRAFLUJO"])
        layout.addWidget(self.sentido_combo, row, 1)
    
    def _create_tipo_alcant_field(self, layout, row):
        """Crear campo TIPO ALCANT."""
        layout.addWidget(QLabel("TIPO ALCANT.:"), row, 0)
        self.tipo_alcant_combo = QComboBox()
        self.tipo_alcant_combo.addItems(["PLUVIAL", "SANITARIO", "COMBINADO"])
        layout.addWidget(self.tipo_alcant_combo, row, 1)
    
    def _create_material_field(self, layout, row):
        """Crear campo MATERIAL"""
        layout.addWidget(QLabel("MATERIAL:"), row, 0)
        self.material_input = QLineEdit()
        self.material_input.setPlaceholderText("MATERIAL DE LA TUBERÍA")
        layout.addWidget(self.material_input, row, 1)
    
    def _create_diametro_field(self, layout, row):
        """Crear campo DIÁMETRO/TAMAÑO"""
        layout.addWidget(QLabel("DIÁMETRO/TAMAÑO:"), row, 0)
        self.diametro_input = QLineEdit()
        self.diametro_input.setPlaceholderText("DIÁMETRO O TAMAÑO EN MILÍMETROS")
        layout.addWidget(self.diametro_input, row, 1)
    
    def _create_pozo_desde_field(self, layout, row):
        """Crear campo POZO DESDE"""
        layout.addWidget(QLabel("POZO DESDE:"), row, 0)
        self.pozo_desde_input = QLineEdit()
        self.pozo_desde_input.setPlaceholderText("IDSIG POZO DESDE")
        layout.addWidget(self.pozo_desde_input, row, 1)
    
    def _create_pozo_hasta_field(self, layout, row):
        """Crear campo POZO HASTA"""
        layout.addWidget(QLabel("POZO HASTA:"), row, 0)
        self.pozo_hasta_input = QLineEdit()
        self.pozo_hasta_input.setPlaceholderText("IDSIG POZO HASTA")
        layout.addWidget(self.pozo_hasta_input, row, 1)
    
    def _create_ref_tramo_field(self, layout, row):
        """Crear campo REF. TRAMO"""
        layout.addWidget(QLabel("REF. TRAMO:"), row, 0)
        self.ref_tramo_input = QLineEdit()
        self.ref_tramo_input.setPlaceholderText("IDSIG TRAMO DE TUBERÍA")
        layout.addWidget(self.ref_tramo_input, row, 1)
    
    def _create_inf_adicional_field(self, layout, row):
        """Crear campo INF. ADICIONAL"""
        layout.addWidget(QLabel("INF. ADICIONAL:"), row, 0)
        self.inf_adicional_input = QTextEdit()
        self.inf_adicional_input.setPlaceholderText("INGRESE INFORMACIÓN ADICIONAL")
        self.inf_adicional_input.setMaximumHeight(80)
        layout.addWidget(self.inf_adicional_input, row, 1)
    
    def populate_defaults(self):
        """Llenar campos con valores por defecto"""
        # Sentido por defecto
        self.sentido_combo.setCurrentText("FLUJO")
        
        # Tipo alcantarilla por defecto
        self.tipo_alcant_combo.setCurrentText("SANITARIO")
        
        logger.debug("Campos poblados con valores por defecto")
    
    def get_all_data(self):
        """Obtener todos los datos del formulario"""
        return {
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
    
    def get_required_fields(self):
        """Obtener lista de campos requeridos para validación"""
        return [
            (self.operario_input, "OPERARIO"),
            (self.direccion_input, "DIRECCIÓN"),
            (self.localidad_input, "LOCALIDAD"),
            (self.material_input, "MATERIAL"),
            (self.diametro_input, "DIÁMETRO/TAMAÑO"),
            (self.pozo_desde_input, "POZO DESDE"),
            (self.pozo_hasta_input, "POZO HASTA"),
            (self.ref_tramo_input, "REF. TRAMO")
        ] 