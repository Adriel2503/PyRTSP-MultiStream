# -*- coding: utf-8 -*-
"""
Generador de informes para MODO RÁPIDO
Layout 3x2 (6 imágenes por página) - Solo imágenes, sin anotaciones adicionales
"""

import os
from datetime import datetime
from typing import List, Optional
from fpdf import FPDF

from .logger import setup_logger

logger = setup_logger("RapidReportGenerator")

class RapidReportGenerator:
    """Generador de PDF para modo RÁPIDO - Layout 3x2"""
    
    def __init__(self, path_manager, session_manager):
        self.path_manager = path_manager
        self.session_manager = session_manager
        
        # Configuración del PDF - Optimizada para capturas 2560x1440
        self.pdf = None
        # Calculado para imágenes 2560x1440: ÷20 = 128x72mm base
        # Ajustado para que quepan 2 columnas en A4
        self.max_img_width = 90   # mm - más ancho para 16:9
        self.max_img_height = 75  # mm - más alto para mejor visualización  
        self.margin_x = 12        # mm - márgenes más pequeños
        self.margin_y = 15        # mm - márgenes más pequeños
        self.spacing = 8          # mm - spacing más compacto
        
        logger.info("RapidReportGenerator inicializado")
    
    def generate_report(self) -> Optional[str]:
        """Generar informe rápido completo"""
        try:
            # 1. Obtener datos de la sesión actual
            session_data = self.session_manager.get_current_session_info()
            if not session_data:
                logger.error("No hay sesión activa")
                return None
            
            # 2. Obtener lista de capturas de esta sesión
            captures_list = session_data["files_generated"]["captures"]
            if not captures_list:
                logger.warning("No hay capturas en la sesión")
                return None
            
            # 3. Obtener rutas completas de las imágenes
            image_paths = self._get_image_paths(captures_list)
            if not image_paths:
                logger.error("No se encontraron archivos de imagen")
                return None
            
            # 4. Crear PDF
            self.pdf = FPDF(orientation='P', unit='mm', format='A4')
            self.pdf.set_auto_page_break(auto=False)  # Control manual de páginas
            
            # 5. Generar portada
            self._add_cover_page(session_data)
            
            # 6. Agregar páginas de imágenes (6 por página)
            self._add_image_pages(image_paths)
            
            # 7. Guardar PDF
            output_path = self._save_pdf(session_data)
            
            logger.info(f"✅ Informe rápido generado: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"❌ Error generando informe rápido: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _get_image_paths(self, captures_list: List[str]) -> List[str]:
        """Obtener rutas completas de las imágenes que existen"""
        image_paths = []
        
        for capture_name in captures_list:
            # Construir ruta completa
            full_path = self.path_manager.get_capture_path(capture_name)
            
            if os.path.exists(full_path):
                image_paths.append(full_path)
                logger.debug(f"✅ Imagen encontrada: {capture_name}")
            else:
                logger.warning(f"⚠️ Imagen no encontrada: {full_path}")
        
        # Ordenar por nombre (cronológicamente)
        image_paths.sort()
        logger.info(f"📸 {len(image_paths)} imágenes disponibles para el informe")
        
        return image_paths
    
    def _add_cover_page(self, session_data: dict):
        """Agregar portada con datos automáticos"""
        self.pdf.add_page()
        
        # Título principal
        self.pdf.set_font('Arial', 'B', 24)
        self.pdf.cell(0, 30, 'REGISTRO RAPIDO', 0, 1, 'C')
        
        # Espaciado
        self.pdf.ln(10)
        
        # Información básica
        self.pdf.set_font('Arial', '', 14)
        
        # Fecha
        start_time = session_data.get('start_time', '')
        if start_time:
            fecha = datetime.fromisoformat(start_time).strftime('%d/%m/%Y %H:%M')
            self.pdf.cell(0, 10, f'Fecha: {fecha}', 0, 1)
        
        # Modo
        self.pdf.cell(0, 10, 'Modo: RAPIDO', 0, 1)
        
        # Sesión ID
        session_id = session_data.get('session_id', '')
        self.pdf.cell(0, 10, f'Sesion: {session_id}', 0, 1)
        
        self.pdf.ln(5)
        
        # Estadísticas
        stats = session_data.get('session_stats', {})
        captures_count = stats.get('captures_count', 0)
        duration = stats.get('duration_seconds', 0)
        
        self.pdf.cell(0, 10, f'Capturas: {captures_count}', 0, 1)
        
        if duration > 0:
            duration_min = int(duration / 60)
            self.pdf.cell(0, 10, f'Duracion: {duration_min} minutos', 0, 1)
        
        # Archivo de video
        recordings = session_data.get('files_generated', {}).get('recordings', [])
        if recordings:
            self.pdf.ln(5)
            self.pdf.cell(0, 10, 'Archivo de video:', 0, 1)
            self.pdf.set_font('Arial', '', 12)
            self.pdf.cell(0, 8, f'    {recordings[0]}', 0, 1)
    
    def _add_image_pages(self, image_paths: List[str]):
        """Agregar páginas con imágenes en layout 3x2"""
        
        # Procesar de 6 en 6
        for i in range(0, len(image_paths), 6):
            page_images = image_paths[i:i+6]
            self._add_single_image_page(page_images)
    
    def _add_single_image_page(self, images: List[str]):
        """Agregar una página con hasta 6 imágenes en layout 3x2"""
        self.pdf.add_page()
        
        # Posiciones para layout 3x2
        # Fila 1: (x1,y1), (x2,y1)
        # Fila 2: (x1,y2), (x2,y2)  
        # Fila 3: (x1,y3), (x2,y3)
        
        x1 = self.margin_x
        x2 = self.margin_x + self.max_img_width + self.spacing
        
        y1 = self.margin_y
        y2 = self.margin_y + self.max_img_height + self.spacing
        y3 = self.margin_y + 2 * (self.max_img_height + self.spacing)
        
        positions = [
            (x1, y1),  # Imagen 1 - Fila 1, Col 1
            (x2, y1),  # Imagen 2 - Fila 1, Col 2
            (x1, y2),  # Imagen 3 - Fila 2, Col 1
            (x2, y2),  # Imagen 4 - Fila 2, Col 2
            (x1, y3),  # Imagen 5 - Fila 3, Col 1
            (x2, y3),  # Imagen 6 - Fila 3, Col 2
        ]
        
        # Colocar imágenes
        for i, img_path in enumerate(images):
            if i < len(positions):
                x, y = positions[i]
                try:
                    # Verificar que el archivo existe
                    if os.path.exists(img_path):
                        # Calcular dimensiones preservando aspect ratio
                        img_width, img_height, offset_x, offset_y = self._calculate_image_dimensions(img_path)
                        
                        # Centrar imagen en el espacio asignado
                        final_x = x + offset_x
                        final_y = y + offset_y
                        
                        self.pdf.image(img_path, final_x, final_y, img_width, img_height)
                        logger.debug(f"✅ Imagen añadida: {os.path.basename(img_path)} - {img_width:.1f}x{img_height:.1f}mm en ({final_x:.1f},{final_y:.1f})")
                    else:
                        logger.warning(f"⚠️ Imagen no encontrada para PDF: {img_path}")
                except Exception as e:
                    logger.error(f"❌ Error añadiendo imagen {img_path}: {e}")
    
    def _save_pdf(self, session_data: dict) -> str:
        """Guardar PDF en la carpeta de reportes del modo rápido"""
        
        # Generar nombre de archivo
        session_id = session_data.get('session_id', datetime.now().strftime('%Y%m%d_%H%M%S'))
        filename = f"reporte_rapido_{session_id}.pdf"
        
        # Obtener ruta de destino
        output_path = self.path_manager.get_reports_path(filename)
        
        # Crear directorio si no existe
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Guardar PDF
        self.pdf.output(output_path)
        
        return output_path
    
    def _calculate_image_dimensions(self, img_path: str):
        """Calcular dimensiones de imagen preservando aspect ratio"""
        try:
            from PIL import Image
            
            # Abrir imagen para obtener dimensiones originales
            with Image.open(img_path) as img:
                orig_width, orig_height = img.size
                
            # Calcular aspect ratio original
            aspect_ratio = orig_width / orig_height
            
            # Calcular dimensiones manteniendo proporciones
            if aspect_ratio > (self.max_img_width / self.max_img_height):
                # Imagen más ancha - limitar por ancho
                img_width = self.max_img_width
                img_height = self.max_img_width / aspect_ratio
            else:
                # Imagen más alta - limitar por alto
                img_height = self.max_img_height
                img_width = self.max_img_height * aspect_ratio
            
            # Calcular offsets para centrar
            offset_x = (self.max_img_width - img_width) / 2
            offset_y = (self.max_img_height - img_height) / 2
            
            logger.debug(f"📐 {os.path.basename(img_path)}: {orig_width}x{orig_height} → {img_width:.1f}x{img_height:.1f}mm (AR: {aspect_ratio:.2f})")
            
            return img_width, img_height, offset_x, offset_y
            
        except Exception as e:
            logger.warning(f"⚠️ Error calculando dimensiones para {img_path}: {e}")
            # Fallback: usar dimensiones máximas
            return self.max_img_width, self.max_img_height, 0, 0