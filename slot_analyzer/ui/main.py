"""Main application window for the slot analyzer."""

import tkinter as tk
from tkinter import ttk, messagebox
import logging
from typing import Optional

from ..services.capture import CaptureService
from ..services.symbol import SymbolRecognizer
from ..services.pattern import PatternAnalyzer
from ..queue import MessageQueue
from .components import (
    CaptureMonitor,
    SymbolGrid,
    PatternViewer,
    SessionControls,
    DataViewer,
    SessionManager,
    ConfigEditor
)

logger = logging.getLogger(__name__)

class SlotAnalyzerApp:
    """Main application window for the slot game analyzer."""
    
    def __init__(self, root: tk.Tk):
        """Initialize the main application window.
        
        Args:
            root: The root tkinter window
        """
        self.root = root
        self.root.title("Slot Game Analyzer")
        
        # Initialize services
        self.capture_service: Optional[CaptureService] = None
        self.symbol_recognizer: Optional[SymbolRecognizer] = None
        self.pattern_analyzer: Optional[PatternAnalyzer] = None
        self.message_queue: Optional[MessageQueue] = None
        
        self._init_window()
        self._init_services()
        self._setup_layout()
        self._bind_events()
    
    def _init_window(self):
        """Initialize the main window settings."""
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)
        
        # Configure grid weights
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Create main container
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Configure main frame grid
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=1)
    
    def _init_services(self):
        """Initialize and connect to backend services."""
        try:
            self.capture_service = CaptureService()
            self.symbol_recognizer = SymbolRecognizer()
            self.pattern_analyzer = PatternAnalyzer()
            self.message_queue = MessageQueue()
            logger.info("Services initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize services: {e}")
            messagebox.showerror("Error", f"Failed to initialize services: {str(e)}")
    
    def _setup_layout(self):
        """Set up the main application layout."""
        # Create and position components
        self.session_controls = SessionControls(self.main_frame, self.capture_service)
        self.session_controls.grid(row=0, column=0, columnspan=3, sticky="ew", padx=5, pady=5)
        
        # Left panel - Session management and configuration
        left_panel = ttk.Frame(self.main_frame)
        left_panel.grid(row=1, column=0, sticky="nsew", padx=5)
        self.session_manager = SessionManager(left_panel)
        self.session_manager.pack(fill="both", expand=True, pady=(0, 5))
        self.config_editor = ConfigEditor(left_panel)
        self.config_editor.pack(fill="both", expand=True)
        
        # Center panel - Symbol grid and pattern analysis
        center_panel = ttk.Frame(self.main_frame)
        center_panel.grid(row=1, column=1, sticky="nsew", padx=5)
        self.symbol_grid = SymbolGrid(center_panel, self.symbol_recognizer)
        self.symbol_grid.pack(fill="both", expand=True, pady=(0, 5))
        self.pattern_viewer = PatternViewer(center_panel, self.pattern_analyzer)
        self.pattern_viewer.pack(fill="both", expand=True)
        
        # Right panel - Capture monitoring and data viewing
        right_panel = ttk.Frame(self.main_frame)
        right_panel.grid(row=1, column=2, sticky="nsew", padx=5)
        self.capture_monitor = CaptureMonitor(right_panel)
        self.capture_monitor.pack(fill="both", expand=True, pady=(0, 5))
        self.data_viewer = DataViewer(right_panel)
        self.data_viewer.pack(fill="both", expand=True)
    
    def _bind_events(self):
        """Bind event handlers."""
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.message_queue.subscribe("capture_update", self._handle_capture_update)
        self.message_queue.subscribe("symbol_update", self._handle_symbol_update)
        self.message_queue.subscribe("pattern_update", self._handle_pattern_update)
        
    def _handle_capture_update(self, data):
        """Handle capture service updates."""
        self.capture_monitor.update_display(data)
        self.data_viewer.update_request_data(data)
    
    def _handle_symbol_update(self, data):
        """Handle symbol recognition updates."""
        self.symbol_grid.update_grid(data)
    
    def _handle_pattern_update(self, data):
        """Handle pattern analysis updates."""
        self.pattern_viewer.update_patterns(data)
    
    def _on_close(self):
        """Handle application shutdown."""
        try:
            if self.capture_service:
                self.capture_service.stop()
            if self.message_queue:
                self.message_queue.close()
            logger.info("Application shutdown complete")
            self.root.destroy()
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
            self.root.destroy()

    def run(self):
        """Start the main application loop."""
        try:
            self.root.mainloop()
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
            raise