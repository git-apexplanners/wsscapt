"""Configuration management for the Slot Game Analyzer."""

from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Base configuration settings."""
    
    # Application settings
    APP_NAME: str = "Slot Game Analyzer"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    
    # Paths
    BASE_DIR: Path = Path(__file__).parent.parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    SCREENSHOT_DIR: Path = Field(default=Path("screenshots"), env="SCREENSHOT_DIR")
    
    # Redis settings
    REDIS_HOST: str = Field(default="localhost", env="REDIS_HOST")
    REDIS_PORT: int = Field(default=6379, env="REDIS_PORT")
    REDIS_DB: int = Field(default=0, env="REDIS_DB")
    
    # Proxy settings
    PROXY_HOST: str = Field(default="127.0.0.1", env="PROXY_HOST")
    PROXY_PORT: int = Field(default=8080, env="PROXY_PORT")
    CERT_DIR: Path = Field(default=Path("certificates"), env="CERT_DIR")
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = "structured"
    LOG_FILE: Optional[Path] = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()