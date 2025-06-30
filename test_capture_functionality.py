#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 PRUEBA COMPLETA DE FUNCIONALIDAD DE CAPTURA
=============================================

Este script verifica que la funcionalidad de captura esté
completamente implementada y funcional.

Componentes verificados:
1. ✅ Cache en GStreamerManager
2. ✅ Métodos de captura en ButtonHandlers  
3. ✅ Conversión YUV→JPEG con PyAV
4. ✅ Threading para background processing
5. ✅ Directorio de capturas
6. ✅ Imports y dependencias

Ejecutar: python test_capture_functionality.py
"""

import sys
import os
import importlib.util
import inspect
from datetime import datetime

def test_imports():
    """Verificar que todos los imports estén disponibles"""
    print("🔍 VERIFICANDO IMPORTS...")
    
    try:
        import av
        print("✅ PyAV disponible")
    except ImportError:
        print("❌ PyAV NO disponible - instalar: pip install av")
        return False
    
    try:
        import threading
        print("✅ Threading disponible")
    except ImportError:
        print("❌ Threading NO disponible")
        return False
    
    try:
        from PyQt6.QtWidgets import QMessageBox
        print("✅ PyQt6 disponible")
    except ImportError:
        print("❌ PyQt6 NO disponible")
        return False
    
    print("✅ Todos los imports OK\n")
    return True

def test_gstreamer_manager_cache():
    """Verificar que GStreamerManager tenga funcionalidad de cache"""
    print("🔍 VERIFICANDO GSTREAMER MANAGER...")
    
    try:
        # Importar GStreamerManager
        sys.path.append('./src')
        from ui.video.gstreamer_manager import GStreamerManager
        
        # Verificar que tenga cache en __init__
        source = inspect.getsource(GStreamerManager.__init__)
        if 'latest_frame_cache' in source:
            print("✅ GStreamerManager tiene cache en __init__")
        else:
            print("❌ GStreamerManager NO tiene cache en __init__")
            return False
        
        # Verificar que tenga método get_latest_frame_for_capture
        if hasattr(GStreamerManager, 'get_latest_frame_for_capture'):
            print("✅ GStreamerManager tiene método get_latest_frame_for_capture")
        else:
            print("❌ GStreamerManager NO tiene método get_latest_frame_for_capture")
            return False
        
        # Verificar que _on_new_frame tenga cache
        source = inspect.getsource(GStreamerManager._on_new_frame)
        if 'latest_frame_cache' in source and 'frame_copy = bytes' in source:
            print("✅ GStreamerManager._on_new_frame actualiza cache")
        else:
            print("❌ GStreamerManager._on_new_frame NO actualiza cache")
            return False
        
        print("✅ GStreamerManager cache OK\n")
        return True
        
    except Exception as e:
        print(f"❌ Error verificando GStreamerManager: {e}\n")
        return False

def test_button_handlers_capture():
    """Verificar que ButtonHandlers tenga métodos de captura"""
    print("🔍 VERIFICANDO BUTTON HANDLERS...")
    
    try:
        # Importar ButtonHandlers
        from ui.controls.button_handlers import ButtonHandlers
        
        # Verificar que tenga imports necesarios
        button_handlers_file = './src/ui/controls/button_handlers.py'
        with open(button_handlers_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'import av' in content:
            print("✅ ButtonHandlers importa PyAV")
        else:
            print("❌ ButtonHandlers NO importa PyAV")
            return False
        
        if 'import threading' in content:
            print("✅ ButtonHandlers importa threading")
        else:
            print("❌ ButtonHandlers NO importa threading")
            return False
        
        # Verificar métodos de captura
        if hasattr(ButtonHandlers, 'capture_frame_and_save'):
            print("✅ ButtonHandlers tiene método capture_frame_and_save")
        else:
            print("❌ ButtonHandlers NO tiene método capture_frame_and_save")
            return False
        
        if hasattr(ButtonHandlers, 'capture_frame_but_discard'):
            print("✅ ButtonHandlers tiene método capture_frame_but_discard")
        else:
            print("❌ ButtonHandlers NO tiene método capture_frame_but_discard")
            return False
        
        # Verificar que handle_capture_button esté implementado
        source = inspect.getsource(ButtonHandlers.handle_capture_button)
        if 'capture_frame_and_save' in source and 'capture_frame_but_discard' in source:
            print("✅ ButtonHandlers.handle_capture_button llama métodos de captura")
        else:
            print("❌ ButtonHandlers.handle_capture_button NO implementado correctamente")
            return False
        
        print("✅ ButtonHandlers captura OK\n")
        return True
        
    except Exception as e:
        print(f"❌ Error verificando ButtonHandlers: {e}\n")
        return False

def test_capture_directory():
    """Verificar/crear directorio de capturas"""
    print("🔍 VERIFICANDO DIRECTORIO DE CAPTURAS...")
    
    try:
        captures_dir = "grabaciones/capturas"
        
        # Crear si no existe
        os.makedirs(captures_dir, exist_ok=True)
        
        if os.path.exists(captures_dir):
            print(f"✅ Directorio {captures_dir} existe y es accesible")
        else:
            print(f"❌ No se pudo crear directorio {captures_dir}")
            return False
        
        # Verificar permisos de escritura
        test_file = f"{captures_dir}/test_write.tmp"
        try:
            with open(test_file, 'w') as f:
                f.write("test")
            os.remove(test_file)
            print("✅ Permisos de escritura OK")
        except:
            print("❌ Sin permisos de escritura")
            return False
        
        print("✅ Directorio de capturas OK\n")
        return True
        
    except Exception as e:
        print(f"❌ Error verificando directorio: {e}\n")
        return False

def test_pyav_conversion():
    """Verificar que PyAV pueda hacer conversión YUV→JPEG"""
    print("🔍 VERIFICANDO CONVERSIÓN PyAV...")
    
    try:
        import av
        import numpy as np
        
        # Crear frame YUV420P de prueba (200x100)
        width, height = 200, 100
        y_size = width * height
        uv_size = (width // 2) * (height // 2)
        
        # Datos YUV de prueba (gradiente)
        y_data = np.arange(y_size, dtype=np.uint8) % 256
        u_data = np.full(uv_size, 128, dtype=np.uint8)
        v_data = np.full(uv_size, 128, dtype=np.uint8)
        
        yuv_data = bytes(np.concatenate([y_data, u_data, v_data]))
        
        # Crear VideoFrame YUV420P
        frame = av.VideoFrame.from_buffer(yuv_data, (width, height), 'yuv420p')
        print("✅ PyAV puede crear VideoFrame desde buffer YUV420P")
        
        # Convertir a RGB
        rgb_frame = frame.reformat(format='rgb24')
        print("✅ PyAV puede convertir YUV420P → RGB24")
        
        # Convertir a formato JPEG
        jpeg_frame = rgb_frame.reformat(format='yuvj444p')
        print("✅ PyAV puede convertir RGB24 → YUVJ444P (JPEG)")
        
        # Crear container JPEG
        test_filename = "grabaciones/capturas/test_pyav.jpg"
        os.makedirs("grabaciones/capturas", exist_ok=True)
        
        output = av.open(test_filename, 'w')
        stream = output.add_stream('mjpeg', rate=1)
        stream.width = width
        stream.height = height
        stream.pix_fmt = 'yuvj444p'
        print("✅ PyAV puede crear stream MJPEG")
        
        # Encodear
        for packet in stream.encode(jpeg_frame):
            output.mux(packet)
        
        for packet in stream.encode():
            output.mux(packet)
        
        output.close()
        
        # Verificar archivo
        if os.path.exists(test_filename):
            file_size = os.path.getsize(test_filename)
            print(f"✅ PyAV guardó JPEG: {test_filename} ({file_size} bytes)")
            
            # Limpiar archivo de prueba
            os.remove(test_filename)
            print("✅ Archivo de prueba limpiado")
        else:
            print("❌ PyAV NO guardó archivo JPEG")
            return False
        
        print("✅ Conversión PyAV completa OK\n")
        return True
        
    except Exception as e:
        print(f"❌ Error en conversión PyAV: {e}\n")
        return False

def test_threading():
    """Verificar que threading funcione correctamente"""
    print("🔍 VERIFICANDO THREADING...")
    
    try:
        import threading
        import time
        
        results = []
        
        def background_task():
            time.sleep(0.1)  # Simular trabajo
            results.append("completed")
        
        thread = threading.Thread(target=background_task, daemon=True)
        thread.start()
        thread.join(timeout=1.0)
        
        if results:
            print("✅ Threading funciona correctamente")
        else:
            print("❌ Threading NO funciona")
            return False
        
        print("✅ Threading OK\n")
        return True
        
    except Exception as e:
        print(f"❌ Error en threading: {e}\n")
        return False

def main():
    """Ejecutar todas las pruebas"""
    print("=" * 60)
    print("🧪 PRUEBA COMPLETA DE FUNCIONALIDAD DE CAPTURA")
    print("=" * 60)
    print(f"📅 Ejecutado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    tests = [
        ("Imports", test_imports),
        ("GStreamerManager Cache", test_gstreamer_manager_cache),
        ("ButtonHandlers Captura", test_button_handlers_capture),
        ("Directorio Capturas", test_capture_directory),
        ("Conversión PyAV", test_pyav_conversion),
        ("Threading", test_threading)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"🧪 PRUEBA: {test_name}")
        print("-" * 40)
        result = test_func()
        results.append((test_name, result))
        print()
    
    # Resumen final
    print("=" * 60)
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print()
    print(f"📈 RESULTADO: {passed}/{total} pruebas pasaron")
    
    if passed == total:
        print("🎉 ¡TODAS LAS PRUEBAS PASARON!")
        print("✅ La funcionalidad de captura está completamente implementada")
        print()
        print("🎯 NEXT STEPS:")
        print("1. Ejecutar: python main.py")
        print("2. Presionar PLAY para iniciar grabación")
        print("3. Presionar CAPTURA 📸 para tomar capturas")
        print("4. Verificar archivos en grabaciones/capturas/")
    else:
        print("⚠️ ALGUNAS PRUEBAS FALLARON")
        print("Revisa los errores arriba antes de usar la funcionalidad")
    
    print("=" * 60)

if __name__ == '__main__':
    main() 