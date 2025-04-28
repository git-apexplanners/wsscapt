"""
Custom exceptions for the slot analyzer application with enhanced error handling.
"""

from typing import Any, Dict, Optional

class SlotAnalyzerError(Exception):
    """Base exception for all slot analyzer errors"""
    def __init__(self, message: str, error_code: str = None, context: Dict[str, Any] = None):
        super().__init__(message)
        self.error_code = error_code or "GENERIC_ERROR"
        self.context = context or {}
        self.recovery_guidance = ""

    def with_recovery(self, guidance: str) -> 'SlotAnalyzerError':
        """Add recovery guidance to the error"""
        self.recovery_guidance = guidance
        return self

class CaptureError(SlotAnalyzerError):
    """Raised when capture operations fail"""
    def __init__(self, message: str, component: str = None, **kwargs):
        super().__init__(message, error_code="CAPTURE_ERROR", context={"component": component, **kwargs})

class ProxyError(CaptureError):
    """Raised when proxy operations fail"""
    def __init__(self, message: str, proxy_type: str = None, **kwargs):
        super().__init__(message, component="proxy", context={"proxy_type": proxy_type, **kwargs})

class ScreenshotError(CaptureError):
    """Raised when screenshot operations fail"""
    def __init__(self, message: str, screenshot_path: str = None, **kwargs):
        super().__init__(message, component="screenshot", context={"screenshot_path": screenshot_path, **kwargs})

class AnalysisError(SlotAnalyzerError):
    """Raised when pattern analysis operations fail"""
    def __init__(self, message: str, analysis_type: str = None, **kwargs):
        super().__init__(message, error_code="ANALYSIS_ERROR", context={"analysis_type": analysis_type, **kwargs})

class StatisticalAnalysisError(AnalysisError):
    """Raised when statistical analysis fails"""
    def __init__(self, message: str, test_type: str = None, **kwargs):
        super().__init__(message, analysis_type="statistical", context={"test_type": test_type, **kwargs})

class PatternDetectionError(AnalysisError):
    """Raised when pattern detection fails"""
    def __init__(self, message: str, pattern_type: str = None, **kwargs):
        super().__init__(message, analysis_type="pattern", context={"pattern_type": pattern_type, **kwargs})

class ValidationError(SlotAnalyzerError):
    """Raised when data validation fails"""
    def __init__(self, message: str, field: str = None, value: Any = None, **kwargs):
        super().__init__(message, error_code="VALIDATION_ERROR", context={"field": field, "value": value, **kwargs})

class InputValidationError(ValidationError):
    """Raised when user input validation fails"""
    def __init__(self, message: str, input_type: str = None, **kwargs):
        super().__init__(message, field=input_type, **kwargs)

class ConfigurationError(SlotAnalyzerError):
    """Raised when configuration is invalid or missing"""
    def __init__(self, message: str, config_key: str = None, **kwargs):
        super().__init__(message, error_code="CONFIG_ERROR", context={"config_key": config_key, **kwargs})

class MessageQueueError(SlotAnalyzerError):
    """Exception raised for errors in the message broker operations."""
    def __init__(self, message: str, queue_name: str = None, **kwargs):
        super().__init__(message, error_code="QUEUE_ERROR", context={"queue_name": queue_name, **kwargs})

class ResourceError(SlotAnalyzerError):
    """Raised when resource allocation or access fails"""
    def __init__(self, message: str, resource_type: str = None, **kwargs):
        super().__init__(message, error_code="RESOURCE_ERROR", context={"resource_type": resource_type, **kwargs})