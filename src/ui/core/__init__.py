# -*- coding: utf-8 -*-
"""
Módulo core de la interfaz de usuario
Contiene componentes principales de la aplicación con arquitectura MVC
"""

from .main_window import MainWindow
from .application_controller import ApplicationController
from .window_manager import WindowManager

__all__ = [
    "MainWindow",
    "ApplicationController", 
    "WindowManager"
] 