# Optimizaciones de Renderizado de Alto Impacto

Este documento describe las **3 optimizaciones principales** para mejorar el rendimiento del sistema de renderizado de overlays en Welltep.

## 📊 Contexto Actual

El sistema actual renderiza overlays en cada frame (30 FPS = 30 veces por segundo):

```
Frame Video → [Calcular Grilla] + [Calcular Fecha] + [Calcular Tramo] + [Calcular Pozos] → Composición Final
   ↓             ↓                   ↓                  ↓                   ↓
 Nuevo         MISMO              MISMO              MISMO               MISMO
```

**Problema:** Recalculamos elementos idénticos 29 de cada 30 veces.

---

## 🚀 Optimización #1: Renderizado Condicional de Overlays

### ¿Qué Es?
Solo recalcular un overlay cuando su contenido realmente cambió.

### Implementación Actual (Ineficiente)
```python
# src/ui/video/cairo/grid_renderer.py - Método draw()
def draw(self, context, overlay_config):
    # ❌ SE EJECUTA 30 VECES POR SEGUNDO
    context.set_source_rgba(color...)    # Configurar pincel
    context.set_line_width(2)            # Configurar grosor
    
    # Dibujar 8 líneas de grilla
    for line in lines:
        context.move_to(x1, y1)
        context.line_to(x2, y2)  
        context.stroke()                 # CALCULAR + DIBUJAR cada línea
```

### Implementación Optimizada
```python
class OptimizedGridRenderer:
    def __init__(self):
        self.cached_surface = None
        self.last_config_hash = None
    
    def draw(self, context, overlay_config):
        # ✅ VERIFICAR SI CAMBIÓ CONFIGURACIÓN
        config_hash = self._get_config_hash(overlay_config)
        
        if self.last_config_hash != config_hash:
            # ❌ SOLO cuando cambió: RECALCULAR
            self.cached_surface = self._render_to_surface(overlay_config)
            self.last_config_hash = config_hash
            
        # ✅ SIEMPRE: COMPONER (súper rápido)
        context.set_source_surface(self.cached_surface, 0, 0)
        context.paint()  # Una sola operación de blit
```

### Casos de Aplicación (Modo Inspección Rápida)
| Overlay | Frecuencia de Cambio | Ganancia Esperada | Prioridad |
|---------|---------------------|-------------------|-----------|
| **🎯 Cuadrícula** | Nunca (configuración) | 95% menos cómputo | **ALTA** |
| **🎯 Fecha/Hora** | Cada segundo | 90% menos cómputo | **ALTA** |
| **🎯 Distancia** | Solo al cambiar valor | 99% menos cómputo | **ALTA** |
| **🎯 Anotaciones** | Solo al escribir (cuando activo) | 95% menos cómputo | **ALTA** |
| **Tramo** | Solo al cambiar formulario | 99% menos cómputo | Baja (Modo Pro) |
| **Pozos** | Solo al cambiar formulario | 99% menos cómputo | Baja (Modo Pro) |

> **Nota:** En Modo Inspección Rápida están activos los overlays marcados con 🎯  
> **Anotaciones:** Solo se activan cuando usuario hace clic en botón "anotar"

---

## 🎯 Optimización #2: Dirty Tracking Inteligente

### ¿Qué Es?
Solo actualizar las regiones de pantalla que realmente cambiaron.

### Problema Actual
```python
# El contexto Cairo siempre renderiza toda la superficie
def compose_overlays(video_frame):
    # ❌ TODA LA SUPERFICIE (1280x720 = 921,600 píxeles)
    render_grid_overlay()      # Toda la superficie
    render_datetime_overlay()  # Toda la superficie  
    render_tramo_overlay()     # Toda la superficie
    render_pozos_overlay()     # Toda la superficie
```

### Implementación Optimizada
```python
class DirtyRegionTracker:
    def __init__(self):
        self.dirty_regions = []
        self.overlay_bounds = {}
    
    def mark_dirty(self, overlay_name, x, y, width, height):
        """Marcar región específica como sucia"""
        self.dirty_regions.append({
            'name': overlay_name,
            'bounds': (x, y, width, height),
            'needs_update': True
        })
    
    def render_frame(self, context, overlays):
        """Renderizar solo regiones marcadas como sucias"""
        for region in self.dirty_regions:
            if region['needs_update']:
                # ✅ SOLO RENDERIZAR REGIÓN ESPECÍFICA
                self._render_region_only(context, region)
                region['needs_update'] = False
```

