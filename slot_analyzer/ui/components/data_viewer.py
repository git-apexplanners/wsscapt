"""Data viewer component for displaying request/response data with syntax highlighting."""

import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
import json
import logging
from typing import Dict, Any, Optional
from PIL import Image, ImageTk
import datetime

logger = logging.getLogger(__name__)

class DataViewer(ttk.Frame):
    """Component for viewing detailed request/response data."""
    
    def __init__(self, parent):
        """Initialize the data viewer component.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.current_request: Optional[Dict[str, Any]] = None
        self.current_response: Optional[Dict[str, Any]] = None
        self.current_screenshot: Optional[Image.Image] = None
        
        self._init_ui()
    
    def _init_ui(self):
        """Initialize the UI components."""
        # Title frame
        title_frame = ttk.Frame(self)
        title_frame.pack(fill="x", padx=5, pady=(0, 5))
        ttk.Label(title_frame, text="Data Viewer", font=("TkDefaultFont", 10, "bold")).pack(side="left")
        
        # Create notebook for different views
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Request/Response tab
        self.req_resp_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.req_resp_frame, text="Request/Response")
        
        # Request panel
        request_frame = ttk.LabelFrame(self.req_resp_frame, text="Request")
        request_frame.pack(fill="both", expand=True, padx=5, pady=(5, 2))
        
        self.request_text = ScrolledText(
            request_frame,
            wrap=tk.NONE,
            width=40,
            height=8,
            font=("Courier", 9)
        )
        self.request_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Response panel
        response_frame = ttk.LabelFrame(self.req_resp_frame, text="Response")
        response_frame.pack(fill="both", expand=True, padx=5, pady=(2, 5))
        
        self.response_text = ScrolledText(
            response_frame,
            wrap=tk.NONE,
            width=40,
            height=8,
            font=("Courier", 9)
        )
        self.response_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Screenshot tab
        self.screenshot_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.screenshot_frame, text="Screenshot")
        
        # Screenshot display
        self.screenshot_label = ttk.Label(self.screenshot_frame, text="No screenshot available")
        self.screenshot_label.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Details tab
        self.details_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.details_frame, text="Details")
        
        # Details grid
        details_grid = ttk.Frame(self.details_frame)
        details_grid.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Timestamp
        ttk.Label(details_grid, text="Timestamp:").grid(row=0, column=0, sticky="w", padx=(0, 5))
        self.timestamp_var = tk.StringVar(value="N/A")
        ttk.Label(details_grid, textvariable=self.timestamp_var).grid(row=0, column=1, sticky="w")
        
        # Request size
        ttk.Label(details_grid, text="Request Size:").grid(row=1, column=0, sticky="w", padx=(0, 5))
        self.request_size_var = tk.StringVar(value="N/A")
        ttk.Label(details_grid, textvariable=self.request_size_var).grid(row=1, column=1, sticky="w")
        
        # Response size
        ttk.Label(details_grid, text="Response Size:").grid(row=2, column=0, sticky="w", padx=(0, 5))
        self.response_size_var = tk.StringVar(value="N/A")
        ttk.Label(details_grid, textvariable=self.response_size_var).grid(row=2, column=1, sticky="w")
        
        # Configure text tags for syntax highlighting
        self._configure_text_tags()
    
    def _configure_text_tags(self):
        """Configure syntax highlighting tags."""
        # JSON key highlighting
        self.request_text.tag_configure("key", foreground="blue")
        self.response_text.tag_configure("key", foreground="blue")
        
        # JSON string value highlighting
        self.request_text.tag_configure("string", foreground="green")
        self.response_text.tag_configure("string", foreground="green")
        
        # JSON number highlighting
        self.request_text.tag_configure("number", foreground="orange")
        self.response_text.tag_configure("number", foreground="orange")
        
        # JSON boolean/null highlighting
        self.request_text.tag_configure("keyword", foreground="purple")
        self.response_text.tag_configure("keyword", foreground="purple")
    
    def _highlight_json(self, text_widget: ScrolledText, json_str: str):
        """Apply syntax highlighting to JSON text.
        
        Args:
            text_widget: Text widget to apply highlighting to
            json_str: JSON string to highlight
        """
        text_widget.delete("1.0", tk.END)
        
        try:
            # Format JSON
            parsed = json.loads(json_str)
            formatted = json.dumps(parsed, indent=2)
            
            # Insert formatted text
            text_widget.insert("1.0", formatted)
            
            # Apply syntax highlighting
            lines = formatted.split("\n")
            line_num = 1
            
            for line in lines:
                # Highlight keys
                if ":" in line:
                    key_end = line.find(":")
                    text_widget.tag_add(
                        "key",
                        f"{line_num}.{line.find('"')}",
                        f"{line_num}.{key_end}"
                    )
                
                # Highlight string values
                quote_positions = []
                pos = 0
                while True:
                    pos = line.find('"', pos)
                    if pos == -1:
                        break
                    quote_positions.append(pos)
                    pos += 1
                
                for i in range(0, len(quote_positions), 2):
                    if i + 1 < len(quote_positions):
                        text_widget.tag_add(
                            "string",
                            f"{line_num}.{quote_positions[i]}",
                            f"{line_num}.{quote_positions[i+1]+1}"
                        )
                
                # Highlight numbers
                for i, char in enumerate(line):
                    if char.isdigit():
                        text_widget.tag_add(
                            "number",
                            f"{line_num}.{i}",
                            f"{line_num}.{i+1}"
                        )
                
                # Highlight keywords
                for keyword in ["true", "false", "null"]:
                    pos = 0
                    while True:
                        pos = line.find(keyword, pos)
                        if pos == -1:
                            break
                        text_widget.tag_add(
                            "keyword",
                            f"{line_num}.{pos}",
                            f"{line_num}.{pos+len(keyword)}"
                        )
                        pos += len(keyword)
                
                line_num += 1
                
        except json.JSONDecodeError:
            # If not valid JSON, just insert plain text
            text_widget.insert("1.0", json_str)
    
    def update_request_data(self, data: Dict[str, Any]):
        """Update the display with new request/response data.
        
        Args:
            data: Dictionary containing request/response information
        """
        try:
            # Store current data
            self.current_request = data.get("request")
            self.current_response = data.get("response")
            self.current_screenshot = data.get("screenshot")
            
            # Update request/response text
            if self.current_request:
                self._highlight_json(
                    self.request_text,
                    json.dumps(self.current_request)
                )
            
            if self.current_response:
                self._highlight_json(
                    self.response_text,
                    json.dumps(self.current_response)
                )
            
            # Update screenshot if available
            if self.current_screenshot and isinstance(self.current_screenshot, Image.Image):
                # Resize image to fit display while maintaining aspect ratio
                display_size = (400, 300)
                self.current_screenshot.thumbnail(display_size, Image.Resampling.LANCZOS)
                
                # Convert to PhotoImage for display
                photo = ImageTk.PhotoImage(self.current_screenshot)
                self.screenshot_label.configure(image=photo, text="")
                self.screenshot_label.image = photo
            
            # Update details
            timestamp = data.get("timestamp")
            if timestamp:
                self.timestamp_var.set(
                    datetime.datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
                )
            
            if self.current_request:
                self.request_size_var.set(f"{len(str(self.current_request))} bytes")
            
            if self.current_response:
                self.response_size_var.set(f"{len(str(self.current_response))} bytes")
            
            logger.debug("Data viewer updated successfully")
            
        except Exception as e:
            logger.error(f"Error updating data viewer: {e}")
    
    def clear_data(self):
        """Clear all data and reset to initial state."""
        self.request_text.delete("1.0", tk.END)
        self.response_text.delete("1.0", tk.END)
        self.screenshot_label.configure(image="", text="No screenshot available")
        self.timestamp_var.set("N/A")
        self.request_size_var.set("N/A")
        self.response_size_var.set("N/A")
        
        self.current_request = None
        self.current_response = None
        self.current_screenshot = None