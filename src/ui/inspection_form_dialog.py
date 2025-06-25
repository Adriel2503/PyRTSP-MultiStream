# -*- coding: utf-8 -*-
"""
Dialog de formulario para inspección - REFACTORIZADO
Ahora importa desde la nueva arquitectura modular en src/ui/inspection/

El código original de 490 líneas ha sido refactorizado en:
- src/ui/inspection/inspection_form_dialog.py (120 líneas) - Dialog principal
- src/ui/inspection/form_fields.py (170 líneas) - Campos del formulario
- src/ui/inspection/form_validation.py (70 líneas) - Validación de datos
- src/ui/inspection/styled_messages.py (80 líneas) - Mensajes personalizados
- src/ui/inspection/inspection_styles.py (200 líneas) - Estilos CSS
"""

# Importar desde la nueva ubicación modular
from .inspection import InspectionFormDialog

# Mantener compatibilidad hacia atrás
__all__ = ['InspectionFormDialog'] 