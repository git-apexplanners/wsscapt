"""Configuration editor component for managing analyzer settings."""

import tkinter as tk
from tkinter import ttk, messagebox
import logging
from typing import Dict, Any, Optional
import json

logger = logging.getLogger(__name__)

class ConfigEditor(ttk.Frame):
    """Component for editing analyzer configuration settings."""
    
    def __init__(self, parent):
        """Initialize the configuration editor component.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.current_config: Optional[Dict[str, Any]] = None
        self.modified = False
        
        self._init_ui()
        self._load_config()
    
    def _init_ui(self):
        """Initialize the UI components."""
        # Title frame
        title_frame = ttk.Frame(self)
        title_frame.pack(fill="x", padx=5, pady=(0, 5))
        ttk.Label(title_frame, text="Configuration", font=("TkDefaultFont", 10, "bold")).pack(side="left")
        
        # Create notebook for different settings
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Capture settings tab
        self.capture_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.capture_frame, text="Capture")
        
        capture_grid = ttk.Frame(self.capture_frame)
        capture_grid.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Port number
        ttk.Label(capture_grid, text="Proxy Port:").grid(row=0, column=0, sticky="w", padx=(0, 5))
        self.port_var = tk.StringVar(value="8080")
        ttk.Entry(
            capture_grid,
            textvariable=self.port_var,
            width=10
        ).grid(row=0, column=1, sticky="w")
        
        # Screenshot interval
        ttk.Label(capture_grid, text="Screenshot Interval (ms):").grid(row=1, column=0, sticky="w", padx=(0, 5))
        self.interval_var = tk.StringVar(value="1000")
        ttk.Entry(
            capture_grid,
            textvariable=self.interval_var,
            width=10
        ).grid(row=1, column=1, sticky="w")
        
        # Symbol recognition settings tab
        self.symbol_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.symbol_frame, text="Symbol Recognition")
        
        symbol_grid = ttk.Frame(self.symbol_frame)
        symbol_grid.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Confidence threshold
        ttk.Label(symbol_grid, text="Confidence Threshold:").grid(row=0, column=0, sticky="w", padx=(0, 5))
        self.confidence_var = tk.StringVar(value="0.8")
        ttk.Entry(
            symbol_grid,
            textvariable=self.confidence_var,
            width=10
        ).grid(row=0, column=1, sticky="w")
        
        # Grid dimensions
        ttk.Label(symbol_grid, text="Grid Dimensions:").grid(row=1, column=0, sticky="w", padx=(0, 5))
        grid_frame = ttk.Frame(symbol_grid)
        grid_frame.grid(row=1, column=1, sticky="w")
        
        self.rows_var = tk.StringVar(value="3")
        ttk.Entry(
            grid_frame,
            textvariable=self.rows_var,
            width=5
        ).pack(side="left", padx=(0, 5))
        
        ttk.Label(grid_frame, text="x").pack(side="left", padx=5)
        
        self.cols_var = tk.StringVar(value="5")
        ttk.Entry(
            grid_frame,
            textvariable=self.cols_var,
            width=5
        ).pack(side="left", padx=(5, 0))
        
        # Pattern analysis settings tab
        self.pattern_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.pattern_frame, text="Pattern Analysis")
        
        pattern_grid = ttk.Frame(self.pattern_frame)
        pattern_grid.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Minimum sequence length
        ttk.Label(pattern_grid, text="Min Sequence Length:").grid(row=0, column=0, sticky="w", padx=(0, 5))
        self.min_seq_var = tk.StringVar(value="3")
        ttk.Entry(
            pattern_grid,
            textvariable=self.min_seq_var,
            width=10
        ).grid(row=0, column=1, sticky="w")
        
        # Pattern types
        ttk.Label(pattern_grid, text="Pattern Types:").grid(row=1, column=0, sticky="w", padx=(0, 5))
        pattern_frame = ttk.Frame(pattern_grid)
        pattern_frame.grid(row=1, column=1, sticky="w")
        
        self.simple_patterns = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            pattern_frame,
            text="Simple",
            variable=self.simple_patterns
        ).pack(side="left", padx=(0, 5))
        
        self.complex_patterns = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            pattern_frame,
            text="Complex",
            variable=self.complex_patterns
        ).pack(side="left", padx=(0, 5))
        
        self.custom_patterns = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            pattern_frame,
            text="Custom",
            variable=self.custom_patterns
        ).pack(side="left")
        
        # Action buttons
        button_frame = ttk.Frame(self)
        button_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Button(
            button_frame,
            text="Save",
            command=self._save_config
        ).pack(side="left", padx=(0, 5))
        
        ttk.Button(
            button_frame,
            text="Reset",
            command=self._load_config
        ).pack(side="left")
        
        # Bind change events
        self._bind_change_events()
    
    def _bind_change_events(self):
        """Bind events for detecting configuration changes."""
        self.port_var.trace_add("write", self._on_change)
        self.interval_var.trace_add("write", self._on_change)
        self.confidence_var.trace_add("write", self._on_change)
        self.rows_var.trace_add("write", self._on_change)
        self.cols_var.trace_add("write", self._on_change)
        self.min_seq_var.trace_add("write", self._on_change)
        self.simple_patterns.trace_add("write", self._on_change)
        self.complex_patterns.trace_add("write", self._on_change)
        self.custom_patterns.trace_add("write", self._on_change)
    
    def _on_change(self, *args):
        """Handle configuration value changes."""
        self.modified = True
    
    def _load_config(self):
        """Load configuration from file."""
        try:
            with open("config.json", "r") as f:
                config = json.load(f)
                
            # Update UI with loaded values
            self.port_var.set(str(config.get("proxy_port", 8080)))
            self.interval_var.set(str(config.get("screenshot_interval", 1000)))
            self.confidence_var.set(str(config.get("confidence_threshold", 0.8)))
            self.rows_var.set(str(config.get("grid_rows", 3)))
            self.cols_var.set(str(config.get("grid_cols", 5)))
            self.min_seq_var.set(str(config.get("min_sequence_length", 3)))
            self.simple_patterns.set(config.get("simple_patterns", True))
            self.complex_patterns.set(config.get("complex_patterns", True))
            self.custom_patterns.set(config.get("custom_patterns", False))
            
            self.current_config = config
            self.modified = False
            
            logger.info("Configuration loaded successfully")
            
        except FileNotFoundError:
            logger.info("No configuration file found, using defaults")
            self._save_config()  # Create default config
            
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            messagebox.showerror("Error", f"Failed to load configuration: {str(e)}")
    
    def _save_config(self):
        """Save configuration to file."""
        try:
            config = {
                "proxy_port": int(self.port_var.get()),
                "screenshot_interval": int(self.interval_var.get()),
                "confidence_threshold": float(self.confidence_var.get()),
                "grid_rows": int(self.rows_var.get()),
                "grid_cols": int(self.cols_var.get()),
                "min_sequence_length": int(self.min_seq_var.get()),
                "simple_patterns": bool(self.simple_patterns.get()),
                "complex_patterns": bool(self.complex_patterns.get()),
                "custom_patterns": bool(self.custom_patterns.get())
            }
            
            # Validate values
            if config["proxy_port"] < 1 or config["proxy_port"] > 65535:
                raise ValueError("Port number must be between 1 and 65535")
                
            if config["screenshot_interval"] < 100:
                raise ValueError("Screenshot interval must be at least 100ms")
                
            if config["confidence_threshold"] < 0 or config["confidence_threshold"] > 1:
                raise ValueError("Confidence threshold must be between 0 and 1")
                
            if config["grid_rows"] < 1 or config["grid_cols"] < 1:
                raise ValueError("Grid dimensions must be positive")
                
            if config["min_sequence_length"] < 2:
                raise ValueError("Minimum sequence length must be at least 2")
            
            # Save to file
            with open("config.json", "w") as f:
                json.dump(config, f, indent=2)
            
            self.current_config = config
            self.modified = False
            
            logger.info("Configuration saved successfully")
            messagebox.showinfo("Success", "Configuration saved successfully")
            
        except ValueError as e:
            logger.error(f"Invalid configuration value: {e}")
            messagebox.showerror("Error", str(e))
            
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
            messagebox.showerror("Error", f"Failed to save configuration: {str(e)}")
    
    def get_config(self) -> Dict[str, Any]:
        """Get the current configuration.
        
        Returns:
            Dictionary containing current configuration values
        """
        return self.current_config.copy() if self.current_config else {}