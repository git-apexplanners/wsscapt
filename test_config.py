"""Test script for configuration validation."""
from slot_analyzer.config import Settings

def test_settings():
    """Test configuration settings loading."""
    # Test production mode
    import os
    os.environ["SLOT_ANALYZER_ENV"] = "production"
    os.environ["SLOT_ANALYZER_DEBUG"] = "false"
    
    settings = Settings()
    print("Configuration loaded successfully:")
    print(f"ENV: {settings.ENV}")
    print(f"DEBUG: {settings.DEBUG}")
    print(f"CAPTURE_THROTTLE_MS: {settings.CAPTURE_THROTTLE_MS}")
    print(f"MAX_CAPTURE_QUEUE: {settings.MAX_CAPTURE_QUEUE}")

if __name__ == "__main__":
    test_settings()