# -*- coding: utf-8 -*-
"""
Manejadores de eventos para botones
Extraído de main_window.py para mejor modularización
"""

from PyQt6.QtWidgets import QMessageBox
from datetime import datetime
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst
import av
import threading
import os
import time
import numpy as np

from ...utils.logger import setup_logger
from ...utils.path_manager import get_path_manager
from ...utils.session_manager import get_session_manager
from ...utils.rapid_report_generator import RapidReportGenerator
from ...core.mode_manager import InspectionMode
from ..inspection_form_dialog import InspectionFormDialog
from ..overlays.overlay_config_dialog import OverlayConfigDialog

logger = setup_logger("ButtonHandlers")

class ButtonHandlers:
    """Clase para manejar eventos de botones de la aplicación"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.is_recording = False
        
        # Inicializar gestores de rutas y sesión
        self.path_manager = get_path_manager()
        self.session_manager = get_session_manager()
        
        # Inicializar generador de informes rápidos
        self.rapid_report_generator = RapidReportGenerator(self.path_manager, self.session_manager)
        
        logger.info("ButtonHandlers inicializado con gestores de rutas, sesión y generador de informes")
    
    def handle_plus_button(self):
        """Manejar clic en botón flotante '+' - Mostrar formulario de inspección"""
        logger.info("Botón '+' presionado - Abriendo formulario de inspección")
        
        # Obtener modo actual
        current_mode = self.main_window.mode_manager.current_mode
        
        # Crear y mostrar el dialog de formulario de inspección con el modo
        dialog = InspectionFormDialog(self.main_window, current_mode)
        
        # Conectar señal para recibir los datos guardados
        dialog.data_saved.connect(self.handle_inspection_data_saved)
        
        # Mostrar dialog modal
        dialog.exec()
    
    def handle_inspection_data_saved(self, data):
        """Manejar datos guardados del formulario de inspección"""
        logger.info("Datos de inspección recibidos desde el formulario")
        logger.debug(f"Datos completos: {data}")
        
        # ✅ NUEVO: Actualizar datos de inspección en la sesión actual
        self.session_manager.update_inspection_data(data)
        
        # ✅ NUEVO: Refrescar estado del botón + en el control panel
        if hasattr(self.main_window, 'control_panel'):
            self.main_window.control_panel.refresh_plus_button_state()
        
        # Actualizar overlays en el video
        ref_tramo = data.get('ref_tramo', '')
        pozo_desde = data.get('pozo_desde', '')
        pozo_hasta = data.get('pozo_hasta', '')
        
        if self.main_window.video_widget:
            self.main_window.video_widget.update_ref_tramo(ref_tramo)
            self.main_window.video_widget.update_pozo_inicio(pozo_desde)
            self.main_window.video_widget.update_pozo_fin(pozo_hasta)
            
            # ✅ IMPORTANTE: Activar elementos dependientes del formulario
            self.main_window.video_widget.enable_form_elements()
        
        # Mostrar resumen simplificado
        summary = f"""
📋 DATOS DE INSPECCIÓN GUARDADOS:

👤 Operario: {data['operario']}
🏙️ Ciudad: {data['ciudad']}
📍 Dirección: {data['direccion']}
🏘️ Localidad: {data['localidad']}
🔄 Sentido: {data['sentido']}
🚰 Tipo Alcant.: {data['tipo_alcant']}
🔧 Material: {data['material']}
📏 Diámetro: {data['diametro']}
⬇️ Pozo Desde: {data['pozo_desde']}
⬆️ Pozo Hasta: {data['pozo_hasta']}
🔗 Ref. Tramo: {data['ref_tramo']}
📝 Info Adicional: {data['inf_adicional'][:50]}{'...' if len(data['inf_adicional']) > 50 else ''}

🎬 Los overlays ahora se muestran en el video:
   📍 Superior: REF. TRAMO
   📍 Inferior: POZO INICIO y POZO FIN

