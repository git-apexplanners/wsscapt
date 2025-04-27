"""
Services layer for the slot analyzer application.
Provides access to core functionality modules.
"""

from .capture import (
    SlotGameCapture,
    ProxyManager,
    ScreenshotManager
)

__all__ = [
    'SlotGameCapture',
    'ProxyManager',
    'ScreenshotManager'
]