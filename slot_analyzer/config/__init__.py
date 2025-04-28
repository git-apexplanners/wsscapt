"""Configuration management for the Slot Game Analyzer."""

from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings

__all__ = ['Settings', 'get_settings']

def get_settings():
    """Get the application settings instance"""
    return settings

class Settings(BaseSettings):
    """Base configuration settings."""
    
    # Application settings
    APP_NAME: str = Field(
        default="Slot Game Analyzer",
        description="Application name"
    )
    APP_VERSION: str = Field(
        default="0.1.0",
        description="Application version"
    )
    ENV: str = Field(
        default="development",
        description="Runtime environment (development|production|staging)",
        env="SLOT_ANALYZER_ENV"
    )
    DEBUG: bool = Field(
        default=False,
        description="Enable debug mode",
        env="SLOT_ANALYZER_DEBUG"
    )
    
    # Paths
    BASE_DIR: Path = Field(
        default=Path(__file__).resolve().parent.parent.parent,
        description="Base directory for the application"
    )
    DATA_DIR: Path = Field(
        default=Path("data"),
        description="Directory for application data"
    )
    SCREENSHOT_DIR: Path = Field(
        default=Path("screenshots"),
        description="Directory to store captured screenshots",
        env="SLOT_ANALYZER_CAPTURE_SCREENSHOT_DIR"
    )
    
    # Redis settings
    REDIS_HOST: str = Field(
        default="localhost",
        description="Redis server hostname",
        env="REDIS_HOST"
    )
    REDIS_PORT: int = Field(
        default=6379,
        description="Redis server port",
        env="REDIS_PORT"
    )
    REDIS_DB: int = Field(
        default=0,
        description="Redis database number",
        env="REDIS_DB"
    )
    
    # Proxy settings
    PROXY_HOST: str = Field(
        default="127.0.0.1",
        description="Proxy server hostname",
        env="PROXY_HOST"
    )
    PROXY_PORT: int = Field(
        default=8080,
        description="Proxy server port",
        env="SLOT_ANALYZER_CAPTURE_PROXY_PORT"
    )
    CERT_DIR: Path = Field(
        default=Path("certificates"),
        description="Directory for SSL certificates",
        env="CERT_DIR"
    )
    
    # Capture settings
    CAPTURE_THROTTLE_MS: int = Field(
        default=500,
        description="Minimum time between screenshots in milliseconds",
        env="SLOT_ANALYZER_CAPTURE_SCREENSHOT_THROTTLE_MS"
    )
    MAX_CAPTURE_QUEUE: int = Field(
        default=100,
        description="Maximum number of captures to queue before dropping",
        env="SLOT_ANALYZER_CAPTURE_MAX_CAPTURE_QUEUE"
    )
    
    # Logging
    LOG_LEVEL: str = Field(
        default="INFO",
        description="Logging level (DEBUG|INFO|WARNING|ERROR|CRITICAL)",
        env="LOG_LEVEL"
    )
    LOG_FORMAT: str = Field(
        default="structured",
        description="Log format (structured|plain)"
    )
    LOG_FILE: Optional[Path] = Field(
        default=None,
        description="Optional path to log file"
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # Ignore extra environment variables

    def validate_paths(self) -> dict:
        """
        Validate that required directories exist or can be created.
        Returns dictionary of full paths keyed by directory name.
        """
        path_dict = {}
        required_dirs = {
            "DATA_DIR": self.DATA_DIR,
            "SCREENSHOT_DIR": self.SCREENSHOT_DIR,
            "CERT_DIR": self.CERT_DIR
        }
        
        for name, path in required_dirs.items():
            full_path = self.BASE_DIR / path
            full_path.mkdir(parents=True, exist_ok=True)
            path_dict[name] = full_path
            
        return path_dict

settings = Settings()
settings.validate_paths()