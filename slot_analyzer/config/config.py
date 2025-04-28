"""Configuration management system for slot analyzer application."""
import os
from pathlib import Path
from typing import Optional, Dict, Any
from configparser import ConfigParser
from pydantic_settings import BaseSettings
from pydantic import validator, Field

class CaptureSettings(BaseSettings):
    """Configuration for capture service."""
    screenshot_throttle_ms: int = Field(
        500,
        description="Minimum time between screenshots in milliseconds"
    )
    proxy_port: int = Field(
        8080,
        description="Port for proxy server to listen on"
    )
    screenshot_dir: str = Field(
        "screenshots",
        description="Directory to store captured screenshots"
    )
    max_capture_queue: int = Field(
        100,
        description="Maximum number of captures to queue before dropping"
    )

    @validator('screenshot_throttle_ms')
    def validate_throttle(cls, v):
        if v < 100:
            raise ValueError("Screenshot throttle must be >= 100ms")
        return v

class AppSettings(BaseSettings):
    """Main application configuration."""
    env: str = Field(
        "development",
        description="Runtime environment (development|production)"
    )
    debug: bool = Field(
        False,
        description="Enable debug mode"
    )
    capture: CaptureSettings = Field(
        default_factory=CaptureSettings,
        description="Capture service configuration"
    )

    class Config:
        env_prefix = "SLOT_ANALYZER_"
        env_file = ".env"
        env_file_encoding = "utf-8"

def load_config() -> AppSettings:
    """Load configuration with environment overrides."""
    # Load from .env file if present
    env_file = Path(".env")
    if env_file.exists():
        from dotenv import load_dotenv
        load_dotenv(env_file)

    # Load from config.ini if present
    config = ConfigParser()
    config_file = Path("config.ini")
    if config_file.exists():
        config.read(config_file)

    # Create settings with environment overrides
    settings = AppSettings()

    # Apply INI file overrides if present
    if config.has_section("slot_analyzer"):
        for key, value in config["slot_analyzer"].items():
            if hasattr(settings, key):
                setattr(settings, key, value)

    return settings

def get_config() -> AppSettings:
    """Get the application configuration (singleton pattern)."""
    if not hasattr(get_config, "_instance"):
        get_config._instance = load_config()
    return get_config._instance