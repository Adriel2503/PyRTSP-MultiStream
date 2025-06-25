# -*- coding: utf-8 -*-
"""
Módulo de inspección - formularios y diálogos relacionados
Refactorización modular del inspection_form_dialog.py original
"""

from .inspection_form_dialog import InspectionFormDialog
from .form_fields import FormFields
from .form_validation import FormValidation
from .styled_messages import StyledMessages

__all__ = [
    'InspectionFormDialog',
    'FormFields',
    'FormValidation', 
    'StyledMessages'
] 