💾 Datos almacenados en la sesión actual
📁 Se incluirán en los metadatos JSON
        """.strip()
        
        # Mostrar resumen
        QMessageBox.information(self.main_window, "✅ Datos Guardados", summary)
    
    def handle_record_button(self):
        """Iniciar grabación al presionar el botón de grabación"""
        if not self.is_recording:
            # Usar PathManager para generar ruta según el modo activo
            filename = self.path_manager.generate_recording_filename()
            
            # Configurar y iniciar el pipeline de GStreamer para grabación
            success = self.start_gstreamer_recording(filename)
            
            if success:
                self.is_recording = True
                logger.info(f"📹 ✅ GRABACIÓN INICIADA: {filename}")
                
                # Registrar grabación en la sesión actual
                self.session_manager.add_recording(filename)
                
                # Obtener información para mostrar al usuario
                basename = os.path.basename(filename)
                mode_folder = self.path_manager.get_current_mode_folder()
                
                # Mostrar confirmación en pantalla
                QMessageBox.information(
                    self.main_window, 
                    "🎬 GRABACIÓN INICIADA", 
                    f"✅ Grabación iniciada exitosamente\n\n"
                    f"📁 Archivo: {basename}\n"
                    f"📍 Ubicación: metadatos/{mode_folder}/grabaciones/\n"
                    f"🎯 Estado: GRABANDO ACTIVAMENTE\n\n"
                    f"💡 Presiona STOP para detener la grabación"
                )
            else:
                logger.error("📹 ❌ ERROR AL INICIAR GRABACIÓN")
                QMessageBox.critical(
                    self.main_window, 
                    "❌ ERROR DE GRABACIÓN", 
                    "No se pudo iniciar la grabación.\n\n"
                    "Verifica:\n"
                    "• Que el stream esté activo\n"
                    "• Que las carpetas de modo existan\n"
                    "• Los logs en la terminal para más detalles"
                )
        else:
            logger.warning("📹 ⚠️ LA GRABACIÓN YA ESTÁ EN CURSO")
            QMessageBox.warning(
                self.main_window, 
                "⚠️ GRABACIÓN ACTIVA", 
                "La grabación ya está en curso.\n\n"
                "Presiona STOP para detener la grabación actual\n"
                "antes de iniciar una nueva."
            )
    
    def handle_capture_button(self):
        """Manejar clic del botón CAPTURA - Implementación completa"""
        logger.info("📷 Botón CAPTURA presionado")
        
        if self.is_recording:
            # ✅ MODO GRABANDO: Capturar Y guardar
            try:
                success = self.capture_frame_and_save()
                if success:
                    # Registrar captura en la sesión actual
                    filename = self.path_manager.generate_capture_filename()
                    self.session_manager.add_capture(filename)
                    
                    # Obtener información para mostrar al usuario
                    mode_folder = self.path_manager.get_current_mode_folder()
                    
                    QMessageBox.information(
                        self.main_window, 
                        "📷 Captura Iniciada", 
                        "✅ Captura procesándose en background\n\n"
                        f"📁 Ubicación: metadatos/{mode_folder}/capturas/\n"
                        "🖼️ Formato: JPEG (PyAV/FFmpeg, ultra-rápido)\n"
                        "📐 Resolución: 2560×1440\n"
                        "🎯 Incluye todos los overlays Cairo\n\n"
                        "⚡ Encoding FFmpeg nativo (C++)\n"
                        "RGB→JPEG directo, sin interrumpir grabación"
                    )
                else:
                    QMessageBox.critical(
                        self.main_window,
                        "❌ Error de Captura",
                        "No se pudo guardar la captura.\n\n"
                        "Posibles causas:\n"
                        "• Grabación no iniciada (requerida para capturas)\n"
                        "• Permisos de escritura en carpetas de modo\n"
                        "• Espacio en disco disponible\n\n"
                        "💡 Tip: DEBES iniciar grabación primero\n"
                        "Las capturas usan frames del proceso de grabación"
                    )
            except Exception as e:
                logger.error(f"❌ Error en captura durante grabación: {e}")
                QMessageBox.critical(
                    self.main_window,
                    "❌ Error Técnico",
                    f"Error técnico en captura:\n{str(e)}"
                )
        else:
            # ❌ MODO SIN GRABAR: Capturar pero NO guardar
            try:
                # Verificar disponibilidad de capturas (requiere grabación activa)
                frame_captured = self.capture_frame_but_discard()
                if frame_captured:
                    QMessageBox.information(
                        self.main_window,
                        "📷 Captura NO Disponible",
                        "❌ No se puede capturar sin grabación activa\n\n"
                        "El sistema de capturas requiere que\n"
                        "la grabación esté en curso.\n\n"
                        "💡 Para tomar capturas:\n"
                        "1. Presione PLAY para iniciar grabación\n"
                        "2. Luego use el botón CAPTURA 📸\n\n"
                        "🎯 La captura incluirá todos los overlays"
                    )
                else:
                    QMessageBox.warning(
                        self.main_window,
                        "⚠️ Stream No Disponible",
                        "No se puede capturar frame.\n\n"
                        "Verifica que el stream esté conectado\n"
                        "y funcionando correctamente."
                    )
            except Exception as e:
                logger.error(f"❌ Error en captura sin grabación: {e}")
                QMessageBox.warning(
                    self.main_window,
                    "⚠️ Error de Captura",
                    "No se pudo procesar la captura.\n\n"
                    "Verifica que el stream esté activo."
                )
    
    def handle_stop_button(self):
        """Detener grabación al presionar el botón de detener"""
        if self.is_recording:
            # Detener el pipeline de GStreamer y guardar el archivo
            success = self.stop_gstreamer_recording()
            
            if success:
                self.is_recording = False
                logger.info("📹 ✅ GRABACIÓN DETENIDA Y GUARDADA")
                
                # Mostrar confirmación en pantalla
                QMessageBox.information(
                    self.main_window, 
                    "🛑 GRABACIÓN DETENIDA", 
                    "✅ Grabación detenida exitosamente\n\n"
                    f"📁 Archivo guardado en:\n"
                    f"C:/Users/ariel/Documents/Welltep/grabaciones/\n\n"
                    f"🎯 Estado: LISTO PARA NUEVA GRABACIÓN\n\n"
                    f"💡 Presiona PLAY para iniciar nueva grabación"
                )
            else:
                logger.error("📹 ❌ ERROR AL DETENER GRABACIÓN")
                QMessageBox.critical(
                    self.main_window, 
                    "❌ ERROR AL DETENER", 
                    "Hubo un problema al detener la grabación.\n\n"
                    "Verifica los logs en la terminal para más detalles."
                )
        else:
            logger.warning("📹 ⚠️ NO HAY GRABACIÓN EN CURSO PARA DETENER")
            QMessageBox.warning(
                self.main_window, 
                "⚠️ SIN GRABACIÓN ACTIVA", 
                "No hay grabación en curso para detener.\n\n"
                "Presiona PLAY para iniciar una nueva grabación."
            )
    
    def handle_annotate_button(self):
        """Manejar clic del botón ANOTAR - iniciar anotación dinámica en el video"""
        logger.info("📝 Botón ANOTAR presionado - Iniciando anotación dinámica")
        
        if self.main_window.video_widget:
            if self.main_window.video_widget.is_annotation_active():
                # Si ya está activo, detenerlo
                self.main_window.video_widget.stop_annotation()
                QMessageBox.information(self.main_window, "📝 Anotación", 
                                       "Modo de anotación detenido.\n\n"
                                       "La anotación ha sido guardada.")
            else:
                # Iniciar modo de anotación
                self.main_window.video_widget.start_annotation()
                QMessageBox.information(self.main_window, "📝 Anotación Activa", 
                                       "¡Modo de anotación iniciado!\n\n"
                                       "• Escribe directamente en el video\n"
                                       "• ENTER: Guardar y salir\n"
                                       "• ESC: Cancelar\n"
                                       "• BACKSPACE: Borrar\n\n"
                                       "El texto aparecerá debajo de la línea roja.")
        else:
            logger.warning("Video widget no disponible para anotaciones")
            QMessageBox.warning(self.main_window, "📝 Error", 
                               "No se puede iniciar anotación.\n"
                               "Video no disponible.")
    
    def handle_reset_distance_button(self):
        """Manejar clic del botón RESETEAR DISTANCIA"""
        logger.info("📏 Botón RESETEAR DISTANCIA presionado")
        # Por el momento solo mostrar mensaje - funcionalidad a implementar
        QMessageBox.information(self.main_window, "📏 Resetear Distancia", 
                               "Función de resetear distancia en desarrollo.\n\n"
                               "Esta función permitirá reiniciar el contador\n"
                               "de distancia recorrida en la inspección.")
    
    def handle_clear_screen_button(self):
        """Manejar clic del botón LIMPIAR PANTALLA"""
        logger.info("🧹 Botón LIMPIAR PANTALLA presionado")
        
        if self.main_window.video_widget:
            # Limpiar anotaciones activas
            if self.main_window.video_widget.is_annotation_active():
                self.main_window.video_widget.stop_annotation()
                logger.info("✅ Anotación limpiada")
            
            # Aquí se pueden agregar más limpiezas en el futuro
            # Por ejemplo: resetear distancia, limpiar otros overlays temporales, etc.
            
            # ✅ Pantalla limpiada silenciosamente (sin mensaje molesto)
        else:
            logger.warning("Video widget no disponible para limpiar")
            # ✅ Error silencioso, solo en logs
    
    def handle_settings_button(self):
        """Manejar clic en botón de configuraciones"""
        logger.info("⚙️ Botón CONFIGURACIONES presionado - Abriendo configuración de overlays")
        
        # Obtener configuración actual del video widget
        current_config = {}
        if self.main_window.video_widget:
            current_config = self.main_window.video_widget.get_overlay_config()
            logger.info(f"Configuración actual obtenida: {current_config}")
        
        # Crear y mostrar el diálogo de configuración de overlays
        config_dialog = OverlayConfigDialog(self.main_window, current_config)
        
        # Conectar señal para recibir cambios de configuración
        config_dialog.overlay_config_changed.connect(self.handle_overlay_config_changed)
        
        # Mostrar diálogo modal
        config_dialog.exec()
    
    def handle_overlay_config_changed(self, config):
        """Manejar cambios en la configuración de overlays"""
        logger.info(f"Configuración de overlays cambiada: {config}")
        
        # Aplicar configuración al video widget si está disponible
        if self.main_window.video_widget:
            self.main_window.video_widget.update_overlay_config(config)
            logger.info("Configuración aplicada al video widget")
        else:
            logger.warning("Video widget no disponible para aplicar configuración")
        
        # Mostrar confirmación al usuario
        enabled_items = []
        if config.get('grid_enabled', False):
            enabled_items.append("📐 Cuadrículas")
        if config.get('fecha_enabled', False):
            enabled_items.append("📅 Fecha y hora")
        if config.get('tramo_enabled', False):
            enabled_items.append("🔗 Referencia de tramo")
        if config.get('pozo_inicial_enabled', False):
            enabled_items.append("⬇️ Pozo inicial")
        if config.get('pozo_final_enabled', False):
            enabled_items.append("⬆️ Pozo final")
        
        if enabled_items:
            items_text = "\n".join(enabled_items)
            summary = f"✅ Configuración aplicada exitosamente\n\nElementos activos:\n{items_text}"
        else:
            summary = "⚠️ Todos los overlays han sido deshabilitados"
        
        # Mostrar confirmación
        QMessageBox.information(self.main_window, "⚙️ Configuración Aplicada", summary)

    def start_gstreamer_recording(self, filename):
        """Iniciar grabación con PyAV"""
        logger.info(f"🎬 Iniciando grabación PyAV: {filename}")
        
        # Usar el GStreamerManager con PyAV
        if self.main_window.video_widget and hasattr(self.main_window.video_widget, 'gstreamer_manager'):
            gstreamer_manager = self.main_window.video_widget.gstreamer_manager
            
            # Iniciar grabación con PyAV
            success = gstreamer_manager.start_recording(filename)
            
            if success:
                logger.info(f"✅ GRABACIÓN PyAV INICIADA: {filename}")
                return True
            else:
                logger.error("❌ ERROR AL INICIAR GRABACIÓN PyAV")
                return False
        else:
            logger.error("❌ Video widget o GStreamer manager no disponible")
            return False

    def stop_gstreamer_recording(self):
        """Detener grabación con PyAV"""
        logger.info("🛑 Deteniendo grabación PyAV...")
        
        # Usar el GStreamerManager con PyAV
        if self.main_window.video_widget and hasattr(self.main_window.video_widget, 'gstreamer_manager'):
            gstreamer_manager = self.main_window.video_widget.gstreamer_manager
            
            # Detener grabación con PyAV
            success = gstreamer_manager.stop_recording()
            
            if success:
                logger.info("✅ GRABACIÓN PyAV DETENIDA")
                return True
            else:
                logger.error("❌ ERROR AL DETENER GRABACIÓN PyAV")
                return False
        else:
            logger.error("❌ Video widget o GStreamer manager no disponible")
            return False 

    def capture_frame_and_save(self):
        """Capturar frame y guardarlo usando PyAV - MODO GRABANDO"""
        try:
            # Obtener frame desde el cache del GStreamerManager
            if not hasattr(self.main_window.video_widget, 'gstreamer_manager'):
                logger.error("❌ GStreamerManager no disponible")
                return False
            
            gstreamer_manager = self.main_window.video_widget.gstreamer_manager
            frame_data = gstreamer_manager.get_latest_frame_for_capture()
            
            if not frame_data:
                logger.error("❌ No hay frame disponible para captura")
                return False
            
            raw_data, width, height = frame_data
            logger.info(f"📷 Capturando frame {width}x{height}, {len(raw_data)} bytes")
            
            # Usar PathManager para generar ruta según el modo activo
            filename = self.path_manager.generate_capture_filename()
            
            # Procesar en background thread para no bloquear UI
            def save_frame_background():
                try:
                    logger.info(f"🚀 Encoding JPEG ultra-rápido con PyAV/FFmpeg...")
                    
                    # ¡Los datos YA están en RGB! Conversión directa con PyAV
                    # El pipeline tiene: videoconvert ! video/x-raw,format=RGB ! appsink
                    
                    # Calcular dimensiones esperadas para RGB (3 bytes por pixel)
                    expected_size = width * height * 3
                    actual_size = len(raw_data)
                    
                    logger.info(f"📐 Dimensiones: {width}x{height}")
                    logger.info(f"📊 Datos: esperados {expected_size} bytes, recibidos {actual_size} bytes")
                    
                    if actual_size != expected_size:
                        logger.warning(f"⚠️ Tamaño de datos no coincide - ajustando...")
                        if actual_size > expected_size:
                            raw_data_fixed = raw_data[:expected_size]
                        else:
                            raw_data_fixed = raw_data + b'\x00' * (expected_size - actual_size)
                    else:
                        raw_data_fixed = raw_data
                    
                    # Convertir buffer RGB a numpy array
                    rgb_array = np.frombuffer(raw_data_fixed, dtype=np.uint8)
                    rgb_image = rgb_array.reshape((height, width, 3))
                    
                    # MÉTODO PyAV: VideoFrame desde numpy RGB24
                    frame = av.VideoFrame.from_ndarray(rgb_image, format='rgb24')
                    
                    # Crear output container JPEG con PyAV/FFmpeg
                    output = av.open(filename, 'w')
                    stream = output.add_stream('mjpeg', rate=1)
                    stream.width = width
                    stream.height = height
                    stream.pix_fmt = 'yuvj420p'  # JPEG estándar
                    
                    # PyAV auto-convierte RGB24 → YUVJ420P para JPEG
                    jpeg_frame = frame.reformat(format='yuvj420p')
                    
                    # Encoding nativo FFmpeg (C++) - ULTRA RÁPIDO
                    for packet in stream.encode(jpeg_frame):
                        output.mux(packet)
                    
                    # Flush encoder
                    for packet in stream.encode():
                        output.mux(packet)
                    
                    output.close()
                    
                    file_size = os.path.getsize(filename)
                    logger.info(f"✅ CAPTURA PyAV/FFmpeg: {filename} ({file_size/1024:.1f} KB)")
                    
                except Exception as e:
                    logger.error(f"❌ Error en captura PyAV: {e}")
                    import traceback
                    logger.error(f"Detalles: {traceback.format_exc()}")
            
            # Ejecutar en background
            thread = threading.Thread(target=save_frame_background, daemon=True)
            thread.start()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error en captura: {e}")
            return False

    def capture_frame_but_discard(self):
        """Verificar si hay frames disponibles pero NO guardar - MODO SIN GRABAR"""
        try:
            # Solo verificar disponibilidad sin guardar
            if not hasattr(self.main_window.video_widget, 'gstreamer_manager'):
                logger.warning("⚠️ GStreamerManager no disponible")
                return False
            
            gstreamer_manager = self.main_window.video_widget.gstreamer_manager
            frame_data = gstreamer_manager.get_latest_frame_for_capture()
            
            if frame_data:
                raw_data, width, height = frame_data
                logger.info(f"📷 Frame verificado: {width}x{height}, {len(raw_data)} bytes - NO guardado")
                return True
            else:
                logger.warning("⚠️ No hay frames en cache")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error verificando frame: {e}")
            return False
    
    def handle_report_button(self):
        """Manejar clic del botón INFORME - Generar según el modo"""
        logger.info("📋 Botón INFORME presionado")
        
        # Obtener información básica de la sesión actual
        session_info = self.session_manager.get_current_session_info()
        
        if not session_info:
            # No hay sesión activa
            QMessageBox.information(
                self.main_window,
                "📋 Generar Informe",
                "❌ No hay sesión activa\n\n"
                "Para generar un informe:\n"
                "1. Inicia una inspección\n"
                "2. Realiza capturas de video\n"
                "3. Luego genera el informe\n\n"
                "🔄 El informe incluirá todas las capturas de la sesión actual"
            )
            return
        
        # Obtener datos básicos
        mode_name = session_info.get('mode_name', 'Desconocido')
        captures_count = session_info.get('session_stats', {}).get('captures_count', 0)
        mode_folder = self.path_manager.get_current_mode_folder()
        current_mode = session_info.get('mode', '')
        
        if captures_count == 0:
            # Sesión sin capturas
            QMessageBox.information(
                self.main_window,
                "📋 Generar Informe",
                "❌ No hay capturas en esta sesión\n\n"
                "Para generar un informe necesitas:\n"
                "• Al menos 1 captura de pantalla\n"
                "• Usa el botón 📸 CAPTURA durante la grabación\n\n"
                f"💡 Modo actual: {mode_name}\n"
                f"📁 Las capturas se guardan en: metadatos/{mode_folder}/capturas/"
            )
            return
        
        # ✅ GENERAR INFORME SEGÚN EL MODO
        if current_mode == "rapido":
            # MODO RÁPIDO: Generar PDF real
            self._generate_rapid_report(session_info, captures_count)
        else:
            # OTROS MODOS: Mensaje de desarrollo
            QMessageBox.information(
                self.main_window,
                "📋 Generar Informe",
                f"🚀 MODO {mode_name.upper()}\n\n"
                "📊 Información de la sesión actual:\n"
                f"• Modo: {mode_name}\n"
                f"• Capturas disponibles: {captures_count}\n"
                f"• Ubicación: metadatos/{mode_folder}/\n\n"
                "⏳ Informe para este modo próximamente disponible...\n\n"
                "✅ El modo RÁPIDO ya está implementado"
            )
    
    def _generate_rapid_report(self, session_info: dict, captures_count: int):
        """Generar informe para MODO RÁPIDO"""
        try:
            logger.info("🚀 Generando informe rápido...")
            
            # Generar PDF
            output_path = self.rapid_report_generator.generate_report()
            
            if output_path and os.path.exists(output_path):
                # ✅ PDF generado exitosamente
                file_size = os.path.getsize(output_path) / 1024  # KB
                filename = os.path.basename(output_path)
                
                QMessageBox.information(
                    self.main_window,
                    "📋 Informe Generado",
                    f"✅ Informe rápido generado exitosamente\n\n"
                    f"📁 Archivo: {filename}\n"
                    f"📍 Ubicación: metadatos/rapido/reportes/\n"
                    f"📊 Tamaño: {file_size:.1f} KB\n\n"
                    f"📸 Capturas incluidas: {captures_count}\n"
                    f"📐 Layout: 3×2 por página\n"
                    f"📄 Solo imágenes (sin anotaciones)\n\n"
                    f"🎯 ¡Listo para visualizar!"
                )
                
                logger.info(f"✅ Informe rápido generado: {output_path}")
                
            else:
                # ❌ Error en la generación
                QMessageBox.critical(
                    self.main_window,
                    "❌ Error de Generación",
                    "No se pudo generar el informe rápido.\n\n"
                    "Posibles causas:\n"
                    "• Archivos de imagen no encontrados\n"
                    "• Permisos de escritura en carpeta reportes/\n"
                    "• Error en la librería PDF\n\n"
                    "💡 Revisa los logs para más detalles"
                )
                
                logger.error("❌ Error generando informe rápido")
                
        except Exception as e:
            # ❌ Error técnico
            logger.error(f"❌ Error técnico generando informe: {e}")
            QMessageBox.critical(
                self.main_window,
                "❌ Error Técnico",
                f"Error técnico al generar informe:\n\n{str(e)}\n\n"
                "💡 Contacta al soporte técnico si persiste"
            )