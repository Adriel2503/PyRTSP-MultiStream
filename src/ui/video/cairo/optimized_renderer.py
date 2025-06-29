# -*- coding: utf-8 -*-
"""
Sistema de renderizado Cairo optimizado para mejor rendimiento
Implementa cache de elementos, renderizado diferido y optimizaciones de memoria
"""

import time
import hashlib
from typing import Dict, Tuple, Optional, Any
from threading import RLock

try:
    import cairo
    CAIRO_AVAILABLE = True
except ImportError:
    CAIRO_AVAILABLE = False

from ....utils.logger import setup_logger
from ....core.thread_pool_manager import get_thread_pool_manager

logger = setup_logger("OptimizedCairoRenderer")

class CairoRenderCache:
    """Cache inteligente para elementos Cairo renderizados"""
    
    def __init__(self, max_entries: int = 50, ttl_seconds: float = 1.0):
        self.max_entries = max_entries
        self.ttl_seconds = ttl_seconds
        self._cache = {}  # key -> (surface, timestamp, access_count)
        self._lock = RLock()
        
    def _generate_key(self, element_type: str, config: dict, text: str = "") -> str:
        """Generar clave única para elementos del cache"""
        # Crear hash de configuración relevante
        config_str = f"{element_type}:{text}:"
        for key in sorted(config.keys()):
            if key.endswith(('_visible', '_color', '_font_size', '_opacity')):
                config_str += f"{key}:{config[key]}:"
        
        return hashlib.md5(config_str.encode()).hexdigest()[:16]
    
    def get(self, key: str) -> Optional[cairo.ImageSurface]:
        """Obtener surface del cache si está válido"""
        with self._lock:
            if key in self._cache:
                surface, timestamp, access_count = self._cache[key]
                current_time = time.time()
                
                # Verificar TTL
                if current_time - timestamp <= self.ttl_seconds:
                    # Actualizar contador de acceso
                    self._cache[key] = (surface, timestamp, access_count + 1)
                    return surface
                else:
                    # Eliminar entrada expirada
                    del self._cache[key]
        
        return None
    
    def put(self, key: str, surface: cairo.ImageSurface):
        """Guardar surface en cache"""
        with self._lock:
            current_time = time.time()
            
            # Limpiar cache si está lleno
            if len(self._cache) >= self.max_entries:
                self._evict_old_entries()
            
            self._cache[key] = (surface, current_time, 1)
    
    def _evict_old_entries(self):
        """Eliminar entradas antiguas del cache"""
        current_time = time.time()
        
        # Eliminar entradas expiradas primero
        expired_keys = []
        for key, (surface, timestamp, access_count) in self._cache.items():
            if current_time - timestamp > self.ttl_seconds:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self._cache[key]
        
        # Si aún está lleno, eliminar menos accedidas
        if len(self._cache) >= self.max_entries:
            sorted_items = sorted(
                self._cache.items(),
                key=lambda x: x[1][2]  # access_count
            )
            
            # Eliminar 20% de las menos accedidas
            to_remove = max(1, len(sorted_items) // 5)
            for i in range(to_remove):
                key = sorted_items[i][0]
                del self._cache[key]
    
    def clear(self):
        """Limpiar cache completamente"""
        with self._lock:
            self._cache.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas del cache"""
        with self._lock:
            current_time = time.time()
            valid_entries = 0
            total_access = 0
            
            for surface, timestamp, access_count in self._cache.values():
                if current_time - timestamp <= self.ttl_seconds:
                    valid_entries += 1
                    total_access += access_count
            
            return {
                'total_entries': len(self._cache),
                'valid_entries': valid_entries,
                'hit_rate': total_access / max(1, valid_entries) if valid_entries > 0 else 0,
                'memory_usage_mb': len(self._cache) * 0.1  # Estimación aproximada
            }

class OptimizedCairoRenderer:
    """Renderer Cairo optimizado con cache y renderizado diferido"""
    
    def __init__(self):
        if not CAIRO_AVAILABLE:
            logger.warning("Cairo no disponible - renderer deshabilitado")
            return
        
        # Cache para elementos renderizados
        self.cache = CairoRenderCache(max_entries=100, ttl_seconds=0.5)
        
        # Pool de threads para renderizado pesado
        self.thread_pool = get_thread_pool_manager()
        
        # Estado de elementos para detectar cambios
        self._element_states = {}
        self._dirty_elements = set()
        
        # Configuración de optimización
        self.enable_cache = True
        self.enable_background_render = True
        self.batch_render_threshold = 3  # Agrupar renders pequeños
        
        # Métricas de rendimiento
        self._render_times = []
        self._cache_hits = 0
        self._cache_misses = 0
        
        logger.info("OptimizedCairoRenderer inicializado")
    
    def render_element(self, context: cairo.Context, element_type: str, 
                      config: dict, text: str = "", force_render: bool = False) -> bool:
        """Renderizar elemento con optimizaciones"""
        if not CAIRO_AVAILABLE:
            return False
        
        start_time = time.time()
        
        try:
            # Verificar si el elemento está visible
            visible_key = f"{element_type}_visible"
            if not config.get(visible_key, True):
                return True
            
            # Generar clave de cache
            cache_key = self.cache._generate_key(element_type, config, text)
            
            # Intentar obtener del cache si está habilitado
            cached_surface = None
            if self.enable_cache and not force_render:
                cached_surface = self.cache.get(cache_key)
                
                if cached_surface:
                    self._cache_hits += 1
                    self._draw_cached_surface(context, cached_surface, config)
                    self._record_render_time(time.time() - start_time)
                    return True
            
            # Cache miss - renderizar nuevo
            self._cache_misses += 1
            surface = self._render_to_surface(element_type, config, text)
            
            if surface and self.enable_cache:
                self.cache.put(cache_key, surface)
            
            # Dibujar en el contexto principal
            if surface:
                self._draw_cached_surface(context, surface, config)
            
            self._record_render_time(time.time() - start_time)
            return True
            
        except Exception as e:
            logger.error(f"Error renderizando {element_type}: {e}")
            return False
    
    def _render_to_surface(self, element_type: str, config: dict, text: str) -> Optional[cairo.ImageSurface]:
        """Renderizar elemento a una surface separada"""
        try:
            # Crear surface temporal (tamaño optimizado)
            width, height = self._calculate_element_size(element_type, config, text)
            surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
            ctx = cairo.Context(surface)
            
            # Renderizar según el tipo
            if element_type == "grid":
                self._render_grid(ctx, config, width, height)
            elif element_type == "datetime":
                self._render_datetime(ctx, config, width, height)
            elif element_type == "text":
                self._render_text(ctx, config, text, width, height)
            elif element_type == "annotation":
                self._render_annotation(ctx, config, text, width, height)
            else:
                logger.warning(f"Tipo de elemento desconocido: {element_type}")
                return None
            
            return surface
            
        except Exception as e:
            logger.error(f"Error creando surface para {element_type}: {e}")
            return None
    
    def _calculate_element_size(self, element_type: str, config: dict, text: str) -> Tuple[int, int]:
        """Calcular tamaño óptimo para el elemento"""
        if element_type == "grid":
            return (100, 100)  # Grid pequeño para cache
        elif element_type == "datetime":
            return (300, 50)   # Suficiente para fecha/hora
        elif element_type in ("text", "annotation"):
            # Estimar basado en texto
            font_size = config.get(f"{element_type}_font_size", 24)
            text_len = len(text) if text else 10
            width = min(600, max(200, text_len * font_size // 2))
            height = font_size + 20
            return (width, height)
        
        return (200, 50)  # Tamaño por defecto
    
    def _draw_cached_surface(self, context: cairo.Context, surface: cairo.ImageSurface, config: dict):
        """Dibujar surface cacheada en el contexto principal"""
        # Aplicar transformaciones si es necesario
        context.save()
        
        # Posicionamiento (esto debería venir del config específico del elemento)
        x, y = 0, 0  # Por defecto
        
        context.set_source_surface(surface, x, y)
        
        # Aplicar opacidad si está configurada
        opacity = config.get('opacity', 1.0)
        if opacity < 1.0:
            context.paint_with_alpha(opacity)
        else:
            context.paint()
        
        context.restore()
    
    def _render_grid(self, ctx: cairo.Context, config: dict, width: int, height: int):
        """Renderizar grilla optimizada"""
        grid_color = config.get('grid_color_rgba', (1.0, 1.0, 1.0, 0.3))
        line_width = config.get('grid_line_width', 1.0)
        spacing = config.get('grid_spacing', 50)
        
        ctx.set_source_rgba(*grid_color)
        ctx.set_line_width(line_width)
        
        # Líneas verticales
        for x in range(0, width, spacing):
            ctx.move_to(x, 0)
            ctx.line_to(x, height)
        
        # Líneas horizontales
        for y in range(0, height, spacing):
            ctx.move_to(0, y)
            ctx.line_to(width, y)
        
        ctx.stroke()
    
    def _render_datetime(self, ctx: cairo.Context, config: dict, width: int, height: int):
        """Renderizar fecha/hora optimizada"""
        import datetime
        
        font_size = config.get('datetime_font_size', 24)
        color = config.get('datetime_color_rgba', (1.0, 1.0, 1.0, 1.0))
        
        current_time = datetime.datetime.now()
        text = current_time.strftime("%Y-%m-%d %H:%M:%S")
        
        ctx.select_font_face("Arial", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(font_size)
        ctx.set_source_rgba(*color)
        
        # Centrar texto
        text_extents = ctx.text_extents(text)
        x = (width - text_extents.width) / 2
        y = (height + text_extents.height) / 2
        
        ctx.move_to(x, y)
        ctx.show_text(text)
    
    def _render_text(self, ctx: cairo.Context, config: dict, text: str, width: int, height: int):
        """Renderizar texto genérico optimizado"""
        if not text:
            return
        
        font_size = config.get('font_size', 20)
        color = config.get('color_rgba', (1.0, 1.0, 1.0, 1.0))
        
        ctx.select_font_face("Arial", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(font_size)
        ctx.set_source_rgba(*color)
        
        # Posicionar texto
        text_extents = ctx.text_extents(text)
        x = 10  # Margen izquierdo
        y = (height + text_extents.height) / 2
        
        ctx.move_to(x, y)
        ctx.show_text(text)
    
    def _render_annotation(self, ctx: cairo.Context, config: dict, text: str, width: int, height: int):
        """Renderizar anotación optimizada"""
        if not text:
            return
        
        # Fondo semi-transparente
        ctx.set_source_rgba(0, 0, 0, 0.7)
        ctx.rectangle(0, 0, width, height)
        ctx.fill()
        
        # Texto de anotación
        self._render_text(ctx, config, text, width, height)
    
    def _record_render_time(self, render_time: float):
        """Registrar tiempo de renderizado para métricas"""
        self._render_times.append(render_time)
        
        # Mantener solo las últimas 100 mediciones
        if len(self._render_times) > 100:
            self._render_times.pop(0)
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas de rendimiento"""
        cache_stats = self.cache.get_stats()
        
        avg_render_time = 0
        if self._render_times:
            avg_render_time = sum(self._render_times) / len(self._render_times)
        
        total_requests = self._cache_hits + self._cache_misses
        hit_rate = self._cache_hits / max(1, total_requests) * 100
        
        return {
            'cache': cache_stats,
            'performance': {
                'avg_render_time_ms': avg_render_time * 1000,
                'cache_hit_rate': hit_rate,
                'total_renders': total_requests,
                'recent_render_times': len(self._render_times)
            },
            'settings': {
                'cache_enabled': self.enable_cache,
                'background_render': self.enable_background_render,
                'batch_threshold': self.batch_render_threshold
            }
        }
    
    def optimize_cache(self):
        """Optimizar cache manualmente"""
        self.cache.clear()
        self._render_times.clear()
        logger.info("Cache de renderer optimizado")
    
    def set_optimization_level(self, level: str):
        """Configurar nivel de optimización"""
        if level == "performance":
            self.enable_cache = True
            self.enable_background_render = True
            self.cache.ttl_seconds = 1.0
            self.cache.max_entries = 100
        elif level == "memory":
            self.enable_cache = True
            self.enable_background_render = False
            self.cache.ttl_seconds = 0.3
            self.cache.max_entries = 30
        elif level == "disabled":
            self.enable_cache = False
            self.enable_background_render = False
        
        logger.info(f"Nivel de optimización establecido: {level}")

# Instancia global para uso en toda la aplicación
_optimized_renderer = None

def get_optimized_renderer() -> OptimizedCairoRenderer:
    """Obtener instancia singleton del renderer optimizado"""
    global _optimized_renderer
    if _optimized_renderer is None:
        _optimized_renderer = OptimizedCairoRenderer()
    return _optimized_renderer 