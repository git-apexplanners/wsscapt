"""
Custom exceptions for the slot analyzer application.
"""

class SlotAnalyzerError(Exception):
    """Base exception for all slot analyzer errors"""
    pass

class CaptureError(SlotAnalyzerError):
    """Raised when capture operations fail"""
    pass

class ProxyError(SlotAnalyzerError):
    """Raised when proxy operations fail"""
    pass

class MessageQueueError(SlotAnalyzerError):
    """Exception raised for errors in the message broker operations."""
    pass

class ValidationError(SlotAnalyzerError):
    """Raised when data validation fails"""
    pass

class ConfigurationError(SlotAnalyzerError):
    """Raised when configuration is invalid or missing"""
    pass

class QueueError(SlotAnalyzerError):
    """Raised when message queue operations fail"""
    pass

class AnalysisError(SlotAnalyzerError):
    """Raised when pattern analysis operations fail"""
    pass