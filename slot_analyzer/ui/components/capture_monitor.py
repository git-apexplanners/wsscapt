"""Capture monitoring component for displaying real-time capture status and data."""

import tkinter as tk
from tkinter import ttk
import logging
from PIL import Image, ImageTk
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class CaptureMonitor(ttk.Frame):
    """Component for monitoring and displaying capture status and screenshots."""
    
    def __init__(self, parent):
        """Initialize the capture monitor component.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.screenshot_label: Optional[ttk.Label] = None
        self.status_var = tk.StringVar(value="Waiting for capture...")
        
        self._init_ui()
    
    def _init_ui(self):
        """Initialize the UI components."""
        # Title
        title_frame = ttk.Frame(self)
        title_frame.pack(fill="x", padx=5, pady=(0, 5))
        ttk.Label(title_frame, text="Capture Monitor", font=("TkDefaultFont", 10, "bold")).pack(side="left")
        self.status_label = ttk.Label(title_frame, textvariable=self.status_var)
        self.status_label.pack(side="right")
        
        # Screenshot display
        self.screenshot_frame = ttk.LabelFrame(self, text="Current Screenshot")
        self.screenshot_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Placeholder for screenshot
        self.screenshot_label = ttk.Label(self.screenshot_frame, text="No screenshot available")
        self.screenshot_label.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Capture details
        details_frame = ttk.LabelFrame(self, text="Capture Details")
        details_frame.pack(fill="x", padx=5, pady=5)
        
        # Grid for capture details
        details_grid = ttk.Frame(details_frame)
        details_grid.pack(fill="x", padx=5, pady=5)
        
        # Request count
        ttk.Label(details_grid, text="Requests:").grid(row=0, column=0, sticky="w", padx=(0, 5))
        self.request_count = tk.StringVar(value="0")
        ttk.Label(details_grid, textvariable=self.request_count).grid(row=0, column=1, sticky="w")
        
        # Last capture time
        ttk.Label(details_grid, text="Last Capture:").grid(row=1, column=0, sticky="w", padx=(0, 5))
        self.last_capture = tk.StringVar(value="N/A")
        ttk.Label(details_grid, textvariable=self.last_capture).grid(row=1, column=1, sticky="w")
    
    def update_display(self, data: Dict[str, Any]):
        """Update the display with new capture data.
        
        Args:
            data: Dictionary containing capture update information
        """
        try:
            # Update status
            status = data.get("status", "Unknown")
            self.status_var.set(f"Status: {status}")
            
            # Update screenshot if available
            screenshot = data.get("screenshot")
            if screenshot and isinstance(screenshot, Image.Image):
                # Resize image to fit display while maintaining aspect ratio
                display_size = (400, 300)  # Maximum display size
                screenshot.thumbnail(display_size, Image.Resampling.LANCZOS)
                
                # Convert to PhotoImage for display
                photo = ImageTk.PhotoImage(screenshot)
                
                # Update or create screenshot label
                if self.screenshot_label:
                    self.screenshot_label.configure(image=photo, text="")
                    self.screenshot_label.image = photo  # Keep reference to prevent garbage collection
            
            # Update capture details
            if "request_count" in data:
                self.request_count.set(str(data["request_count"]))
            if "last_capture_time" in data:
                self.last_capture.set(data["last_capture_time"])
                
            logger.debug("Capture monitor display updated successfully")
            
        except Exception as e:
            logger.error(f"Error updating capture monitor display: {e}")
            self.status_var.set("Error updating display")

    def clear_display(self):
        """Clear the display and reset to initial state."""
        self.status_var.set("Waiting for capture...")
        if self.screenshot_label:
            self.screenshot_label.configure(image="", text="No screenshot available")
        self.request_count.set("0")
        self.last_capture.set("N/A")