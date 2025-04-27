"""
Game layout configuration for symbol recognition.
"""
from dataclasses import dataclass
from typing import List, Tuple
from pathlib import Path

@dataclass
class SymbolTemplate:
    """Represents a symbol template for matching"""
    name: str
    template_path: Path
    confidence_threshold: float = 0.8

@dataclass
class GridPosition:
    """Represents a position on the game grid"""
    row: int
    col: int
    x: int  # X coordinate in pixels
    y: int  # Y coordinate in pixels
    width: int
    height: int

@dataclass
class GameLayout:
    """Game-specific layout configuration"""
    name: str
    grid_size: Tuple[int, int]  # (rows, columns)
    positions: List[GridPosition]
    symbols: List[SymbolTemplate]
    template_dir: Path

    @property
    def symbol_count(self) -> int:
        """Total number of symbol positions in layout"""
        return len(self.positions)

    def validate(self) -> bool:
        """
        Validate layout configuration.
        
        Returns:
            bool: True if layout is valid
        """
        if not self.template_dir.exists():
            return False
            
        # Check if all template files exist
        for symbol in self.symbols:
            if not (self.template_dir / symbol.template_path).exists():
                return False
                
        # Validate grid positions
        rows, cols = self.grid_size
        for pos in self.positions:
            if pos.row >= rows or pos.col >= cols:
                return False
            if pos.width <= 0 or pos.height <= 0:
                return False
                
        return True