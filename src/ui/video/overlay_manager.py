# -*- coding: utf-8 -*-
"""
Manager de overlays que coordina todos los renderers Cairo
Gestiona configuración, visibilidad y actualizaciones de texto
"""

try:
    import cairo
    CAIRO_AVAILABLE = True
except ImportError:
    CAIRO_AVAILABLE = False

from ...utils.logger import setup_logger
from .cairo import DateTimeRenderer, GridRenderer, TramoRenderer, PozosRenderer

logger = setup_logger("OverlayManager")

class OverlayManager:
    """Manager que coordina todos los overlays Cairo"""
    
    def __init__(self):
        # Renderers especializados
        self.datetime_renderer = DateTimeRenderer()
        self.grid_renderer = GridRenderer()
        self.tramo_renderer = TramoRenderer()
        self.pozos_renderer = PozosRenderer()
        
        # Control de visibilidad (por defecto todos activos)
        self.overlay_config = {
            'grid_enabled': True,
            'fecha_enabled': True,
            'tramo_enabled': True,
            'pozo_inicial_enabled': True,
            'distancia_enabled': True,
            'pozo_final_enabled': True
        }
        
        # Variables para textos dinámicos
        self.ref_tramo_text = ""
        self.pozo_inicio_text = ""
        self.pozo_fin_text = ""
        self.distancia_text = "0.0 m"
        
        logger.info("OverlayManager inicializado con renderers modulares")
    
    def configure_pipeline_overlays(self, overlays):
        """Configurar overlays del pipeline con callbacks"""
        if not CAIRO_AVAILABLE:
            logger.warning("Cairo no disponible - overlays deshabilitados")
            return
        
        try:
            # === CAIRO OVERLAY MALLA/GRILLA ===
            if overlays.get('cairo_grid'):
                overlays['cairo_grid'].connect("draw", self._on_cairo_draw_grid)
                logger.info("✅ Grid renderer configurado")
            
            # === CAIRO OVERLAY FECHA/HORA ===
            if overlays.get('cairo_datetime'):
                overlays['cairo_datetime'].connect("draw", self._on_cairo_draw_datetime)
                logger.info("✅ DateTime renderer configurado")
            
            # === CAIRO OVERLAY REF. TRAMO ===
            if overlays.get('cairo_ref_tramo'):
                overlays['cairo_ref_tramo'].connect("draw", self._on_cairo_draw_ref_tramo)
                logger.info("✅ Tramo renderer configurado")
            
            # === CAIRO OVERLAY POZOS Y DISTANCIA ===
            if overlays.get('cairo_pozo_inicio'):
                overlays['cairo_pozo_inicio'].connect("draw", self._on_cairo_draw_pozo_inicio)
                logger.info("✅ Pozo inicio renderer configurado")
            
            if overlays.get('cairo_distancia'):
                overlays['cairo_distancia'].connect("draw", self._on_cairo_draw_distancia)
                logger.info("✅ Distancia renderer configurado")
            
            if overlays.get('cairo_pozo_fin'):
                overlays['cairo_pozo_fin'].connect("draw", self._on_cairo_draw_pozo_fin)
                logger.info("✅ Pozo fin renderer configurado")
                
        except Exception as e:
            logger.error(f"Error configurando overlays: {e}")
    
    # === CALLBACKS DELEGADOS A RENDERERS ===
    
    def _on_cairo_draw_grid(self, element, context, timestamp, duration, user_data=None):
        """Callback delegado al GridRenderer"""
        return self.grid_renderer.draw(context, self.overlay_config)
    
    def _on_cairo_draw_datetime(self, element, context, timestamp, duration, user_data=None):
        """Callback delegado al DateTimeRenderer"""
        return self.datetime_renderer.draw(context, self.overlay_config)
    
    def _on_cairo_draw_ref_tramo(self, element, context, timestamp, duration, user_data=None):
        """Callback delegado al TramoRenderer"""
        return self.tramo_renderer.draw(context, self.overlay_config, self.ref_tramo_text)
    
    def _on_cairo_draw_pozo_inicio(self, element, context, timestamp, duration, user_data=None):
        """Callback delegado al PozosRenderer - pozo inicio"""
        return self.pozos_renderer.draw_pozo_inicio(context, self.overlay_config, self.pozo_inicio_text)
    
    def _on_cairo_draw_distancia(self, element, context, timestamp, duration, user_data=None):
        """Callback delegado al PozosRenderer - distancia"""
        return self.pozos_renderer.draw_distancia(context, self.overlay_config, self.distancia_text)
    
    def _on_cairo_draw_pozo_fin(self, element, context, timestamp, duration, user_data=None):
        """Callback delegado al PozosRenderer - pozo fin"""
        return self.pozos_renderer.draw_pozo_fin(context, self.overlay_config, self.pozo_fin_text)
    
    # === MÉTODOS PÚBLICOS ===
    
    def update_config(self, config):
        """Actualizar configuración de visibilidad"""
        self.overlay_config.update(config)
        logger.info(f"Configuración de overlays actualizada: {config}")
    
    def update_ref_tramo(self, ref_tramo):
        """Actualizar texto de REF. TRAMO"""
        self.ref_tramo_text = ref_tramo if ref_tramo else ""
        logger.info(f"✅ REF. TRAMO actualizado: '{self.ref_tramo_text}'")
    
    def update_pozo_inicio(self, pozo_inicio):
        """Actualizar texto de POZO INICIO"""
        self.pozo_inicio_text = pozo_inicio if pozo_inicio else ""
        logger.info(f"✅ POZO INICIO actualizado: '{self.pozo_inicio_text}'")
    
    def update_pozo_fin(self, pozo_fin):
        """Actualizar texto de POZO FIN"""
        self.pozo_fin_text = pozo_fin if pozo_fin else ""
        logger.info(f"✅ POZO FIN actualizado: '{self.pozo_fin_text}'")
    
    def update_distancia(self, distancia):
        """Actualizar texto de DISTANCIA"""
        self.distancia_text = distancia if distancia else "0.0 m"
        logger.info(f"✅ DISTANCIA actualizada: '{self.distancia_text}'") 