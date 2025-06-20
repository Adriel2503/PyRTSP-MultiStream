# -*- coding: utf-8 -*-
"""
Sistema de logging para PyRTSP-FastStream
"""

import logging
import sys
from .constants import LOG_FORMAT, LOG_LEVEL

def setup_logger(name: str = "PyRTSP-FastStream", level: str = LOG_LEVEL) -> logging.Logger:
    """
    Configurar y obtener logger para el proyecto
    
    Args:
        name: Nombre del logger
        level: Nivel de logging (DEBUG, INFO, WARNING, ERROR)
    
    Returns:
        Logger configurado
    """
    logger = logging.getLogger(name)
    
    # Evitar duplicar handlers si ya existe
    if logger.hasHandlers():
        return logger
    
    # Configurar nivel
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(numeric_level)
    
    # Crear handler para consola
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    
    # Crear formatter
    formatter = logging.Formatter(LOG_FORMAT)
    console_handler.setFormatter(formatter)
    
    # Agregar handler al logger
    logger.addHandler(console_handler)
    
    return logger

# Logger principal del proyecto
main_logger = setup_logger() 