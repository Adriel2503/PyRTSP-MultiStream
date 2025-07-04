# 📐 Sistema de Coordenadas y Posicionamiento de Overlays

## 🎯 Resumen

Este documento explica el **sistema de coordenadas consistente** para el posicionamiento de overlays en IRIS - WELLTEP. Los overlays se aplican directamente sobre el **frame original de 2560x1440 píxeles** antes del escalado, garantizando precisión y consistencia.

---

## 🏗️ Arquitectura del Sistema

### 📺 **Frame Original**
- **Resolución**: 2560 x 1440 píxeles
- **Origen (0,0)**: Esquina superior izquierda
- **Eje X**: Izquierda → Derecha (0 a 2560px)
- **Eje Y**: Arriba → Abajo (0 a 1440px)

### 🎨 **Pipeline de Overlays**
```bash
Frame Original (2560x1440)
    ↓ Aplicar Overlays (Cairo)
Frame con Overlays (2560x1440)
    ↓ Escalado Automático
Widget Mostrado (1280x720 o personalizado)
```

---

## 📍 Sistema de Coordenadas Fijas

### 🔧 **Principio de Diseño**
Cada overlay usa **coordenadas fijas** tanto en X como en Y para garantizar consistencia:

```python
# Distancias fijas desde los bordes
DISTANCIA_FIJA_BORDE_X = 150px  # Desde borde izquierdo/derecho
DISTANCIA_FIJA_BORDE_Y = 50px   # Desde borde superior

# Posición del rectángulo (box)
box_left = DISTANCIA_FIJA_BORDE_X   # 150px
box_top = DISTANCIA_FIJA_BORDE_Y    # 50px

# Posición del texto (dentro del box)
x_texto = box_left + padding        # 150 + 25 = 175px
y_texto = box_top + padding + text_height  # 50 + 25 + 32 = 107px
```

---

## 📊 Coordenadas de Overlays

### 🔹 **FECHA/HORA (Superior Izquierda)**
```python
# Archivo: src/ui/video/cairo/datetime_renderer.py
DISTANCIA_FIJA_BORDE_X = 150px  # Desde borde izquierdo
DISTANCIA_FIJA_BORDE_Y = 50px   # Desde borde superior

# Coordenadas en frame 2560x1440:
Rectángulo: (150, 50) + dimensiones variables
Texto: (175, 107) - posición fija
```

### 🔹 **REF. TRAMO (Superior Derecha)**
```python
# Archivo: src/ui/video/cairo/tramo_renderer.py
DISTANCIA_FIJA_BORDE_X = 150px  # Desde borde derecho
DISTANCIA_FIJA_BORDE_Y = 50px   # Desde borde superior

# Coordenadas en frame 2560x1440:
box_right = 2560 - 150 = 2410px
Rectángulo: (variable, 50) - crece hacia la izquierda
Texto: (variable + 25, 107) - altura fija
```

### 🔹 **OTROS OVERLAYS**
Todos los overlays siguen el mismo patrón de **coordenadas fijas** para mantener consistencia:

- **POZO INICIO**: Inferior izquierda (150px desde izquierda, distancia fija desde abajo)
- **POZO FIN**: Inferior derecha (150px desde derecha, distancia fija desde abajo)
- **DISTANCIA**: Inferior derecha, encima de POZO FIN
- **GRILLA**: Cubre todo el frame con espaciado regular

---

## 🛠️ Configuración y Personalización

### 📝 **Modificar Posiciones**

Para cambiar la posición de los overlays, modifica las constantes en cada renderer:

```python
# Para mover todos los overlays más cerca/lejos de los bordes
DISTANCIA_FIJA_BORDE_X = 100px  # Era 150px

# Para mover todos los overlays arriba/abajo
DISTANCIA_FIJA_BORDE_Y = 30px   # Era 50px
```

### 📝 **Parámetros de Configuración**

Cada overlay utiliza la configuración de `src/utils/constants.py`:

```python
CAIRO_OVERLAY_CONFIG = {
    'font_family': 'Arial',
    'font_size': 32,                    # Tamaño de fuente
    'font_weight': 'bold',
    'text_color': (1.0, 1.0, 1.0, 1.0),  # Blanco RGBA
    'bg_color': (1.0, 0.65, 0.15, 0.2),  # Naranja transparente
    'padding': 25,                       # Espaciado interno
    'border_radius': 15,                 # Esquinas redondeadas
}
```

---

## 🔄 Escalado Automático

### 📐 **Proporciones en Pantalla**

Las coordenadas absolutas se mantienen como **proporciones** al escalar:

