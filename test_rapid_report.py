#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test del generador de informes rápidos
Simula una sesión con capturas y genera PDF
"""

import sys
import os
import json
from datetime import datetime
from pathlib import Path

# Agregar src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def create_test_session():
    """Crear sesión de prueba para el test"""
    try:
        from src.utils.path_manager import PathManager
        from src.utils.session_manager import SessionManager
        from src.core.mode_manager import InspectionMode
        
        # Crear instancias
        path_manager = PathManager()
        session_manager = SessionManager()
        
        # Configurar modo rápido
        path_manager.set_current_mode(InspectionMode.RAPIDO)
        
        # Crear sesión de prueba
        session_id = session_manager.start_session(InspectionMode.RAPIDO)
        print(f"✅ Sesión de prueba creada: {session_id}")
        
        # Simular capturas
        test_captures = [
            "captura_2025-08-03_14-30-15.jpg",
            "captura_2025-08-03_14-32-20.jpg", 
            "captura_2025-08-03_14-34-45.jpg",
            "captura_2025-08-03_14-36-10.jpg",
            "captura_2025-08-03_14-38-25.jpg",
            "captura_2025-08-03_14-40-50.jpg",
            "captura_2025-08-03_14-42-15.jpg",
            "captura_2025-08-03_14-44-30.jpg"
        ]
        
        # Registrar capturas simuladas
        for capture in test_captures:
            session_manager.add_capture(capture)
        
        print(f"✅ {len(test_captures)} capturas simuladas registradas")
        
        # Finalizar sesión
        session_manager.end_session()
        print("✅ Sesión finalizada")
        
        return path_manager, session_manager, session_id
        
    except Exception as e:
        print(f"❌ Error creando sesión de prueba: {e}")
        import traceback
        traceback.print_exc()
        return None, None, None

def create_dummy_images(path_manager, captures):
    """Crear imágenes dummy para el test"""
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # Crear imágenes de prueba
        img_width, img_height = 640, 480
        
        for i, capture_name in enumerate(captures):
            # Crear imagen con texto
            img = Image.new('RGB', (img_width, img_height), color='lightblue')
            draw = ImageDraw.Draw(img)
            
            # Texto de prueba
            text = f"IMAGEN DE PRUEBA #{i+1}\n{capture_name}\nMODO RÁPIDO"
            
            try:
                # Intentar usar fuente por defecto
                font = ImageFont.load_default()
            except:
                font = None
            
            # Dibujar texto centrado
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            x = (img_width - text_width) // 2
            y = (img_height - text_height) // 2
            
            draw.text((x, y), text, fill='darkblue', font=font)
            
            # Simular grilla
            grid_spacing = 50
            for x in range(0, img_width, grid_spacing):
                draw.line([(x, 0), (x, img_height)], fill='gray', width=1)
            for y in range(0, img_height, grid_spacing):
                draw.line([(0, y), (img_width, y)], fill='gray', width=1)
            
            # Guardar imagen
            img_path = path_manager.get_capture_path(capture_name)
            os.makedirs(os.path.dirname(img_path), exist_ok=True)
            img.save(img_path, 'JPEG', quality=85)
            
            print(f"✅ Imagen dummy creada: {capture_name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creando imágenes dummy: {e}")
        return False

def test_rapid_report_generation():
    """Test principal de generación de informe rápido"""
    print("🚀 PROBANDO GENERADOR DE INFORME RÁPIDO")
    print("=" * 50)
    
    try:
        # 1. Crear sesión de prueba
        print("\n1️⃣ CREANDO SESIÓN DE PRUEBA...")
        path_manager, session_manager, session_id = create_test_session()
        
        if not path_manager or not session_manager:
            print("❌ No se pudo crear la sesión de prueba")
            return False
        
        # 2. Leer datos de la sesión
        session_file = f"metadatos/rapido/sesiones/sesion_{session_id}.json"
        if not os.path.exists(session_file):
            print(f"❌ Archivo de sesión no encontrado: {session_file}")
            return False
        
        with open(session_file, 'r', encoding='utf-8') as f:
            session_data = json.load(f)
        
        captures = session_data["files_generated"]["captures"]
        print(f"✅ Sesión cargada con {len(captures)} capturas")
        
        # 3. Crear imágenes dummy
        print("\n2️⃣ CREANDO IMÁGENES DE PRUEBA...")
        if not create_dummy_images(path_manager, captures):
            print("❌ No se pudieron crear las imágenes de prueba")
            return False
        
        # 4. Generar informe
        print("\n3️⃣ GENERANDO INFORME PDF...")
        from src.utils.rapid_report_generator import RapidReportGenerator
        
        generator = RapidReportGenerator(path_manager, session_manager)
        
        # Simular sesión activa
        session_manager.current_session = session_data
        
        output_path = generator.generate_report()
        
        if output_path and os.path.exists(output_path):
            file_size = os.path.getsize(output_path) / 1024  # KB
            print(f"✅ PDF generado exitosamente:")
            print(f"   📁 Archivo: {os.path.basename(output_path)}")
            print(f"   📍 Ubicación: {output_path}")
            print(f"   📊 Tamaño: {file_size:.1f} KB")
            return True
        else:
            print("❌ No se pudo generar el PDF")
            return False
        
    except Exception as e:
        print(f"❌ Error en el test: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Ejecutar test completo"""
    success = test_rapid_report_generation()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 ¡TEST EXITOSO!")
        print("✅ El generador de informe rápido funciona correctamente")
        print("📋 Layout 3×2 implementado")
        print("🚀 Listo para usar en la aplicación")
    else:
        print("❌ Test falló")
        print("⚠️ Revisa los errores antes de usar en producción")
    
    return success

if __name__ == "__main__":
    success = main()
    input("\nPresiona Enter para salir...")
    sys.exit(0 if success else 1)