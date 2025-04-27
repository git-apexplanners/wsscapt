"""Logging configuration for the Slot Game Analyzer."""

import sys
from typing import Any, Dict, Optional

import structlog
from loguru import logger

from slot_analyzer.config import settings

def configure_logging() -> None:
    """Configure structured logging for the application."""
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        cache_logger_on_first_use=True,
    )
    
    # Configure loguru
    logger.remove()  # Remove default handler
    
    # Add console handler
    logger.add(
        sys.stderr,
        level=settings.LOG_LEVEL,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
        backtrace=True,
        diagnose=True,
    )
    
    # Add file handler if log file is specified
    if settings.LOG_FILE:
        logger.add(
            settings.LOG_FILE,
            rotation="100 MB",
            retention="30 days",
            compression="zip",
            level=settings.LOG_LEVEL,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
        )

def get_logger(name: Optional[str] = None) -> structlog.BoundLogger:
    """Get a structured logger instance."""
    return structlog.get_logger(name)

# Configure logging on module import
configure_logging()