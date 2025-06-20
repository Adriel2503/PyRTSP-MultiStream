# -*- coding: utf-8 -*-
"""
🔍 Verificador de Dependencias para GStreamer Viewer
"""

import sys

def test_pyqt6():
    """Verificar PyQt6"""
    try:
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import Qt
        print("✅ PyQt6 instalado correctamente")
        return True
    except ImportError as e:
        print(f"❌ PyQt6 NO instalado: {e}")
        print("💡 Instalar con: pip install PyQt6")
        return False

def test_gstreamer():
    """Verificar GStreamer y PyGObject"""
    try:
        import gi
        gi.require_version('Gst', '1.0')
        gi.require_version('GstVideo', '1.0')
        from gi.repository import Gst, GstVideo, GObject
        
        # Inicializar GStreamer
        Gst.init(None)
        version = Gst.version()
        
        print(f"✅ GStreamer {version.major}.{version.minor}.{version.micro}")
        print("✅ PyGObject instalado correctamente")
        return True
        
    except ImportError as e:
        print(f"❌ GStreamer/PyGObject NO instalado: {e}")
        print("\n💡 Instalación:")
        print("Ubuntu: sudo apt install python3-gst-1.0 gstreamer1.0-plugins-*")
        print("Windows: Descargar GStreamer SDK + pip install PyGObject")
        print("macOS: brew install gstreamer pygobject3")
        return False
    except Exception as e:
        print(f"❌ Error inicializando GStreamer: {e}")
        return False

def test_gstreamer_plugins():
    """Verificar plugins específicos de GStreamer"""
    try:
        import gi
        gi.require_version('Gst', '1.0')
        from gi.repository import Gst
        
        Gst.init(None)
        
        # Plugins necesarios
        required_plugins = [
            'rtspsrc',      # Para RTSP
            'rtph264depay', # Para H264
            'avdec_h264',   # Para decodificar H264
            'videoconvert', # Para conversión
            'autovideosink' # Para mostrar video
        ]
        
        registry = Gst.Registry.get()
        missing_plugins = []
        
        for plugin_name in required_plugins:
            plugin = registry.find_feature(plugin_name, Gst.ElementFactory.__gtype__)
            if plugin:
                print(f"✅ Plugin {plugin_name} disponible")
            else:
                print(f"❌ Plugin {plugin_name} NO encontrado")
                missing_plugins.append(plugin_name)
        
        if missing_plugins:
            print(f"\n🚨 Plugins faltantes: {missing_plugins}")
            print("💡 Instalar plugins adicionales:")
            print("Ubuntu: sudo apt install gstreamer1.0-plugins-*")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error verificando plugins: {e}")
        return False

def test_rtsp_pipeline():
    """Verificar que se puede crear un pipeline RTSP básico"""
    try:
        import gi
        gi.require_version('Gst', '1.0')
        from gi.repository import Gst
        
        Gst.init(None)
        
        # Pipeline básico de prueba
        pipeline_str = """
        videotestsrc ! video/x-raw,width=320,height=240 ! videoconvert ! autovideosink
        """
        
        pipeline = Gst.parse_launch(pipeline_str)
        
        if pipeline:
            print("✅ Pipeline de prueba creado correctamente")
            return True
        else:
            print("❌ No se pudo crear pipeline de prueba")
            return False
            
    except Exception as e:
        print(f"❌ Error creando pipeline: {e}")
        return False

def main():
    """Función principal de verificación"""
    print("🔍 VERIFICANDO DEPENDENCIAS PARA GSTREAMER_VIEWER.PY")
    print("=" * 60)
    
    all_ok = True
    
    print("\n📦 1. Verificando PyQt6...")
    if not test_pyqt6():
        all_ok = False
    
    print("\n🎬 2. Verificando GStreamer...")
    if not test_gstreamer():
        all_ok = False
    
    print("\n🔌 3. Verificando plugins GStreamer...")
    if not test_gstreamer_plugins():
        all_ok = False
    
    print("\n🧪 4. Verificando pipeline básico...")
    if not test_rtsp_pipeline():
        all_ok = False
    
    print("\n" + "=" * 60)
    
    if all_ok:
        print("🎉 ¡TODAS LAS DEPENDENCIAS ESTÁN INSTALADAS!")
        print("✅ Puedes ejecutar gstreamer_viewer.py sin problemas")
        print("\n🚀 Ejecutar con:")
        print("python gstreamer_viewer.py")
    else:
        print("❌ FALTAN DEPENDENCIAS")
        print("🔧 Instala las librerías faltantes antes de continuar")
        
        print("\n📋 RESUMEN DE INSTALACIÓN:")
        print("Ubuntu:")
        print("  sudo apt install python3-gst-1.0 gstreamer1.0-plugins-*")
        print("  pip install PyQt6")
        print("\nWindows:")
        print("  1. Descargar GStreamer SDK desde gstreamer.freedesktop.org")
        print("  2. pip install PyGObject PyQt6")
        print("\nmacOS:")
        print("  brew install gstreamer pygobject3")
        print("  pip install PyQt6")

if __name__ == "__main__":
    main() 