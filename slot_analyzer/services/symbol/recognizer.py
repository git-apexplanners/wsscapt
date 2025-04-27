"""
Symbol recognition module for extracting and identifying slot symbols.
"""
import cv2
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from loguru import logger

from ...config.layouts import GameLayout, GridPosition, SymbolTemplate
from ...errors import CaptureError

class SymbolRecognizer:
    """Handles symbol recognition and extraction from screenshots"""

    def __init__(self, layout: GameLayout):
        """
        Initialize symbol recognizer with game layout.
        
        Args:
            layout: Game-specific layout configuration
        """
        if not layout.validate():
            raise ValueError("Invalid game layout configuration")
            
        self.layout = layout
        self._symbol_templates: Dict[str, np.ndarray] = {}
        self._load_templates()
        
    def _load_templates(self):
        """Load and cache symbol templates"""
        for symbol in self.layout.symbols:
            template_path = self.layout.template_dir / symbol.template_path
            template = cv2.imread(str(template_path))
            if template is None:
                raise ValueError(f"Failed to load template: {template_path}")
            self._symbol_templates[symbol.name] = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
            
    def extract_symbols(self, screenshot_path: Path) -> List[Tuple[str, GridPosition, float]]:
        """
        Extract symbols from a screenshot based on game layout.
        
        Args:
            screenshot_path: Path to screenshot image
            
        Returns:
            List of tuples containing (symbol_name, position, confidence)
            
        Raises:
            CaptureError: If screenshot processing fails
        """
        try:
            # Load and preprocess screenshot
            screenshot = cv2.imread(str(screenshot_path))
            if screenshot is None:
                raise CaptureError(f"Failed to load screenshot: {screenshot_path}")
                
            gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
            results = []
            
            # Process each grid position
            for position in self.layout.positions:
                # Extract region of interest
                roi = self._extract_roi(gray, position)
                if roi is None:
                    continue
                    
                # Find best matching symbol
                symbol_match = self._match_symbol(roi)
                if symbol_match:
                    symbol_name, confidence = symbol_match
                    results.append((symbol_name, position, confidence))
                    
            return results
            
        except Exception as e:
            logger.error(f"Symbol extraction failed: {str(e)}")
            raise CaptureError(f"Symbol extraction failed: {str(e)}")
            
    def _extract_roi(self, screenshot: np.ndarray, position: GridPosition) -> Optional[np.ndarray]:
        """Extract region of interest for a grid position"""
        try:
            return screenshot[
                position.y:position.y + position.height,
                position.x:position.x + position.width
            ]
        except IndexError:
            logger.warning(f"Invalid ROI coordinates for position: {position}")
            return None
            
    def _match_symbol(self, roi: np.ndarray) -> Optional[Tuple[str, float]]:
        """
        Find best matching symbol template for region of interest.
        
        Returns:
            Tuple of (symbol_name, confidence) or None if no match
        """
        best_match = None
        best_confidence = 0
        
        for symbol in self.layout.symbols:
            template = self._symbol_templates[symbol.name]
            
            # Resize template to match ROI size if needed
            if template.shape != roi.shape:
                template = cv2.resize(template, (roi.shape[1], roi.shape[0]))
                
            # Perform template matching
            result = cv2.matchTemplate(roi, template, cv2.TM_CCOEFF_NORMED)
            confidence = result.max()
            
            if confidence > symbol.confidence_threshold and confidence > best_confidence:
                best_match = symbol.name
                best_confidence = confidence
                
        return (best_match, best_confidence) if best_match else None
        
    def train_symbol(self, symbol_name: str, template_image: Path, confidence_threshold: float = 0.8):
        """
        Add or update a symbol template for recognition.
        
        Args:
            symbol_name: Name of the symbol
            template_image: Path to template image
            confidence_threshold: Minimum confidence for matching
        """
        template = cv2.imread(str(template_image))
        if template is None:
            raise ValueError(f"Failed to load template image: {template_image}")
            
        # Create new template
        template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        self._symbol_templates[symbol_name] = template_gray
        
        # Update layout configuration
        template_path = template_image.relative_to(self.layout.template_dir)
        self.layout.symbols.append(SymbolTemplate(
            name=symbol_name,
            template_path=template_path,
            confidence_threshold=confidence_threshold
        ))