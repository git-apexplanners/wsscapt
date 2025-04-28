"""
Core capture module implementation for slot game analysis.
"""
from datetime import datetime
import asyncio
from typing import Dict, Optional
from pathlib import Path

from loguru import logger
from pydantic import BaseModel
from slot_analyzer.config.config import get_config

from slot_analyzer.services.capture.proxy import ProxyManager
from slot_analyzer.services.capture.screenshot import ScreenshotManager
from slot_analyzer.errors import (
    CaptureError,
    ProxyError,
    ScreenshotError,
    MessageQueueError,
    ValidationError,
    ResourceError
)
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
        try:
            self.session = SessionInfo(**session_info)
            if not self.session.session_id:
                self.session.session_id = self.session.generate_session_id()

            self.proxy_manager = ProxyManager()
            config = get_config()
            self.screenshot_manager = ScreenshotManager(
                session_id=self.session.session_id,
                throttle_ms=config.capture.screenshot_throttle_ms
            )
            self.message_queue = MessageQueue()
        except Exception as e:
            raise ValidationError(
                "Invalid session configuration",
                input_type="session_info",
                value=session_info
            ).with_recovery("Verify session parameters and try again") from e
        self.captures: list[CaptureData] = []
        self._running = False

    async def start_capture(self):
        """Start the capture process"""
        if self._running:
            raise CaptureError(
                "Capture session already running",
                session_id=self.session.session_id
            ).with_recovery("Stop the current session before starting a new one")

        self._running = True
        logger.info(
            "Starting capture session",
            session_id=self.session.session_id,
            casino=self.session.casino_name,
            game=self.session.game_name
        )
            
            # Start proxy with SSL certificate handling
        # Start proxy with SSL certificate handling
        try:
            await self.proxy_manager.start()
        except Exception as e:
            raise ProxyError(
                "Failed to start proxy service",
                proxy_type=self.proxy_manager.__class__.__name__,
                session_id=self.session.session_id
            ).with_recovery("Check proxy configuration and network settings") from e
        
        # Start screenshot capture task
        try:
            screenshot_task = asyncio.create_task(self.screenshot_manager.start())
        except Exception as e:
            await self.proxy_manager.stop()
            raise ScreenshotError(
                "Failed to initialize screenshot capture",
                session_id=self.session.session_id
            ).with_recovery("Verify screenshot directory permissions") from e
            
            # Register capture handlers
            self.proxy_manager.on_request(self._handle_request)
            self.proxy_manager.on_response(self._handle_response)
            self.proxy_manager.on_websocket(self._handle_websocket)
            
            try:
                await asyncio.gather(
                    self._process_captures(),
                    screenshot_task
                )
            except Exception as e:
                logger.error(
                    "Error in capture session processing",
                    session_id=self.session.session_id,
                    error=str(e),
                    error_type=e.__class__.__name__
                )
                raise CaptureError(
                    "Capture processing failed",
                    session_id=self.session.session_id,
                    component="processor"
                ).with_recovery("Review captured data and restart session") from e

    async def stop_capture(self):
        """Stop the capture process and cleanup resources"""
        if not self._running:
            logger.debug(
                "Stop capture called but no session running",
                session_id=self.session.session_id
            )
            return

        self._running = False
        logger.info(
            "Stopping capture session",
            session_id=self.session.session_id
        )

        try:
            # Stop proxy manager
            try:
                await self.proxy_manager.stop()
            except Exception as e:
                raise ProxyError(
                    "Failed to stop proxy service",
                    proxy_type=self.proxy_manager.__class__.__name__,
                    session_id=self.session.session_id
                ).with_recovery("Check proxy status and try manual cleanup") from e

            # Stop screenshot manager
            try:
                await self.screenshot_manager.stop()
            except Exception as e:
                raise ScreenshotError(
                    "Failed to stop screenshot capture",
                    session_id=self.session.session_id
                ).with_recovery("Verify screenshot service status") from e

            # Final cleanup
            try:
                await self._cleanup()
            except Exception as e:
                raise ResourceError(
                    "Failed during final cleanup",
                    resource_type="capture_resources",
                    session_id=self.session.session_id
                ).with_recovery("Check system resources and perform manual cleanup") from e

        except Exception as e:
            logger.critical(
                "Error stopping capture session",
                session_id=self.session.session_id,
                error=str(e),
                error_type=e.__class__.__name__
            )
            raise CaptureError(
                "Failed to stop capture session cleanly",
                session_id=self.session.session_id
            ).with_recovery("Perform manual cleanup and verify system state") from e

    async def _handle_request(self, request_data: Dict):
        """Handle intercepted HTTP/HTTPS requests"""
        if not self._running:
            logger.debug(
                "Received request while not running",
                request_data=request_data
            )
            return

        try:
            # Validate request data
            if not isinstance(request_data, dict) or not request_data:
                raise ValidationError(
                    "Invalid request data format",
                    field="request_data",
                    value=type(request_data)
                )

            timestamp = datetime.now()
            
            # Capture screenshot with error handling
            try:
                screenshot_path = await self.screenshot_manager.capture()
            except Exception as e:
                logger.error(
                    "Failed to capture screenshot for request",
                    request_data=request_data,
                    error=str(e),
                    error_type=e.__class__.__name__
                )
                screenshot_path = None

            capture = CaptureData(
                timestamp=timestamp,
                request_data=request_data,
                response_data=None,
                screenshot_path=screenshot_path,
                websocket_data=None
            )
            
            self.captures.append(capture)
            logger.debug(
                "Successfully captured request",
                request_id=request_data.get('id'),
                timestamp=timestamp.isoformat()
            )

        except ValidationError as e:
            logger.warning(
                "Invalid request data received",
                error=str(e),
                error_type=e.__class__.__name__,
                request_data=request_data
            )
        except Exception as e:
            logger.error(
                "Error handling request",
                request_data=request_data,
                error=str(e),
                error_type=e.__class__.__name__
            )
            raise CaptureError(
                "Request handling failed",
                component="request_handler",
                request_id=request_data.get('id')
            ).with_recovery("Check request processing pipeline") from e

    async def _handle_response(self, response_data: Dict):
        """Handle intercepted HTTP/HTTPS responses"""
        if not self._running:
            logger.debug(
                "Received response while not running",
                response_data=response_data
            )
            return
            
        if not self.captures:
            logger.warning(
                "Received response with no pending captures",
                response_data=response_data
            )
            return

        try:
            # Validate response data
            if not isinstance(response_data, dict) or not response_data:
                raise ValidationError(
                    "Invalid response data format",
                    field="response_data",
                    value=type(response_data)
                )

            # Associate response with the most recent capture
            self.captures[-1].response_data = response_data
            logger.debug(
                "Successfully processed response",
                response_id=response_data.get('id'),
                timestamp=self.captures[-1].timestamp.isoformat()
            )

        except ValidationError as e:
            logger.warning(
                "Invalid response data received",
                error=str(e),
                error_type=e.__class__.__name__,
                response_data=response_data
            )
        except Exception as e:
            logger.error(
                "Error handling response",
                response_data=response_data,
                error=str(e),
                error_type=e.__class__.__name__
            )
            raise CaptureError(
                "Response handling failed",
                component="response_handler",
                response_id=response_data.get('id')
            ).with_recovery("Check response processing pipeline") from e

    async def _handle_websocket(self, websocket_data: Dict):
        """Handle WebSocket messages"""
        if not self._running:
            logger.debug(
                "Received WebSocket message while not running",
                websocket_data=websocket_data
            )
            return

        try:
            # Validate WebSocket data
            if not isinstance(websocket_data, dict) or not websocket_data:
                raise ValidationError(
                    "Invalid WebSocket data format",
                    field="websocket_data",
                    value=type(websocket_data)
                )

            timestamp = datetime.now()
            
            # Capture screenshot with error handling
            try:
                screenshot_path = await self.screenshot_manager.capture()
            except Exception as e:
                logger.error(
                    "Failed to capture screenshot for WebSocket message",
                    websocket_data=websocket_data,
                    error=str(e),
                    error_type=e.__class__.__name__
                )
                screenshot_path = None

            capture = CaptureData(
                timestamp=timestamp,
                request_data={},
                response_data=None,
                screenshot_path=screenshot_path,
                websocket_data=websocket_data
            )
            
            self.captures.append(capture)
            logger.debug(
                "Successfully processed WebSocket message",
                message_type=websocket_data.get('type'),
                timestamp=timestamp.isoformat()
            )

        except ValidationError as e:
            logger.warning(
                "Invalid WebSocket data received",
                error=str(e),
                error_type=e.__class__.__name__,
                websocket_data=websocket_data
            )
        except Exception as e:
            logger.error(
                "Error handling WebSocket message",
                websocket_data=websocket_data,
                error=str(e),
                error_type=e.__class__.__name__
            )
            raise CaptureError(
                "WebSocket handling failed",
                component="websocket_handler",
                message_type=websocket_data.get('type')
            ).with_recovery("Check WebSocket processing pipeline") from e

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
        try:
            # Process any remaining captures
            while self.captures:
                capture = self.captures.pop(0)
                try:
                    await self.message_queue.publish(
                        "captures",
                        {
                            "session_id": self.session.session_id,
                            "timestamp": capture.timestamp.isoformat(),
                            "data": capture.dict()
                        }
                    )
                except Exception as e:
                    logger.error(
                        "Failed to publish capture data",
                        session_id=self.session.session_id,
                        timestamp=capture.timestamp.isoformat(),
                        error=str(e),
                        error_type=e.__class__.__name__
                    )
                    # Store failed captures for retry
                    self._store_failed_capture(capture)

            logger.info(
                "Cleanup completed for session",
                session_id=self.session.session_id,
                failed_captures=len(getattr(self, '_failed_captures', []))
            )

        except Exception as e:
            logger.critical(
                "Critical error during cleanup",
                session_id=self.session.session_id,
                error=str(e),
                error_type=e.__class__.__name__
            )
            raise ResourceError(
                "Cleanup operation failed",
                resource_type="capture_resources",
                session_id=self.session.session_id
            ).with_recovery("Check system resources and message queue status") from e

    def _store_failed_capture(self, capture: CaptureData) -> None:
        """Store failed captures for later retry"""
        if not hasattr(self, '_failed_captures'):
            self._failed_captures = []
        self._failed_captures.append(capture)