"""Main application window for the slot analyzer."""

# Standard library imports
import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning, message=".*circular import.*")

import logging
import os
import tkinter as tk
from pathlib import Path
from tkinter import ttk, messagebox
from typing import Optional

# Local application imports
from ..message_broker import MessageQueue
from ..services.capture import CaptureService
from ..services.pattern import PatternAnalyzer
from ..services.symbol import SymbolRecognizer
from .components import (
    CaptureMonitor,
    ConfigEditor,
    DataViewer,
    MatrixBackground,
    PatternViewer,
    SessionControls,
    SessionManager,
    SymbolGrid
)
from .theme import apply_theme, HackerTheme

logger = logging.getLogger(__name__)

class SlotAnalyzerApp:
    """Main application window for the slot game analyzer."""

    def __init__(self, root: tk.Tk):
        """Initialize the main application window.

        Args:
            root: The root tkinter window
        """
        self.root = root
        self.root.title("H4CK3R SLOT ANALYZER")

        # Initialize services
        self.capture_service: Optional[CaptureService] = None
        self.symbol_recognizer: Optional[SymbolRecognizer] = None
        self.pattern_analyzer: Optional[PatternAnalyzer] = None
        self.message_queue: Optional[MessageQueue] = None

        # Apply hacker theme
        self.theme = apply_theme(self.root)

        self._init_window()
        self._init_services()
        self._setup_layout()
        self._bind_events()

    def _init_window(self):
        """Initialize the main window settings."""
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)

        # Set window icon if available
        icon_path = Path(__file__).parent / "assets" / "icon.ico"
        if icon_path.exists():
            self.root.iconbitmap(str(icon_path))

        # Create assets directory if it doesn't exist
        assets_dir = Path(__file__).parent / "assets"
        assets_dir.mkdir(exist_ok=True)

        # Configure grid weights
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Create a matrix background
        self.matrix_bg = MatrixBackground(self.root)
        self.matrix_bg.grid(row=0, column=0, sticky="nsew")

        # Create main container with border
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Add status bar at the bottom
        self.status_bar = ttk.Frame(self.root)
        self.status_bar.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 5))

        # Status message
        self.status_message = tk.StringVar(value="System ready. Awaiting command...")
        status_label = ttk.Label(
            self.status_bar,
            textvariable=self.status_message,
            style="Status.TLabel"
        )
        status_label.pack(side="left")

        # Version info
        from ..config import settings
        version_label = ttk.Label(
            self.status_bar,
            text=f"v{settings.APP_VERSION} | SECURE CONNECTION",
            style="Status.TLabel"
        )
        version_label.pack(side="right")

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
        self.status_message.set("Capture data intercepted. Processing...")

    def _handle_symbol_update(self, data):
        """Handle symbol recognition updates."""
        self.symbol_grid.update_grid(data)
        self.status_message.set("Symbol recognition complete. Analyzing patterns...")

    def _handle_pattern_update(self, data):
        """Handle pattern analysis updates."""
        self.pattern_viewer.update_patterns(data)
        self.status_message.set("Pattern analysis complete. Ready for next operation.")

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