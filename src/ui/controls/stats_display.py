# -*- coding: utf-8 -*-
"""
Display de estadísticas en tiempo real
Extraído de main_window.py para mejor modularización
"""

from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import QTimer

from ...utils.constants import (
    DEFAULT_STATS_UPDATE_INTERVAL,
    STATS_LABEL_STYLE_TEMPLATE,
    LATENCY_COLOR_EXCELLENT,
    LATENCY_COLOR_GOOD,
    LATENCY_COLOR_POOR,
    LATENCY_THRESHOLD_EXCELLENT,
    LATENCY_THRESHOLD_GOOD,
    STATUS_MESSAGES
)
from ...utils.logger import setup_logger

logger = setup_logger("StatsDisplay")

class StatsDisplay(QLabel):
    """Widget para mostrar estadísticas de streaming en tiempo real"""
    
    def __init__(self):
        super().__init__()
        self.stats_timer = None
        self.video_widget = None
        self.setup_ui()
        logger.info("StatsDisplay inicializado")
    
    def setup_ui(self):
        """Configurar interfaz del display de estadísticas"""
        self.setText(STATUS_MESSAGES['waiting'])
        self.setStyleSheet(STATS_LABEL_STYLE_TEMPLATE.format(color=LATENCY_COLOR_EXCELLENT))
        self.setMaximumHeight(40)
    
    def set_video_widget(self, video_widget):
        """Establecer widget de video para obtener métricas"""
        self.video_widget = video_widget
        logger.debug("Video widget establecido para monitoreo de estadísticas")
    
    def start_monitoring(self):
        """Iniciar monitoreo de estadísticas en tiempo real"""
        if not self.video_widget:
            logger.warning("No se puede iniciar monitoreo: video widget no establecido")
            return
        
        self.stats_timer = QTimer()
        self.stats_timer.timeout.connect(self.update_stats)
        self.stats_timer.start(DEFAULT_STATS_UPDATE_INTERVAL)
        logger.debug("Monitoreo de estadísticas iniciado")
    
    def stop_monitoring(self):
        """Detener monitoreo de estadísticas"""
        if self.stats_timer:
            self.stats_timer.stop()
            self.stats_timer = None
        self.setText(STATUS_MESSAGES['waiting'])
        logger.debug("Monitoreo de estadísticas detenido")
    
    def update_stats(self):
        """Actualizar estadísticas en tiempo real"""
        if not self.video_widget:
            return
        
        try:
            metrics = self.video_widget.get_metrics()
            if not metrics:
                return
            
            # Obtener todas las métricas
            fps = metrics.get_fps()
            bitrate_kbps = metrics.get_bitrate_kbps()
            bitrate_mbps = metrics.get_bitrate_mbps()
            data_rate_kbps = metrics.get_data_rate_kbps()
            latency = metrics.get_estimated_latency_ms()
            frames = metrics.frame_count
            data_mb = metrics.get_total_mb_received()
            window_info = metrics.get_window_info()
            
            # Formatear display de bitrate
            if bitrate_mbps >= 1.0:
                bitrate_display = f"{bitrate_mbps:.2f} Mbps"
            else:
                bitrate_display = f"{bitrate_kbps:.0f} Kbps"
            
            # Crear texto de estadísticas
            stats_text = (
                f"📊 FPS: {fps:.1f} | "
                f"📡 {bitrate_display} | "
                f"💾 {data_rate_kbps:.0f} KBps | "
                f"⚡ ~{latency:.0f}ms | "
                f"🎬 {frames} frames | "
                f"📦 {data_mb:.1f} MB | "
                f"🔄 {window_info['packets_in_window']}buf/5s"
            )
            
            # Determinar color según latencia
            if latency < LATENCY_THRESHOLD_EXCELLENT:
                color = LATENCY_COLOR_EXCELLENT
            elif latency < LATENCY_THRESHOLD_GOOD:
                color = LATENCY_COLOR_GOOD
            else:
                color = LATENCY_COLOR_POOR
            
            # Actualizar estilo con color dinámico
            self.setStyleSheet(STATS_LABEL_STYLE_TEMPLATE.format(color=color))
            self.setText(stats_text)
            
        except Exception as e:
            logger.error(f"Error actualizando estadísticas: {e}")
            self.setText("❌ Error en estadísticas")
    
    def is_monitoring(self):
        """Verificar si el monitoreo está activo"""
        return self.stats_timer is not None and self.stats_timer.isActive() 