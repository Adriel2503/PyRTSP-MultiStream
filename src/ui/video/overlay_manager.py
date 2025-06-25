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
from ...utils.constants import DEFAULT_OVERLAY_ELEMENTS, FORM_FILLED_OVERLAY_ELEMENTS, FORM_DEPENDENT_ELEMENTS
from .cairo import DateTimeRenderer, GridRenderer, TramoRenderer, PozosRenderer, AnnotationRenderer

logger = setup_logger("OverlayManager")

class OverlayManager:
    """Manager que coordina todos los overlays Cairo"""
    
    def __init__(self):
        # Renderers especializados
        self.datetime_renderer = DateTimeRenderer()
        self.grid_renderer = GridRenderer()
        self.tramo_renderer = TramoRenderer()
        self.pozos_renderer = PozosRenderer()
        self.annotation_renderer = AnnotationRenderer()
        
        # Control de visibilidad - usando configuración centralizada
        self.overlay_config = DEFAULT_OVERLAY_ELEMENTS.copy()
        
        # ✅ NUEVA: Configuración dinámica para grid renderer
        self.dynamic_grid_config = {}
        
        # Estado del formulario de inspección
        self.form_filled = False
        
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
            
            # === CAIRO OVERLAY ANOTACIONES ===
            if overlays.get('cairo_annotation'):
                overlays['cairo_annotation'].connect("draw", self._on_cairo_draw_annotation)
                logger.info("✅ Annotation renderer configurado")
                
        except Exception as e:
            logger.error(f"Error configurando overlays: {e}")
    
    # === CALLBACKS DELEGADOS A RENDERERS ===
    
    def _on_cairo_draw_grid(self, element, context, timestamp, duration, user_data=None):
        """Callback delegado al GridRenderer con configuración dinámica"""
        # ✅ NUEVA: Pasar configuración dinámica al grid renderer
        combined_config = self.overlay_config.copy()
        combined_config.update(self.dynamic_grid_config)
        return self.grid_renderer.draw(context, combined_config)
    
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
    
    def _on_cairo_draw_annotation(self, element, context, timestamp, duration, user_data=None):
        """Callback delegado al AnnotationRenderer"""
        return self.annotation_renderer.draw(context, self.overlay_config)
    
    # === MÉTODOS PÚBLICOS ===
    
    def update_config(self, config):
        """Actualizar configuración de visibilidad y estilos"""
        # Actualizar configuración de visibilidad
        self.overlay_config.update(config)
        
        # ✅ NUEVA: Manejar configuración específica de cuadrícula
        if 'grid_color_rgba' in config:
            self.dynamic_grid_config['grid_color_rgba'] = config['grid_color_rgba']
            logger.info(f"Color de cuadrícula actualizado: {config['grid_color_rgba']}")
        
        # Manejar otras configuraciones globales si es necesario
        if 'grid_opacity' in config:
            self.dynamic_grid_config['grid_opacity'] = config['grid_opacity']
            logger.info(f"Opacidad de cuadrícula actualizada: {config['grid_opacity']}")
        
        logger.info(f"Configuración de overlays actualizada: {config}")
        logger.debug(f"Configuración dinámica de grid: {self.dynamic_grid_config}")
    
    def is_form_filled(self):
        """Verificar si el formulario está lleno"""
        return self.form_filled
    
    def enable_form_elements(self):
        """Habilitar elementos dependientes del formulario"""
        logger.info("Habilitando elementos dependientes del formulario")
        
        # Cambiar a configuración con elementos del formulario habilitados
        self.overlay_config.update(FORM_FILLED_OVERLAY_ELEMENTS)
        self.form_filled = True
        
        logger.debug(f"Nueva configuración: {self.overlay_config}")
    
    def update_ref_tramo(self, ref_tramo):
        """Actualizar texto de referencia de tramo"""
        self.ref_tramo_text = ref_tramo
        logger.debug(f"REF. TRAMO actualizado: '{ref_tramo}'")
    
    def update_pozo_inicio(self, pozo_inicio):
        """Actualizar texto de pozo inicio"""
        self.pozo_inicio_text = pozo_inicio
        logger.debug(f"POZO INICIO actualizado: '{pozo_inicio}'")
    
    def update_pozo_fin(self, pozo_fin):
        """Actualizar texto de pozo fin"""
        self.pozo_fin_text = pozo_fin
        logger.debug(f"POZO FIN actualizado: '{pozo_fin}'")
    
    def update_distancia(self, distancia):
        """Actualizar texto de distancia"""
        self.distancia_text = distancia
        logger.debug(f"DISTANCIA actualizada: '{distancia}'")
    
    def get_current_texts(self):
        """Obtener textos actuales de overlays"""
        return {
            'ref_tramo': self.ref_tramo_text,
            'pozo_inicio': self.pozo_inicio_text,
            'pozo_fin': self.pozo_fin_text,
            'distancia': self.distancia_text
        }
    
    def get_available_elements(self):
        """Obtener elementos disponibles según estado del formulario"""
        if self.form_filled:
            return self.overlay_config.keys()
        else:
            # Solo elementos que no dependen del formulario
            return [key for key in self.overlay_config.keys() 
                   if key not in FORM_DEPENDENT_ELEMENTS]
    
    # === MÉTODOS PARA ANOTACIONES ===
    
    def start_annotation(self):
        """Iniciar modo de anotación"""
        self.annotation_renderer.start_annotation()
        logger.info("Modo de anotación iniciado desde overlay manager")
    
    def stop_annotation(self):
        """Detener modo de anotación"""
        self.annotation_renderer.stop_annotation()
        logger.info("Modo de anotación detenido desde overlay manager")
    
    def add_annotation_character(self, char):
        """Agregar carácter a la anotación"""
        self.annotation_renderer.add_character(char)
    
    def remove_annotation_character(self):
        """Eliminar último carácter de la anotación"""
        self.annotation_renderer.remove_character()
    
    def get_annotation_text(self):
        """Obtener texto actual de la anotación"""
        return self.annotation_renderer.get_text()
    
    def is_annotation_active(self):
        """Verificar si la anotación está activa"""
        return self.annotation_renderer.is_annotation_active() 