"""
Core capture module implementation for slot game analysis.
"""
from datetime import datetime
import asyncio
from typing import Dict, Optional
from pathlib import Path

from loguru import logger
from pydantic import BaseModel

from slot_analyzer.services.capture.proxy import ProxyManager
from slot_analyzer.services.capture.screenshot import ScreenshotManager
from slot_analyzer.errors import CaptureError
from slot_analyzer.message_broker import MessageQueue

class SessionInfo(BaseModel):
    """Validates and stores session information"""
    casino_name: str
    game_name: str
    session_id: Optional[str] = None
    start_time: Optional[datetime] = None

    def generate_session_id(self) -> str:
        """Generate a unique session ID using the required format"""
        if not self.start_time:
            self.start_time = datetime.now()
        timestamp = self.start_time.strftime("%Y%m%d-%H%M%S")
        return f"{self.casino_name}-{self.game_name}-{timestamp}"

class CaptureData(BaseModel):
    """Data structure for captured network traffic and screenshots"""
    timestamp: datetime
    request_data: Dict
    response_data: Optional[Dict]
    screenshot_path: Optional[Path]
    websocket_data: Optional[Dict]

class SlotGameCapture:
    """Main capture class handling network traffic and screenshots"""

    def __init__(self, session_info: Dict):
        """Initialize capture components and session information"""
        self.session = SessionInfo(**session_info)
        if not self.session.session_id:
            self.session.session_id = self.session.generate_session_id()

        self.proxy_manager = ProxyManager()
        self.screenshot_manager = ScreenshotManager(
            session_id=self.session.session_id,
            throttle_ms=500  # Configurable screenshot throttling
        )
        self.message_queue = MessageQueue()
        self.captures: list[CaptureData] = []
        self._running = False

    async def start_capture(self):
        """Start the capture process"""
        if self._running:
            raise CaptureError("Capture session already running")

        try:
            self._running = True
            logger.info(f"Starting capture session: {self.session.session_id}")
            
            # Start proxy with SSL certificate handling
            await self.proxy_manager.start()
            
            # Start screenshot capture task
            screenshot_task = asyncio.create_task(self.screenshot_manager.start())
            
            # Register capture handlers
            self.proxy_manager.on_request(self._handle_request)
            self.proxy_manager.on_response(self._handle_response)
            self.proxy_manager.on_websocket(self._handle_websocket)
            
            await asyncio.gather(
                self._process_captures(),
                screenshot_task
            )

        except Exception as e:
            logger.error(f"Error in capture session: {str(e)}")
            raise CaptureError(f"Capture session failed: {str(e)}")

    async def stop_capture(self):
        """Stop the capture process and cleanup resources"""
        if not self._running:
            return

        self._running = False
        try:
            await self.proxy_manager.stop()
            await self.screenshot_manager.stop()
            await self._cleanup()
        except Exception as e:
            logger.error(f"Error stopping capture: {str(e)}")
            raise CaptureError(f"Failed to stop capture cleanly: {str(e)}")

    async def _handle_request(self, request_data: Dict):
        """Handle intercepted HTTP/HTTPS requests"""
        if not self._running:
            return

        timestamp = datetime.now()
        capture = CaptureData(
            timestamp=timestamp,
            request_data=request_data,
            response_data=None,
            screenshot_path=await self.screenshot_manager.capture(),
            websocket_data=None
        )
        self.captures.append(capture)

    async def _handle_response(self, response_data: Dict):
        """Handle intercepted HTTP/HTTPS responses"""
        if not self._running or not self.captures:
            return

        # Associate response with the most recent capture
        self.captures[-1].response_data = response_data

    async def _handle_websocket(self, websocket_data: Dict):
        """Handle WebSocket messages"""
        if not self._running:
            return

        timestamp = datetime.now()
        capture = CaptureData(
            timestamp=timestamp,
            request_data={},
            response_data=None,
            screenshot_path=await self.screenshot_manager.capture(),
            websocket_data=websocket_data
        )
        self.captures.append(capture)

    async def _process_captures(self):
        """Process and queue captured data"""
        while self._running:
            if self.captures:
                capture = self.captures.pop(0)
                await self.message_queue.publish(
                    "captures",
                    {
                        "session_id": self.session.session_id,
                        "timestamp": capture.timestamp.isoformat(),
                        "data": capture.dict()
                    }
                )
            await asyncio.sleep(0.1)

    async def _cleanup(self):
        """Cleanup resources and save any remaining captures"""
        # Process any remaining captures
        while self.captures:
            capture = self.captures.pop(0)
            await self.message_queue.publish(
                "captures",
                {
                    "session_id": self.session.session_id,
                    "timestamp": capture.timestamp.isoformat(),
                    "data": capture.dict()
                }
            )

        logger.info(f"Cleanup completed for session: {self.session.session_id}")