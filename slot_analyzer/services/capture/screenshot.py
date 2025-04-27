"""
Screenshot capture management module with throttling and storage.
"""
import asyncio
from datetime import datetime
from pathlib import Path
import time
from typing import Optional

import pyautogui
from loguru import logger
from PIL import Image

from slot_analyzer.errors import CaptureError
from slot_analyzer.config import settings

class ScreenshotManager:
    """Manages screenshot captures with throttling"""

    def __init__(self, session_id: str, throttle_ms: int = 500):
        """
        Initialize the screenshot manager.
        
        Args:
            session_id: Unique session identifier for organizing screenshots
            throttle_ms: Minimum time between screenshots in milliseconds
        """
        self.base_dir = settings.SCREENSHOT_DIR
        self.session_dir = self.base_dir / session_id
        self.throttle_ms = throttle_ms
        self._last_capture = 0
        self._running = False
        
        # Ensure screenshot directory exists
        self.session_dir.mkdir(parents=True, exist_ok=True)
        
        # Configure pyautogui safety settings
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.1  # Add small delay between actions

    async def start(self):
        """Start the screenshot manager"""
        if self._running:
            raise CaptureError("Screenshot manager already running")

        self._running = True
        logger.info(f"Started screenshot manager for session: {self.session_dir.name}")

    async def stop(self):
        """Stop the screenshot manager and cleanup"""
        if not self._running:
            return

        self._running = False
        await self._cleanup()
        logger.info("Screenshot manager stopped")

    async def capture(self) -> Optional[Path]:
        """
        Capture a screenshot if throttling allows.
        
        Returns:
            Path to the captured screenshot file or None if throttled
        """
        if not self._running:
            return None

        current_time = time.time() * 1000  # Convert to milliseconds
        time_since_last = current_time - self._last_capture

        if time_since_last < self.throttle_ms:
            return None

        try:
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
            screenshot_path = self.session_dir / f"capture_{timestamp}.png"

            # Capture and save screenshot
            screenshot = pyautogui.screenshot()
            
            # Validate screenshot
            if not self._validate_screenshot(screenshot):
                logger.warning("Invalid screenshot captured, skipping")
                return None

            # Save with compression
            screenshot.save(
                screenshot_path,
                format="PNG",
                optimize=True,
                compression_level=6
            )

            self._last_capture = current_time
            logger.debug(f"Screenshot captured: {screenshot_path.name}")
            
            return screenshot_path

        except Exception as e:
            logger.error(f"Screenshot capture failed: {str(e)}")
            return None

    def _validate_screenshot(self, screenshot: Image.Image) -> bool:
        """
        Validate captured screenshot.
        
        Args:
            screenshot: PIL Image object to validate
        
        Returns:
            bool: True if screenshot is valid
        """
        # Check for minimum dimensions
        if screenshot.width < 100 or screenshot.height < 100:
            return False

        # Check if image is completely black or white
        extrema = screenshot.convert("L").getextrema()
        if extrema[0] == extrema[1]:  # Same min/max means solid color
            return False

        return True

    async def _cleanup(self):
        """Cleanup any temporary files"""
        # In the future, we might want to:
        # - Remove duplicate screenshots
        # - Compress screenshots further
        # - Move screenshots to long-term storage
        pass