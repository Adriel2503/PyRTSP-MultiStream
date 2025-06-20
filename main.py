#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Punto de entrada principal para PyRTSP-FastStream
Sistema Profesional de Streaming RTSP de Ultra Baja Latencia
"""

import sys
import os

# Agregar el directorio src al path para imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.application import run_application

def main():
    """Función principal del programa"""
    try:
        exit_code = run_application()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n🛑 Aplicación interrumpida por el usuario")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error fatal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 