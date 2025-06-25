# -*- coding: utf-8 -*-
"""
Módulo de video widget para streaming GStreamer
Refactorización modular del video_widget.py original
"""

from .main_widget import VideoWidget
from .gstreamer_manager import GStreamerManager
from .overlay_manager import OverlayManager
from .metrics_integration import MetricsIntegration

__all__ = [
    'VideoWidget',
    'GStreamerManager', 
    'OverlayManager',
    'MetricsIntegration'
] 