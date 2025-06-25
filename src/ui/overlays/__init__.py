# -*- coding: utf-8 -*-
"""
Módulo de overlays y configuración
Contiene widgets personalizados, paneles de configuración y gestión de overlays
"""

from .overlay_config_dialog import OverlayConfigDialog
from .custom_widgets import ToggleSwitch, ColorButton
from .global_config_panel import GlobalConfigPanel
from .elements_config_panel import ElementsConfigPanel
from .style_manager import StyleManager

__all__ = [
    "OverlayConfigDialog",
    "ToggleSwitch",
    "ColorButton", 
    "GlobalConfigPanel",
    "ElementsConfigPanel",
    "StyleManager"
] 