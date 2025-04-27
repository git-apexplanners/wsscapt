"""
Symbol recognition service for slot game analysis.
"""
from pathlib import Path
from typing import Optional, List, Tuple

from loguru import logger
from kombu import Connection, Queue, Consumer, Message

from ...config import get_settings
from ...config.layouts import GameLayout, GridPosition
from .recognizer import SymbolRecognizer

class SymbolRecognitionService:
    """Service for managing symbol recognition and queue integration"""
    
    def __init__(self, layout: GameLayout):
        """Initialize symbol recognition service"""
        self.recognizer = SymbolRecognizer(layout)
        self._setup_queue()
        
    def _setup_queue(self):
        """Setup message queue connection and consumer"""
        settings = get_settings()
        self.connection = Connection(settings.get("broker_url", "redis://localhost:6379/0"))
        self.queue = Queue("screenshots", routing_key="screenshot.captured")
        
    def start(self):
        """Start consuming screenshot messages"""
        with Consumer(self.connection, queues=[self.queue], callbacks=[self._process_screenshot]):
            logger.info("Symbol recognition service started")
            while True:
                try:
                    self.connection.drain_events()
                except KeyboardInterrupt:
                    break
                    
    def _process_screenshot(self, body: dict, message: Message):
        """Process screenshot message from queue"""
        try:
            screenshot_path = Path(body["path"])
            if not screenshot_path.exists():
                logger.error(f"Screenshot not found: {screenshot_path}")
                message.ack()
                return
                
            # Extract symbols
            symbols = self.recognizer.extract_symbols(screenshot_path)
            
            # Store results (timestamp from screenshot name for sync)
            timestamp = screenshot_path.stem.split("_")[1]
            self._store_results(symbols, timestamp)
            
            message.ack()
            
        except Exception as e:
            logger.error(f"Failed to process screenshot: {str(e)}")
            message.reject()
            
    def _store_results(self, symbols: List[Tuple[str, GridPosition, float]], timestamp: str):
        """Store symbol recognition results"""
        # TODO: Implement result storage (Redis/DB)
        # For now, just log results
        for symbol_name, position, confidence in symbols:
            logger.info(
                f"Symbol detected: {symbol_name} at ({position.row}, {position.col}) "
                f"confidence: {confidence:.2f}"
            )