"""
Services layer for the slot analyzer application.
Provides access to core functionality modules.
"""

from .health import health_service  # Explicit import from health.py module
from .capture import (
    SlotGameCapture,
    ProxyManager,
    ScreenshotManager
)

__all__ = [
    'SlotGameCapture',
    'ProxyManager',
    'ScreenshotManager',
    'ServiceRegistry',
    'health_service'
]


class ServiceRegistry:
    def __init__(self):
        self.services = {}

    def register(self, name, service):
        self.services[name] = service

    def get(self, name):
        return self.services.get(name)