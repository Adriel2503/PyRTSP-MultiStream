import os
# ✅ FORZAR USO DE GPU DEDICADA
os.environ['CUDA_VISIBLE_DEVICES'] = '0'  # Solo GPU dedicada
os.environ['OPENCV_DNN_BACKEND'] = 'CUDA'
os.environ['OPENCV_DNN_TARGET'] = 'CUDA'

# Para GStreamer
os.environ['GST_GL_PLATFORM'] = 'wgl'  # Windows OpenGL
os.environ['GST_GL_API'] = 'opengl3'