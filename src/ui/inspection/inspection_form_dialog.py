# -*- coding: utf-8 -*-
"""
Dialog principal de formulario de inspección - REFACTORIZADO
Coordina FormFields, FormValidation y StyledMessages
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QWidget
)
from PyQt6.QtCore import Qt, pyqtSignal

from .form_fields import FormFields
from .form_validation import FormValidation
from .styled_messages import StyledMessages
from .inspection_styles import INSPECTION_DIALOG_STYLE
from ...utils.logger import setup_logger

logger = setup_logger("InspectionFormDialog")

class InspectionFormDialog(QDialog):
    """Dialog modal para formulario de inspección - arquitectura modular"""
    
    # Señal emitida cuando se guardan los datos
    data_saved = pyqtSignal(dict)  # Envía diccionario con todos los datos
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Componentes especializados
        self.form_fields = FormFields()
        self.styled_messages = StyledMessages(self)
        self.form_validation = FormValidation(self.styled_messages)
        
        self.setup_ui()
        self.form_fields.populate_defaults()
        logger.info("InspectionFormDialog inicializado con arquitectura modular")
    
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
        
        # Formulario (delegado a FormFields)
        form_frame = self.form_fields.create_form_layout()
        scroll_layout.addWidget(form_frame)
        
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        main_layout.addWidget(scroll_area)
        
        # Botones
        self._create_buttons(main_layout)
        
        # Aplicar estilos
        self.setStyleSheet(INSPECTION_DIALOG_STYLE)
    
    def _create_buttons(self, main_layout):
        """Crear botones de cancelar y guardar"""
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
    
    def save_data(self):
        """Guardar datos del formulario usando validación modular"""
        # Validar usando FormValidation
        if not self.form_validation.validate_all(self.form_fields):
            return
        
        # Obtener datos usando FormFields
        data = self.form_fields.get_all_data()
        
        logger.info("Datos de inspección guardados exitosamente")
        logger.debug(f"Datos: {data}")
        
        # Emitir señal con los datos
        self.data_saved.emit(data)
        
        # Mostrar confirmación usando StyledMessages
        self.styled_messages.show_success(
            "Datos Guardados", 
            "✅ Información guardada exitosamente\n\n"
            "La inspección se ha registrado correctamente.\n"
            "Los overlays ahora se muestran en el video."
        )
        
        # Cerrar dialog
        self.accept() 