"""Symbol grid component for displaying extracted symbols in a grid layout."""

import tkinter as tk
from tkinter import ttk
import logging
from typing import Optional, List, Dict, Any
from ..services.symbol import SymbolRecognizer

logger = logging.getLogger(__name__)

class SymbolGrid(ttk.Frame):
    """Component for displaying the slot machine symbol grid."""
    
    def __init__(self, parent, symbol_recognizer: Optional[SymbolRecognizer] = None):
        """Initialize the symbol grid component.
        
        Args:
            parent: Parent widget
            symbol_recognizer: Instance of SymbolRecognizer for symbol updates
        """
        super().__init__(parent)
        
        self.symbol_recognizer = symbol_recognizer
        self.cells: List[List[ttk.Label]] = []
        self.current_symbols: List[List[str]] = []
        
        self._init_ui()
    
    def _init_ui(self):
        """Initialize the UI components."""
        # Title frame
        title_frame = ttk.Frame(self)
        title_frame.pack(fill="x", padx=5, pady=(0, 5))
        ttk.Label(title_frame, text="Symbol Grid", font=("TkDefaultFont", 10, "bold")).pack(side="left")
        
        # Grid frame
        self.grid_frame = ttk.LabelFrame(self, text="Current Symbols")
        self.grid_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Create grid cells (3x5 grid for typical slot layout)
        for row in range(3):
            cell_row = []
            for col in range(5):
                cell = ttk.Label(
                    self.grid_frame,
                    text="?",
                    width=4,
                    anchor="center",
                    style="Grid.TLabel",
                    relief="solid",
                    padding=10
                )
                cell.grid(row=row, column=col, padx=2, pady=2, sticky="nsew")
                cell_row.append(cell)
            self.cells.append(cell_row)
            
        # Configure grid weights
        for i in range(5):
            self.grid_frame.grid_columnconfigure(i, weight=1)
        for i in range(3):
            self.grid_frame.grid_rowconfigure(i, weight=1)
        
        # Statistics frame
        stats_frame = ttk.LabelFrame(self, text="Statistics")
        stats_frame.pack(fill="x", padx=5, pady=5)
        
        # Grid for statistics
        stats_grid = ttk.Frame(stats_frame)
        stats_grid.pack(fill="x", padx=5, pady=5)
        
        # Spins count
        ttk.Label(stats_grid, text="Total Spins:").grid(row=0, column=0, sticky="w", padx=(0, 5))
        self.spins_count = tk.StringVar(value="0")
        ttk.Label(stats_grid, textvariable=self.spins_count).grid(row=0, column=1, sticky="w")
        
        # Recognition accuracy
        ttk.Label(stats_grid, text="Recognition Rate:").grid(row=1, column=0, sticky="w", padx=(0, 5))
        self.recognition_rate = tk.StringVar(value="0%")
        ttk.Label(stats_grid, textvariable=self.recognition_rate).grid(row=1, column=1, sticky="w")
        
        # Configure styles
        style = ttk.Style()
        style.configure("Grid.TLabel", font=("TkDefaultFont", 9))
    
    def update_grid(self, data: Dict[str, Any]):
        """Update the grid with new symbol data.
        
        Args:
            data: Dictionary containing symbol update information
        """
        try:
            symbols = data.get("symbols", [])
            if not symbols or not isinstance(symbols, list):
                logger.warning("Invalid symbol data received")
                return
                
            # Update grid cells
            for row in range(min(len(symbols), len(self.cells))):
                row_symbols = symbols[row]
                for col in range(min(len(row_symbols), len(self.cells[row]))):
                    symbol = row_symbols[col]
                    cell = self.cells[row][col]
                    cell.configure(text=symbol if symbol else "?")
            
            # Update statistics
            if "total_spins" in data:
                self.spins_count.set(str(data["total_spins"]))
            if "recognition_rate" in data:
                self.recognition_rate.set(f"{data['recognition_rate']:.1f}%")
                
            # Store current symbols
            self.current_symbols = symbols
            
            logger.debug("Symbol grid updated successfully")
            
        except Exception as e:
            logger.error(f"Error updating symbol grid: {e}")
    
    def clear_grid(self):
        """Clear the grid and reset to initial state."""
        for row in self.cells:
            for cell in row:
                cell.configure(text="?")
        self.spins_count.set("0")
        self.recognition_rate.set("0%")
        self.current_symbols = []

    def get_current_symbols(self) -> List[List[str]]:
        """Get the current symbol grid state.
        
        Returns:
            List of lists containing current symbols
        """
        return self.current_symbols.copy()