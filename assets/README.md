# 📁 Assets - Recursos del Proyecto

Esta carpeta contiene todos los recursos estáticos de PyRTSP-FastStream.

## 📂 Estructura

```
assets/
├── 📁 images/              # Imágenes y logos
│   ├── Logo.png           # Logo principal de la aplicación
│   ├── icon.png           # Icono de la aplicación (opcional)
│   └── background.jpg     # Imagen de fondo (opcional)
├── 📁 icons/              # Iconos SVG/PNG
│   ├── connect.svg
│   ├── disconnect.svg
│   └── settings.svg
└── 📁 fonts/              # Fuentes personalizadas
    └── custom.ttf
```

## 🖼️ Logos Soportados

La aplicación buscará automáticamente el logo en estas ubicaciones (en orden):

1. `assets/images/Logo.png` ← **📍 UBICACIÓN RECOMENDADA**
2. `assets/Logo.png`
3. `Logo.png` (raíz del proyecto)
4. `../Logo.png`

## 📏 Especificaciones Recomendadas

### Logo Principal (`Logo.png`)
- **Formato:** PNG con transparencia
- **Resolución:** 600x400 píxeles (3:2 ratio)
- **Tamaño:** < 2MB
- **Estilo:** Fondo transparente para mejor integración

### Icono de Aplicación (`icon.png`)
- **Formato:** PNG o ICO
- **Resolución:** 256x256 píxeles
- **Tamaño:** < 500KB

## 🎨 Notas de Diseño

- Los colores principales de la interfaz son:
  - **Primario:** #FFA726 (Naranja)
  - **Secundario:** #FFB74D (Naranja claro)
  - **Oscuro:** #1a1a1a
  - **Texto:** #495057

- El logo debe contrastar bien con fondos oscuros
- Se recomienda usar el logo en formato horizontal para mejor visualización 