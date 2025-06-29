# -*- coding: utf-8 -*-
"""
PyAV Recorder para grabación con GPU
Reemplaza la problemática cadena nvh264enc + mp4mux + filesink
"""

import av
import numpy as np
import threading
import queue
from datetime import datetime
import os

from ...utils.logger import setup_logger

logger = setup_logger("PyAVRecorder")

class PyAVRecorder:
    """Grabador de video usando PyAV con encoding GPU"""
    
    def __init__(self):
        self.is_recording = False
        self.output_file = None
        self.codec_context = None
        self.frame_queue = queue.Queue(maxsize=30)  # Buffer de frames
        self.recording_thread = None
        self.width = 2560
        self.height = 1440
        self.fps = 20
        self.bitrate = 8000000  # 8 Mbps
        
        logger.info("PyAVRecorder inicializado")
    
    def start_recording(self, filename):
        """Iniciar grabación con PyAV"""
        if self.is_recording:
            logger.warning("Ya hay una grabación en curso")
            return False
        
        try:
            logger.info(f"🎬 Iniciando grabación PyAV: {filename}")
            
            # Crear directorio si no existe
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            # Abrir archivo de salida
            self.output_file = av.open(filename, 'w')
            
            # Configurar stream de video - Usar CPU encoding directamente
            logger.info("🔧 Configurando encoding de video...")
            try:
                # Usar CPU encoding que es más compatible
                video_stream = self.output_file.add_stream('libx264', rate=self.fps)
                logger.info("✅ Usando libx264 (CPU encoding)")
            except Exception as e:
                logger.warning(f"⚠️ libx264 no disponible: {e}")
                try:
                    # Fallback a encoder genérico
                    video_stream = self.output_file.add_stream('h264', rate=self.fps)
                    logger.info("✅ Usando h264 (encoder genérico)")
                except Exception as e2:
                    logger.error(f"❌ Error con h264: {e2}")
                    raise Exception(f"No se pudo crear stream de video: {e2}")
            
            if not video_stream:
                raise Exception("No se pudo crear stream de video")
            
            # Configurar propiedades del stream
            video_stream.width = self.width
            video_stream.height = self.height
            video_stream.pix_fmt = 'yuv420p'
            video_stream.bit_rate = self.bitrate
            
            # Guardar codec context
            self.codec_context = video_stream
            
            # Iniciar thread de grabación
            self.is_recording = True
            self.recording_thread = threading.Thread(target=self._recording_worker)
            self.recording_thread.daemon = True
            self.recording_thread.start()
            
            logger.info("✅ Grabación PyAV iniciada exitosamente")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error iniciando grabación PyAV: {e}")
            self._cleanup()
            return False
    
    def stop_recording(self):
        """Detener grabación"""
        if not self.is_recording:
            logger.warning("No hay grabación en curso")
            return False
        
        try:
            logger.info("🛑 Deteniendo grabación PyAV...")
            
            # Marcar como no grabando
            self.is_recording = False
            
            # Señal de fin para el thread
            self.frame_queue.put(None)
            
            # Esperar que termine el thread
            if self.recording_thread:
                self.recording_thread.join(timeout=5.0)
                logger.info("✅ Thread de grabación terminado")
            
            # Limpiar recursos
            self._cleanup()
            
            logger.info("✅ Grabación PyAV detenida exitosamente")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error deteniendo grabación PyAV: {e}")
            return False
    
    def add_frame(self, frame_data, width, height):
        """Agregar frame a la cola de grabación"""
        if not self.is_recording:
            return
        
        try:
            # Agregar frame a la cola (non-blocking)
            self.frame_queue.put_nowait((frame_data, width, height))
        except queue.Full:
            # Si la cola está llena, descartar frame más antiguo
            try:
                self.frame_queue.get_nowait()
                self.frame_queue.put_nowait((frame_data, width, height))
            except queue.Empty:
                pass
    
    def _recording_worker(self):
        """Worker thread que procesa frames y los escribe al archivo"""
        logger.info("🎯 Worker de grabación iniciado")
        frame_count = 0
        
        try:
            while self.is_recording:
                try:
                    # Obtener frame de la cola
                    frame_item = self.frame_queue.get(timeout=1.0)
                    
                    # Señal de fin
                    if frame_item is None:
                        break
                    
                    frame_data, width, height = frame_item
                    
                    # Convertir datos a numpy array
                    frame_array = np.frombuffer(frame_data, dtype=np.uint8)
                    frame_array = frame_array.reshape((height, width, 3))  # RGB
                    
                    # Crear VideoFrame de PyAV
                    av_frame = av.VideoFrame.from_ndarray(frame_array, format='rgb24')
                    av_frame.pts = frame_count
                    
                    # Encode frame
                    try:
                        packets = self.codec_context.encode(av_frame)
                    except Exception as e:
                        logger.error(f"❌ Error encoding frame: {e}")
                        continue
                    
                    # Escribir packets al archivo
                    for packet in packets:
                        self.output_file.mux(packet)
                    
                    frame_count += 1
                    
                    if frame_count % 100 == 0:
                        logger.debug(f"📹 Frames grabados: {frame_count}")
                    
                except queue.Empty:
                    continue
                except Exception as e:
                    logger.error(f"❌ Error procesando frame: {e}")
                    continue
            
            # Flush encoder
            if self.codec_context:
                packets = self.codec_context.encode(None)
                for packet in packets:
                    self.output_file.mux(packet)
            
            logger.info(f"✅ Worker terminado - Total frames: {frame_count}")
            
        except Exception as e:
            logger.error(f"❌ Error en worker de grabación: {e}")
    
    def _cleanup(self):
        """Limpiar recursos"""
        try:
            if self.output_file:
                self.output_file.close()
                self.output_file = None
                logger.info("📁 Archivo de salida cerrado")
            
            # Limpiar cola
            while not self.frame_queue.empty():
                try:
                    self.frame_queue.get_nowait()
                except queue.Empty:
                    break
            
            self.codec_context = None
            
        except Exception as e:
            logger.error(f"❌ Error en cleanup: {e}") 