### Ejemplo Práctico
```
Pantalla 1280x720:
┌─────────────────────────────────────┐
│ [Fecha: 200x50]     [Tramo: 150x50] │ ← Solo estas regiones
│                                     │
│                                     │   cuando cambió la fecha
│                                     │
│                                     │
│ [Pozos: 3x(120x50)]                 │
└─────────────────────────────────────┘

❌ Antes: 921,600 píxeles recalculados
✅ Después: 200x50 = 10,000 píxeles (98% menos)
```

---

## ⚡ Optimización #3: Propiedades de VideoSink Optimizadas

### ¿Qué Es?
Configurar GStreamer para máximo rendimiento y mínima latencia.

### Configuración Actual
```python
# src/ui/video/gstreamer_manager.py
def _configure_video_sink(self):
    videosink = self.pipeline.get_by_name("videosink")
    videosink.set_property('force-aspect-ratio', True)
    videosink.set_property('sync', False)
    # ❌ Configuración básica - sin optimizaciones
```

### Configuración Optimizada
```python
def _configure_optimized_video_sink(self):
    videosink = self.pipeline.get_by_name("videosink")
    
    # === REDUCIR LATENCIA ===
    videosink.set_property('max-lateness', 20000000)  # 20ms máximo
    videosink.set_property('qos', True)               # Quality of Service
    videosink.set_property('sync', False)             # No sincronizar con clock
    
    # === OPTIMIZAR MEMORIA ===
    videosink.set_property('enable-last-sample', False)  # No guardar último frame
    videosink.set_property('drop', True)                 # Descartar frames atrasados
    
    # === MEJORAR RENDERIZADO ===
    videosink.set_property('double-buffer', True)        # Double buffering
    videosink.set_property('force-aspect-ratio', True)   # Mantener aspecto
    
    # === THREADING OPTIMIZADO ===
    videosink.set_property('processing-deadline', 15000000)  # 15ms deadline
```

### Propiedades Clave Explicadas

| Propiedad | Valor | Beneficio |
|-----------|-------|-----------|
| `max-lateness` | 20ms | Evita acumular frames atrasados |
| `qos=True` | Activado | GStreamer ajusta automáticamente calidad vs rendimiento |
| `sync=False` | Desactivado | Renderizar tan rápido como sea posible |
| `drop=True` | Activado | Descartar frames si no se puede mantener ritmo |
| `double-buffer` | Activado | Evita parpadeo y mejora fluidez |
| `processing-deadline` | 15ms | Límite de tiempo para procesar cada frame |

---

## 📈 Impacto Esperado

### Rendimiento General
- **CPU Usage**: Reducción del 40-60% en renderizado de overlays
- **Latencia**: Mejora de 15-30ms en pipeline de video
- **Fluidez**: Eliminación de stuttering por frames atrasados
- **Memoria**: Reducción de allocaciones temporales de Cairo

### Por Overlay
| Optimización | Overlay Afectado | Reducción de Cómputo |
|--------------|------------------|---------------------|
| Condicional | Grilla | 95% (solo cambia por configuración) |
| Condicional | Fecha/Hora | 97% (cambia cada segundo) |
| Condicional | Tramo/Pozos | 99% (cambia solo con formulario) |
| Dirty Tracking | Todos | 80-95% (solo regiones afectadas) |
| VideoSink | Pipeline completo | 10-20% (menos overhead) |

---

## 🛠️ Plan de Implementación

### Fase 1: Renderizado Condicional - Modo Rápido (1-2 días)
1. **Crear clase base `CachedRenderer`**
   ```python
   # src/ui/video/cairo/cached_renderer.py
   class CachedRenderer:
       def __init__(self):
           self.cached_surface = None
           self.last_config_hash = None
       
       def draw_cached(self, context, overlay_config):
           # Lógica de caché común
   ```

