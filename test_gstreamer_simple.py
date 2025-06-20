#!/usr/bin/env python3
"""
Test simple de GStreamer - Solo pipeline básico
Para verificar si el problema es la interfaz gráfica o la conexión
"""

import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib
import sys

def main():
    # Inicializar GStreamer
    Gst.init(None)
    
    # URL de tu cámara
    rtsp_url = "rtsp://admin:Prototipo@192.168.18.5:554/Streaming/Channels/101"
    
    print("🚀 Test simple de GStreamer")
    print(f"📹 URL: {rtsp_url}")
    print("=" * 50)
    
    # Pipeline súper simple - solo mostrar video en ventana
    pipeline_str = f"""
    rtspsrc location={rtsp_url} protocols=tcp latency=0
    ! rtph264depay
    ! avdec_h264
    ! videoconvert
    ! autovideosink
    """
    
    print("🔧 Pipeline:")
    print(pipeline_str)
    print("=" * 50)
    
    try:
        # Crear pipeline
        pipeline = Gst.parse_launch(pipeline_str)
        print("✅ Pipeline creado")
        
        # Configurar bus para mensajes
        bus = pipeline.get_bus()
        bus.add_signal_watch()
        
        def on_message(bus, message):
            msg_type = message.type
            
            if msg_type == Gst.MessageType.ERROR:
                error, debug = message.parse_error()
                print(f"❌ ERROR: {error}")
                print(f"🔧 Debug: {debug}")
                loop.quit()
                
            elif msg_type == Gst.MessageType.EOS:
                print("🔚 Fin del stream")
                loop.quit()
                
            elif msg_type == Gst.MessageType.STATE_CHANGED:
                if message.src == pipeline:
                    old_state, new_state, pending = message.parse_state_changed()
                    print(f"🔄 Estado: {old_state.value_nick} → {new_state.value_nick}")
                    
            elif msg_type == Gst.MessageType.WARNING:
                warning, debug = message.parse_warning()
                print(f"⚠️ WARNING: {warning}")
                
            elif msg_type == Gst.MessageType.INFO:
                info, debug = message.parse_info()
                print(f"ℹ️ INFO: {info}")
                
            elif msg_type == Gst.MessageType.STREAM_START:
                print("🎬 ¡Stream iniciado!")
                
            elif msg_type == Gst.MessageType.ASYNC_DONE:
                print("✅ ¡Pipeline listo! Debería aparecer ventana de video...")
        
        bus.connect("message", on_message)
        
        # Iniciar reproducción
        print("▶️ Iniciando reproducción...")
        ret = pipeline.set_state(Gst.State.PLAYING)
        
        if ret == Gst.StateChangeReturn.FAILURE:
            print("❌ Error: No se pudo iniciar pipeline")
            return
        
        print("🎥 Si todo va bien, debería aparecer una ventana con video")
        print("⏹️ Presiona Ctrl+C para salir")
        
        # Loop principal
        loop = GLib.MainLoop()
        
        try:
            loop.run()
        except KeyboardInterrupt:
            print("\n⏹️ Deteniendo...")
        
        # Limpiar
        pipeline.set_state(Gst.State.NULL)
        print("✅ Pipeline detenido")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 