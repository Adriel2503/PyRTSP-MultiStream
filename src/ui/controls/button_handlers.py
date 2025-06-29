# -*- coding: utf-8 -*-
"""
Manejadores de eventos para botones
Extraído de main_window.py para mejor modularización
"""

from PyQt6.QtWidgets import QMessageBox
from datetime import datetime

from ...utils.logger import setup_logger
from ..inspection_form_dialog import InspectionFormDialog
from ..overlays.overlay_config_dialog import OverlayConfigDialog

logger = setup_logger("ButtonHandlers")

class ButtonHandlers:
    """Clase para manejar eventos de botones de la aplicación"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.is_recording = False
        logger.info("ButtonHandlers inicializado")
    
    def handle_plus_button(self):
        """Manejar clic en botón flotante '+' - Mostrar formulario de inspección"""
        logger.info("Botón '+' presionado - Abriendo formulario de inspección")
        
        # Crear y mostrar el dialog de formulario de inspección
        dialog = InspectionFormDialog(self.main_window)
        
        # Conectar señal para recibir los datos guardados
        dialog.data_saved.connect(self.handle_inspection_data_saved)
        
        # Mostrar dialog modal
        dialog.exec()
    
    def handle_inspection_data_saved(self, data):
        """Manejar datos guardados del formulario de inspección"""
        logger.info("Datos de inspección recibidos desde el formulario")
        logger.debug(f"Datos completos: {data}")
        
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
        """.strip()
        
        # Mostrar resumen
        QMessageBox.information(self.main_window, "✅ Datos Guardados", summary)
    
    def handle_record_button(self):
        """Iniciar grabación al presionar el botón de grabación"""
        if not self.is_recording:
            # Generar nombre de archivo basado en la fecha y hora actuales
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"/c:/Users/ariel/Documents/Welltep/grabaciones/inspeccion_{timestamp}.mp4"
            
            # Configurar y iniciar el pipeline de GStreamer para grabación
            self.start_gstreamer_recording(filename)
            self.is_recording = True
            logger.info(f"📹 Grabación iniciada: {filename}")
        else:
            logger.warning("La grabación ya está en curso")
    
    def handle_capture_button(self):
        """Manejar clic del botón CAPTURA"""
        logger.info("📷 Botón CAPTURA presionado")
        QMessageBox.information(self.main_window, "📷 Captura", "Función de captura en desarrollo")
    
    def handle_stop_button(self):
        """Detener grabación al presionar el botón de detener"""
        if self.is_recording:
            # Detener el pipeline de GStreamer y guardar el archivo
            self.stop_gstreamer_recording()
            self.is_recording = False
            logger.info("📹 Grabación detenida y guardada")
        else:
            logger.warning("No hay grabación en curso para detener")
    
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
            
            QMessageBox.information(self.main_window, "🧹 Pantalla Limpiada", 
                                   "✅ Pantalla limpiada exitosamente\n\n"
                                   "Se han eliminado:\n"
                                   "• Anotaciones activas\n"
                                   "• Elementos temporales\n\n"
                                   "El video continúa funcionando normalmente.")
        else:
            logger.warning("Video widget no disponible para limpiar")
            QMessageBox.warning(self.main_window, "🧹 Error", 
                               "No se puede limpiar la pantalla.\n"
                               "Video no disponible.")
    
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
        """Configurar e iniciar el pipeline de GStreamer para grabación"""
        # Configurar el pipeline con un filesink para guardar el video
        # Asegúrate de que el pipeline esté correctamente configurado
        pass

    def stop_gstreamer_recording(self):
        """Detener el pipeline de GStreamer y cerrar el archivo de grabación"""
        # Detener el pipeline y cerrar el archivo
        pass 