2. **Migrar renderers prioritarios (Modo Rápido)**
   - **🎯 Día 1:** `GridRenderer` → `CachedGridRenderer` (mayor impacto)
   - **🎯 Día 2:** `DateTimeRenderer` → `CachedDateTimeRenderer`
   - **🎯 Día 3:** `PozosRenderer` → `CachedPozosRenderer` (solo distancia)
   - **🎯 Día 4:** `AnnotationRenderer` → `CachedAnnotationRenderer` (botón anotar)

3. **Migrar renderers para Modo Pro (futuro)**
   - `TramoRenderer` → `CachedTramoRenderer`

### Fase 2: Dirty Tracking (2-3 días)
1. **Implementar `DirtyRegionTracker`**
   ```python
   # src/ui/video/dirty_tracking.py
   class DirtyRegionTracker:
       # Lógica de tracking de regiones
   ```

2. **Integrar con `OverlayManager`**
   ```python
   # src/ui/video/overlay_manager.py
   class OverlayManager:
       def __init__(self):
           self.dirty_tracker = DirtyRegionTracker()
   ```

### Fase 3: VideoSink Optimization (1 día)
1. **Actualizar `_configure_video_sink()`**
   ```python
   # src/ui/video/gstreamer_manager.py
   def _configure_video_sink(self):
       # Aplicar todas las propiedades optimizadas
   ```

2. **Agregar métricas de rendimiento**
   ```python
   # Monitorear impacto de optimizaciones
   ```

---

## 🧪 Testing

### Scripts de Prueba
```bash
# Benchmark antes de optimizaciones
python test_rendering_performance.py --baseline

# Benchmark después de cada fase
python test_rendering_performance.py --phase1
python test_rendering_performance.py --phase2  
python test_rendering_performance.py --phase3
```

### Métricas a Monitorear
- **FPS de renderizado de overlays**
- **Tiempo de composición por frame**
- **Uso de CPU del proceso de video**
- **Latencia end-to-end**
- **Memoria utilizada por Cairo**

---

## 📋 Checklist de Implementación

### Renderizado Condicional
**Prioridad ALTA (Modo Rápido):**
- [ ] Crear `CachedRenderer` base
- [ ] 🎯 Migrar `GridRenderer` (cuadrícula)
- [ ] 🎯 Migrar `DateTimeRenderer` (fecha-hora)
- [ ] 🎯 Migrar `PozosRenderer` (solo distancia)
- [ ] 🎯 Migrar `AnnotationRenderer` (botón anotar)
- [ ] Testing y benchmark de modo rápido

**Prioridad BAJA (Modo Pro futuro):**
- [ ] Migrar `TramoRenderer`
- [ ] Testing unitario completo

### Dirty Tracking  
- [ ] Implementar `DirtyRegionTracker`
- [ ] Calcular bounds de cada overlay
- [ ] Integrar con `OverlayManager`
- [ ] Manejar overlaps de regiones
- [ ] Testing de invalidación correcta
- [ ] Benchmark de impacto

### VideoSink Optimization
- [ ] Agregar propiedades optimizadas
- [ ] Testing de compatibilidad con hardware
- [ ] Validar que no rompe funcionalidad
- [ ] Medir impacto en latencia
- [ ] Documentar configuraciones por GPU

---

## 🔍 Consideraciones Técnicas

### Compatibilidad
- **Cairo**: Todas las optimizaciones compatibles con Cairo 1.14+
- **GStreamer**: Propiedades de VideoSink validadas en 1.18+
- **Hardware**: Testing en Intel/NVIDIA/AMD GPUs

### Fallbacks
- Si falla el caché → Renderizado tradicional
- Si falla dirty tracking → Renderizado completo
- Si fallan propiedades VideoSink → Configuración básica

### Debugging
```python
# Variables de entorno para debugging
WELLTEP_DEBUG_CACHE=1      # Logs de hit/miss de caché
WELLTEP_DEBUG_DIRTY=1      # Logs de regiones sucias
WELLTEP_DEBUG_VIDEOSINK=1  # Logs de propiedades VideoSink
``` 