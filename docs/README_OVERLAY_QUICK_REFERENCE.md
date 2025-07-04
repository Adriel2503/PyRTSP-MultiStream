# 🚀 Guía Rápida: Overlays IRIS - WELLTEP

## 📋 Resumen Ejecutivo

**Sistema de overlays** para video 2560x1440 con **coordenadas fijas** y escalado automático.

---

## 📐 Coordenadas Base

```python
# Constantes principales
FRAME_ORIGINAL = (2560, 1440)      # Resolución nativa
DISTANCIA_BORDE_X = 150px          # Margen horizontal
DISTANCIA_BORDE_Y = 50px           # Margen vertical
PADDING_INTERNO = 25px             # Espaciado texto
FONT_SIZE = 32px                   # Tamaño fuente
```

---

## 🎯 Posiciones de Overlays

| Overlay | X | Y | Archivo |
|---------|---|---|---------|
| **Fecha/Hora** | 150px | 50px | `datetime_renderer.py` |
| **REF. Tramo** | 2410px* | 50px | `tramo_renderer.py` |
| **Pozo Inicio** | 150px | 1340px* | `pozos_renderer.py` |
| **Pozo Fin** | 2410px* | 1340px* | `pozos_renderer.py` |
| **Distancia** | 2410px* | 1220px* | `pozos_renderer.py` |

*\* Variables según ancho del texto*

---

## 🔧 Modificar Posiciones

### Cambiar Margen Horizontal
```python
# En cada renderer (datetime_renderer.py, tramo_renderer.py, etc.)
DISTANCIA_FIJA_BORDE_X = 100px  # Era 150px
```

### Cambiar Margen Vertical
```python
# En cada renderer
DISTANCIA_FIJA_BORDE_Y = 30px   # Era 50px
```

### Cambiar Tamaño de Fuente
```python
# En src/utils/constants.py
CAIRO_OVERLAY_CONFIG = {
    'font_size': 28,  # Era 32
}
```

---

## 📁 Archivos Clave

```
src/ui/video/cairo/
├── datetime_renderer.py     # Fecha/hora
├── tramo_renderer.py       # REF. Tramo  
├── pozos_renderer.py       # Pozos + Distancia
├── grid_renderer.py        # Cuadrícula
└── annotation_renderer.py  # Anotaciones

src/utils/constants.py      # Configuración global
src/ui/video/overlay_manager.py  # Coordinador
```

---

## ⚡ Comandos Rápidos

### Crear Nuevo Overlay
1. Copiar `datetime_renderer.py` → `mi_overlay_renderer.py`
2. Cambiar coordenadas `DISTANCIA_FIJA_BORDE_X/Y`
3. Agregar `! cairooverlay name=cairo_mi_overlay` al pipeline
4. Registrar en `overlay_manager.py`

### Debug Posiciones
```python
logger.info(f"box_left: {box_left}, box_top: {box_top}")
logger.info(f"x_texto: {x}, y_texto: {y}")
```

### Verificar Frame Size
```python
surface = context.get_target()
width = surface.get_width()   # Debe ser 2560
height = surface.get_height() # Debe ser 1440
```

---

## 🐛 Problemas Comunes

| Problema | Solución |
|----------|----------|
| Overlay no aparece | Verificar `return True` en `draw()` |
| Posición incorrecta | Revisar `DISTANCIA_FIJA_BORDE_X/Y` |
| Texto cortado | Ajustar `padding` o reducir `font_size` |
| Overlay fuera de pantalla | Coordenadas > 2560x1440 |

---

## 📊 Proporciones de Referencia

```python
# Para mantener proporciones visuales:
Margen horizontal: 150/2560 = 5.86%
Margen vertical: 50/1440 = 3.47%

# Escalado automático a 1280x720:
X escalado = 150 * (1280/2560) = 75px
Y escalado = 50 * (720/1440) = 25px
```

---

**Última actualización**: Julio 2025  
**Documentación completa**: `README_OVERLAY_POSITIONING.md` 