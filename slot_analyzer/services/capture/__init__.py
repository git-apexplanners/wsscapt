"""
Network Traffic Capture Module for Slot Game Analysis
Handles HTTP/HTTPS and WebSocket traffic interception with screenshot correlation
"""

from .capture import SlotGameCapture
from .proxy import ProxyManager
from .screenshot import ScreenshotManager

# Maintain backward compatibility
CaptureService = SlotGameCapture

__all__ = ['SlotGameCapture', 'ProxyManager', 'ScreenshotManager', 'CaptureService']