# -*- coding: utf-8 -*-
"""
GPU Recorder usando FFmpeg con NVENC
Alternativa a PyAV para grabación completamente acelerada por GPU
"""

import subprocess
import threading
import queue
import numpy as np
from datetime import datetime
import os

from ...utils.logger import setup_logger

logger = setup_logger("GPURecorder")

class GPURecorder:
    """Grabador de video usando FFmpeg con NVENC (GPU completa)"""
    
    def __init__(self):
        self.is_recording = False
        self.ffmpeg_process = None
        self.frame_queue = queue.Queue(maxsize=30)
        self.recording_thread = None
        self.monitor_thread = None
        self.width = 2560
        self.height = 1440
        self.fps = 20
        self.bitrate = "8M"  # 8 Mbps
        
        # Detectar mejor encoder GPU disponible
        self.gpu_encoder = self._detect_best_gpu_encoder()
        
        logger.info(f"GPURecorder inicializado con encoder: {self.gpu_encoder}")
        
        # Si terminamos usando CPU, dar información útil
        if self.gpu_encoder == 'libx264':
            self._log_gpu_recommendations()
    
    def _detect_best_gpu_encoder(self):
        """Detectar el mejor encoder GPU disponible"""
        # Orden de preferencia
        preferred_encoders = [
            'h264_nvenc',    # NVIDIA NVENC (mejor para RTX)
            'h264_qsv',      # Intel Quick Sync (disponible en tu sistema)
            'h264_amf',      # AMD AMF (fallback)
        ]
        
        available_encoders = self._get_available_encoders()
        logger.info("🔍 Iniciando detección de encoders GPU...")
        
        # Probar encoders GPU en orden de preferencia
        for encoder in preferred_encoders:
            if encoder in available_encoders:
                logger.info(f"🧪 Probando funcionalidad de {encoder}...")
                if self._test_encoder_functionality(encoder):
                    logger.info(f"✅ Encoder GPU seleccionado: {encoder}")
                    logger.info(f"🎮 GPU encoding habilitado con {encoder}")
                    return encoder
                else:
                    logger.warning(f"❌ {encoder} no funcional, continuando con siguiente...")
            else:
                logger.info(f"⚠️ {encoder} no disponible en este sistema")
        
        # Si ningún GPU encoder funciona, usar CPU
        logger.info("💻 Ningún encoder GPU funcional - usando CPU encoding (libx264)")
        return 'libx264'
    
    def _get_available_encoders(self):
        """Obtener lista de encoders disponibles"""
        try:
            result = subprocess.run(
                ['ffmpeg', '-hide_banner', '-encoders'],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.stdout
        except Exception as e:
            logger.error(f"❌ Error obteniendo encoders: {e}")
            return ""
    
    def start_recording(self, filename):
        """Iniciar grabación con FFmpeg + GPU"""
        if self.is_recording:
            logger.warning("Ya hay una grabación en curso")
            return False
        
        try:
            logger.info(f"🎬 Iniciando grabación GPU: {filename}")
            logger.info(f"🎮 Usando encoder: {self.gpu_encoder}")
            
            # Crear directorio si no existe
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            # Comando FFmpeg optimizado según el encoder
            ffmpeg_cmd = self._build_ffmpeg_command(filename)
            
            logger.info(f"🔧 Comando FFmpeg: {' '.join(ffmpeg_cmd)}")
            
            # Iniciar proceso FFmpeg
            self.ffmpeg_process = subprocess.Popen(
                ffmpeg_cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                bufsize=10**8
            )
            
            # Verificar que el proceso inició correctamente
            import time
            time.sleep(0.1)  # Dar tiempo al proceso para iniciar
            if self.ffmpeg_process.poll() is not None:
                # El proceso ya terminó, obtener error
                stdout, stderr = self.ffmpeg_process.communicate()
                logger.error(f"❌ FFmpeg terminó inmediatamente")
                logger.error(f"STDOUT: {stdout.decode() if stdout else 'vacío'}")
                logger.error(f"STDERR: {stderr.decode() if stderr else 'vacío'}")
                raise Exception(f"FFmpeg falló al iniciar: {stderr.decode() if stderr else 'Sin detalles'}")
            
            # Iniciar threads
            self.is_recording = True
            
            # Thread de grabación
            self.recording_thread = threading.Thread(target=self._recording_worker)
            self.recording_thread.daemon = True
            self.recording_thread.start()
            
            # Thread de monitoreo FFmpeg
            self.monitor_thread = threading.Thread(target=self._monitor_ffmpeg)
            self.monitor_thread.daemon = True
            self.monitor_thread.start()
            
            logger.info("✅ Grabación GPU iniciada exitosamente")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error iniciando grabación GPU: {e}")
            self._cleanup()
            return False
    
    def _build_ffmpeg_command(self, filename):
        """Construir comando FFmpeg optimizado según el encoder"""
        base_cmd = [
            'ffmpeg',
            '-y',  # Sobrescribir archivo existente
            '-f', 'rawvideo',  # Formato de entrada
            '-vcodec', 'rawvideo',
            '-s', f'{self.width}x{self.height}',  # Resolución
            '-pix_fmt', 'rgb24',  # Formato de pixel
            '-r', str(self.fps),  # FPS
            '-i', '-',  # Entrada desde stdin
        ]
        
        # Configuración específica por encoder
        if self.gpu_encoder == 'h264_nvenc':
            # Configuración optimizada para NVIDIA NVENC
            encoder_cmd = [
                '-c:v', 'h264_nvenc',
                '-preset', 'fast',           # Velocidad de encoding
                '-tune', 'll',               # Low latency
                '-rc', 'cbr',                # Constant bitrate
                '-b:v', self.bitrate,        # Bitrate
                '-maxrate', self.bitrate,    # Max bitrate
                '-bufsize', '16M',           # Buffer size
                '-profile:v', 'high',        # H.264 profile
                '-level:v', '4.1',           # H.264 level
                '-pix_fmt', 'yuv420p',       # Formato de salida
                '-movflags', '+faststart',   # Optimización MP4
            ]
        elif self.gpu_encoder == 'h264_amf':
            # Configuración para AMD AMF
            encoder_cmd = [
                '-c:v', 'h264_amf',
                '-quality', 'speed',         # Priorizar velocidad
                '-rc', 'cbr',
                '-b:v', self.bitrate,
                '-maxrate', self.bitrate,
                '-pix_fmt', 'yuv420p',
                '-movflags', '+faststart',
            ]
        elif self.gpu_encoder == 'h264_qsv':
            # Configuración para Intel Quick Sync
            encoder_cmd = [
                '-c:v', 'h264_qsv',
                '-preset', 'fast',
                '-b:v', self.bitrate,
                '-maxrate', self.bitrate,
                '-pix_fmt', 'yuv420p',
                '-movflags', '+faststart',
            ]
        else:
            # Fallback CPU (libx264)
            encoder_cmd = [
                '-c:v', 'libx264',
                '-preset', 'ultrafast',      # Más rápido posible
                '-tune', 'zerolatency',      # Baja latencia
                '-b:v', self.bitrate,
                '-pix_fmt', 'yuv420p',
                '-movflags', '+faststart',
            ]
        
        return base_cmd + encoder_cmd + [filename]
    
    def stop_recording(self):
        """Detener grabación"""
        if not self.is_recording:
            logger.warning("No hay grabación en curso")
            return False
        
        try:
            logger.info("🛑 Deteniendo grabación GPU...")
            
            # Marcar como no grabando
            self.is_recording = False
            
            # Señal de fin para el thread
            self.frame_queue.put(None)
            
            # Esperar que terminen los threads
            if self.recording_thread:
                self.recording_thread.join(timeout=5.0)
                logger.info("✅ Thread de grabación terminado")
            
            if self.monitor_thread:
                self.monitor_thread.join(timeout=2.0)
                logger.info("✅ Thread de monitor terminado")
            
            # Cerrar FFmpeg de forma segura
            if self.ffmpeg_process:
                try:
                    if self.ffmpeg_process.stdin and not self.ffmpeg_process.stdin.closed:
                        self.ffmpeg_process.stdin.close()
                    
                    # Esperar a que termine el proceso
                    self.ffmpeg_process.wait(timeout=10.0)
                    logger.info("✅ Proceso FFmpeg terminado correctamente")
                except subprocess.TimeoutExpired:
                    logger.warning("⚠️ FFmpeg no terminó en tiempo, forzando cierre")
                    self.ffmpeg_process.terminate()
                    try:
                        self.ffmpeg_process.wait(timeout=5.0)
                    except subprocess.TimeoutExpired:
                        self.ffmpeg_process.kill()
                        logger.warning("🔥 FFmpeg forzado a terminar")
                except Exception as e:
                    logger.error(f"❌ Error cerrando FFmpeg: {e}")
            
            # Limpiar recursos
            self._cleanup()
            
            logger.info("✅ Grabación GPU detenida exitosamente")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error deteniendo grabación GPU: {e}")
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
        """Worker thread que procesa frames y los envía a FFmpeg"""
        logger.info("🎯 Worker de grabación GPU iniciado")
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
                    
                    # Validar dimensiones del frame
                    expected_size = height * width * 3  # RGB = 3 bytes por pixel
                    actual_size = len(frame_data)
                    
                    if actual_size != expected_size:
                        logger.warning(f"⚠️ Tamaño de frame incorrecto: esperado {expected_size}, recibido {actual_size}")
                        logger.warning(f"⚠️ Dimensiones: {width}x{height}, configurado: {self.width}x{self.height}")
                        continue
                    
                    # Convertir datos a numpy array
                    frame_array = np.frombuffer(frame_data, dtype=np.uint8)
                    frame_array = frame_array.reshape((height, width, 3))  # RGB
                    
                    # Verificar que las dimensiones coincidan con la configuración
                    if width != self.width or height != self.height:
                        logger.warning(f"⚠️ Dimensiones del frame ({width}x{height}) no coinciden con configuración ({self.width}x{self.height})")
                        # Redimensionar si es necesario (esto es costoso, mejor arreglar la fuente)
                        continue
                    
                    # Enviar frame a FFmpeg
                    if self.ffmpeg_process and self.ffmpeg_process.stdin:
                        try:
                            # Verificar que el proceso siga corriendo
                            if self.ffmpeg_process.poll() is not None:
                                logger.warning("🛑 Proceso FFmpeg terminado, deteniendo worker")
                                break
                            
                            self.ffmpeg_process.stdin.write(frame_array.tobytes())
                            self.ffmpeg_process.stdin.flush()
                        except BrokenPipeError:
                            logger.warning("🛑 FFmpeg cerró la entrada, deteniendo worker")
                            break
                        except OSError as e:
                            if e.errno == 22:  # Invalid argument
                                logger.warning("🛑 FFmpeg no acepta más datos, deteniendo worker")
                                break
                            else:
                                logger.error(f"❌ Error OSError enviando frame: {e}")
                                break
                    
                    frame_count += 1
                    
                    if frame_count % 100 == 0:
                        logger.debug(f"📹 Frames grabados (GPU): {frame_count}")
                    
                except queue.Empty:
                    continue
                except Exception as e:
                    logger.error(f"❌ Error procesando frame GPU: {e}")
                    continue
            
            logger.info(f"✅ Worker GPU terminado - Total frames: {frame_count}")
            
        except Exception as e:
            logger.error(f"❌ Error en worker de grabación GPU: {e}")
    
    def _monitor_ffmpeg(self):
        """Monitorear el proceso FFmpeg para detectar errores"""
        logger.info("👁️ Monitor FFmpeg iniciado")
        
        try:
            while self.is_recording and self.ffmpeg_process:
                # Verificar si el proceso sigue corriendo
                if self.ffmpeg_process.poll() is not None:
                    # El proceso terminó inesperadamente
                    stdout, stderr = self.ffmpeg_process.communicate()
                    
                    logger.error("🚨 FFmpeg terminó inesperadamente!")
                    logger.error(f"Código de salida: {self.ffmpeg_process.returncode}")
                    
                    if stdout:
                        logger.error(f"STDOUT FFmpeg: {stdout.decode()}")
                    if stderr:
                        logger.error(f"STDERR FFmpeg: {stderr.decode()}")
                    
                    # Marcar como no grabando para detener el worker
                    self.is_recording = False
                    break
                
                # Esperar un poco antes de verificar de nuevo
                import time
                time.sleep(0.5)
                
        except Exception as e:
            logger.error(f"❌ Error en monitor FFmpeg: {e}")
        
        logger.info("👁️ Monitor FFmpeg terminado")
    
    def _cleanup(self):
        """Limpiar recursos"""
        try:
            if self.ffmpeg_process:
                # Cerrar stdin de forma segura
                try:
                    if self.ffmpeg_process.stdin and not self.ffmpeg_process.stdin.closed:
                        self.ffmpeg_process.stdin.close()
                except Exception:
                    pass  # Ignorar errores al cerrar stdin
                
                # Terminar proceso si sigue corriendo
                if self.ffmpeg_process.poll() is None:
                    self.ffmpeg_process.terminate()
                    try:
                        self.ffmpeg_process.wait(timeout=5.0)
                    except subprocess.TimeoutExpired:
                        self.ffmpeg_process.kill()
                        logger.warning("🔥 Proceso FFmpeg forzado a terminar en cleanup")
                
                self.ffmpeg_process = None
                logger.info("🧹 Recursos GPU limpiados")
            
            # Limpiar cola de frames
            while not self.frame_queue.empty():
                try:
                    self.frame_queue.get_nowait()
                except:
                    break
                    
        except Exception as e:
            logger.error(f"❌ Error limpiando recursos GPU: {e}")
    
    def check_nvenc_support(self):
        """Verificar si NVENC está disponible y funcional"""
        try:
            # Primero verificar que los encoders estén listados
            result = subprocess.run(
                ['ffmpeg', '-hide_banner', '-encoders'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            # Verificar múltiples encoders GPU
            gpu_encoders = ['h264_nvenc', 'h264_amf', 'h264_qsv']
            available_gpu_encoders = []
            
            for encoder in gpu_encoders:
                if encoder in result.stdout:
                    available_gpu_encoders.append(encoder)
            
            if not available_gpu_encoders:
                logger.warning("⚠️ No hay encoders GPU listados")
                return False
            
            # Probar cada encoder disponible hasta encontrar uno funcional
            for encoder in available_gpu_encoders:
                logger.info(f"🧪 Probando funcionalidad de {encoder}...")
                test_success = self._test_encoder_functionality(encoder)
                if test_success:
                    logger.info(f"✅ Encoder GPU funcional encontrado: {encoder}")
                    return True
                else:
                    logger.warning(f"⚠️ {encoder} no funcional, probando siguiente...")
            
            # Si llegamos aquí, ningún encoder GPU funcionó
            logger.warning("⚠️ Ningún encoder GPU funcional, usando CPU")
            return False
                
        except Exception as e:
            logger.error(f"❌ Error verificando encoders GPU: {e}")
            return False
    
    def _test_encoder_functionality(self, encoder):
        """Probar si un encoder GPU realmente funciona"""
        try:
            logger.info(f"   🔧 Ejecutando prueba funcional para {encoder}...")
            
            # Comando de prueba mínimo
            test_cmd = [
                'ffmpeg', '-y', '-hide_banner', '-loglevel', 'error',
                '-f', 'lavfi', '-i', 'testsrc=duration=1:size=320x240:rate=1',
                '-c:v', encoder,
                '-frames:v', '1',
                '-f', 'null', '-'
            ]
            
            result = subprocess.run(
                test_cmd,
                capture_output=True,
                text=True,
                timeout=15
            )
            
            # Si el comando fue exitoso, el encoder funciona
            if result.returncode == 0:
                logger.info(f"   ✅ {encoder} funciona correctamente")
                return True
            else:
                # Verificar errores específicos
                stderr = result.stderr.lower()
                if 'driver does not support' in stderr or 'nvenc api version' in stderr:
                    logger.warning(f"   ❌ {encoder}: Driver NVIDIA incompatible (API version)")
                elif 'required nvenc api version' in stderr:
                    logger.warning(f"   ❌ {encoder}: Driver NVIDIA insuficiente")
                elif 'no device available' in stderr:
                    logger.warning(f"   ❌ {encoder}: Hardware no disponible")
                elif 'unknown encoder' in stderr:
                    logger.warning(f"   ❌ {encoder}: Encoder no reconocido")
                else:
                    logger.warning(f"   ❌ {encoder}: Error - {result.stderr.strip()}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error(f"   ⏰ {encoder}: Timeout en prueba funcional")
            return False
        except Exception as e:
            logger.error(f"   ❌ {encoder}: Error en prueba - {e}")
            return False
    
    def _log_gpu_recommendations(self):
        """Mostrar recomendaciones para habilitar GPU encoding"""
        logger.info("💡 RECOMENDACIONES PARA GPU ENCODING:")
        logger.info("   📋 Tu sistema:")
        logger.info("      - GPU: RTX 3050 Laptop GPU")
        logger.info("      - Driver actual: Soporta NVENC API 12.2")
        logger.info("      - Requerido: NVENC API 13.0+")
        logger.info("")
        logger.info("   🔧 Para habilitar GPU encoding:")
        logger.info("      1. Actualizar driver NVIDIA a versión más reciente")
        logger.info("      2. Descargar desde: https://www.nvidia.com/drivers")
        logger.info("      3. Buscar: RTX 3050 Laptop GPU + Windows 10")
        logger.info("      4. Instalar driver versión 535+ o superior")
        logger.info("")
        logger.info("   ⚡ Beneficios de GPU encoding:")
        logger.info("      - Menor uso de CPU (15% vs 25%)")
        logger.info("      - Mayor velocidad de encoding")
        logger.info("      - Mejor calidad a mismo bitrate")
        logger.info("")
        logger.info("   📊 Estado actual: CPU encoding funcional y confiable")
    
    def get_encoder_info(self):
        """Obtener información del encoder actual"""
        return {
            'encoder': self.gpu_encoder,
            'is_gpu': self.gpu_encoder in ['h264_nvenc', 'h264_amf', 'h264_qsv'],
            'bitrate': self.bitrate,
            'resolution': f"{self.width}x{self.height}",
            'fps': self.fps
        } 