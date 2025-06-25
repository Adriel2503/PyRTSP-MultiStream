# -*- coding: utf-8 -*-
"""
Validación de formulario de inspección
Maneja toda la lógica de validación de campos requeridos
"""

from ...utils.logger import setup_logger

logger = setup_logger("FormValidation")

class FormValidation:
    """Maneja la validación de datos del formulario de inspección"""
    
    def __init__(self, styled_messages):
        self.styled_messages = styled_messages
        logger.debug("FormValidation inicializado")
    
    def validate_required_fields(self, required_fields):
        """Validar que todos los campos requeridos estén completos"""
        for field, name in required_fields:
            if not field.text().strip():
                self.styled_messages.show_warning(
                    "Campo Requerido", 
                    f"El campo '{name}' es requerido.\n\n"
                    f"Por favor complete este campo antes de continuar."
                )
                field.setFocus()
                logger.warning(f"Campo requerido faltante: {name}")
                return False
        
        logger.info("Validación de campos requeridos exitosa")
        return True
    
    def validate_data_format(self, data):
        """Validar formato de datos específicos"""
        # Validar diámetro (debe ser numérico)
        if data['diametro'] and not self._is_valid_diameter(data['diametro']):
            self.styled_messages.show_warning(
                "Formato Incorrecto",
                "El diámetro debe ser un valor numérico.\n\n"
                "Ejemplo: 200, 300, 400"
            )
            return False
        
        # Validar que pozos desde y hasta no sean iguales
        if data['pozo_desde'] and data['pozo_hasta']:
            if data['pozo_desde'] == data['pozo_hasta']:
                self.styled_messages.show_warning(
                    "Datos Inconsistentes",
                    "El pozo de inicio y el pozo final no pueden ser iguales.\n\n"
                    "Por favor verifique los identificadores de pozos."
                )
                return False
        
        logger.info("Validación de formato de datos exitosa")
        return True
    
    def _is_valid_diameter(self, diameter_str):
        """Verificar si el diámetro tiene formato válido"""
        try:
            # Intentar convertir a float
            diameter = float(diameter_str.replace(',', '.'))
            # Validar rango razonable (10mm a 5000mm)
            return 10 <= diameter <= 5000
        except ValueError:
            return False
    
    def validate_all(self, form_fields):
        """Validar todos los aspectos del formulario"""
        # Obtener campos requeridos y datos
        required_fields = form_fields.get_required_fields()
        data = form_fields.get_all_data()
        
        # Validar campos requeridos
        if not self.validate_required_fields(required_fields):
            return False
        
        # Validar formato de datos
        if not self.validate_data_format(data):
            return False
        
        logger.info("Validación completa del formulario exitosa")
        return True 