```python
# En frame original 2560x1440:
Fecha X: 150px de 2560px = 5.86% desde izquierda
Fecha Y: 50px de 1440px = 3.47% desde arriba

# En widget escalado 1280x720:
Fecha X: 75px de 1280px = 5.86% desde izquierda (misma proporción)
Fecha Y: 25px de 720px = 3.47% desde arriba (misma proporción)
```

### ✅ **Ventajas del Sistema**
1. **Precisión**: Overlays aplicados en resolución nativa
2. **Escalabilidad**: Proporciones consistentes en cualquier tamaño
3. **Rendimiento**: Aplicado una vez, escalado automáticamente
4. **Mantenibilidad**: Coordenadas fijas y predecibles

---

## 🏗️ Estructura de Archivos

### 📁 **Renderers de Overlays**
```
src/ui/video/cairo/
├── datetime_renderer.py    # Fecha/hora (superior izquierda)
├── tramo_renderer.py      # REF. TRAMO (superior derecha)
├── pozos_renderer.py      # POZO INICIO/FIN (inferior)
├── grid_renderer.py       # Cuadrícula/malla
└── annotation_renderer.py # Anotaciones dinámicas
```

### 📁 **Configuración**
```
src/utils/constants.py     # Configuración de overlays
src/ui/video/overlay_manager.py  # Coordinador de overlays
```

---

## 🔧 Ejemplo de Implementación

### 📝 **Crear un Nuevo Overlay**

1. **Crear el Renderer**:
```python
# src/ui/video/cairo/mi_overlay_renderer.py
class MiOverlayRenderer:
    def draw(self, context, overlay_config):
        # Coordenadas fijas
        DISTANCIA_FIJA_BORDE_X = 150px  # Desde borde
        DISTANCIA_FIJA_BORDE_Y = 50px   # Desde arriba
        
        # Posición del rectángulo
        box_left = DISTANCIA_FIJA_BORDE_X
        box_top = DISTANCIA_FIJA_BORDE_Y
        
        # Posición del texto
        x = box_left + padding
        y = box_top + padding + text_height
        
        # Dibujar rectángulo y texto...
```

2. **Agregar al Pipeline**:
```python
# src/utils/constants.py
GSTREAMER_PIPELINE_TEMPLATE = """
! cairooverlay name=cairo_mi_overlay
"""
```

3. **Registrar en el Manager**:
```python
# src/ui/video/overlay_manager.py
self.mi_overlay_renderer = MiOverlayRenderer()
```

---

## 📊 Tabla de Coordenadas de Referencia

| Overlay | Posición | X (px) | Y (px) | Alineación |
|---------|----------|--------|--------|------------|
| **Fecha/Hora** | Superior Izq. | 150 | 50 | Fijo desde izquierda |
| **REF. Tramo** | Superior Der. | 2410* | 50 | Fijo desde derecha |
| **Pozo Inicio** | Inferior Izq. | 150 | 1340* | Fijo desde izquierda |
| **Pozo Fin** | Inferior Der. | 2410* | 1340* | Fijo desde derecha |
| **Distancia** | Inferior Der. | 2410* | 1220* | Encima de Pozo Fin |

*\* Valores aproximados, dependen del ancho del texto*

---

## 🐛 Solución de Problemas

### ❓ **Overlay no se muestra**
- Verificar que el renderer esté registrado en `overlay_manager.py`
- Comprobar que el `cairooverlay` esté en el pipeline de GStreamer
- Revisar que la función `draw()` retorne `True`

### ❓ **Posición incorrecta**
- Verificar las constantes `DISTANCIA_FIJA_BORDE_X` y `DISTANCIA_FIJA_BORDE_Y`
- Comprobar el cálculo de `x` e `y` para el texto
- Revisar que `box_top` y `box_left` estén correctos

### ❓ **Overlay cortado**
- Verificar que las coordenadas no excedan las dimensiones del frame (2560x1440)
- Comprobar que el `bg_width` y `bg_height` sean apropiados
- Revisar el `padding` y `border_radius`

---

## 📚 Referencias

- **Sistema de Coordenadas Cairo**: [Cairo Graphics Documentation](https://www.cairographics.org/)
- **GStreamer Overlays**: [GStreamer cairooverlay](https://gstreamer.freedesktop.org/documentation/cairo/cairooverlay.html)
- **Configuración del Proyecto**: `src/utils/constants.py`

---

**Autor**: Sistema IRIS - WELLTEP  
**Versión**: 1.0.0  
**Fecha**: Julio 2025  

---

> 💡 **Nota**: Este sistema garantiza que los overlays se mantengan consistentes y profesionales sin importar el tamaño de visualización, ya que se aplican en la resolución nativa del video antes del escalado. 