"""Pattern viewer component for displaying pattern analysis results."""

import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
import json
import logging
from typing import Optional, Dict, Any, List
from ..services.pattern import PatternAnalyzer

logger = logging.getLogger(__name__)

class PatternViewer(ttk.Frame):
    """Component for displaying pattern analysis results."""
    
    def __init__(self, parent, pattern_analyzer: Optional[PatternAnalyzer] = None):
        """Initialize the pattern viewer component.
        
        Args:
            parent: Parent widget
            pattern_analyzer: Instance of PatternAnalyzer for pattern updates
        """
        super().__init__(parent)
        
        self.pattern_analyzer = pattern_analyzer
        self.current_patterns: List[Dict[str, Any]] = []
        
        self._init_ui()
    
    def _init_ui(self):
        """Initialize the UI components."""
        # Title frame
        title_frame = ttk.Frame(self)
        title_frame.pack(fill="x", padx=5, pady=(0, 5))
        ttk.Label(title_frame, text="Pattern Analysis", font=("TkDefaultFont", 10, "bold")).pack(side="left")
        
        # Create notebook for different views
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Active patterns tab
        self.active_patterns_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.active_patterns_frame, text="Active Patterns")
        
        # Pattern tree
        self.pattern_tree = ttk.Treeview(
            self.active_patterns_frame,
            columns=("type", "confidence", "last_seen"),
            show="headings"
        )
        
        # Configure columns
        self.pattern_tree.heading("type", text="Pattern Type")
        self.pattern_tree.heading("confidence", text="Confidence")
        self.pattern_tree.heading("last_seen", text="Last Seen")
        
        self.pattern_tree.column("type", width=150)
        self.pattern_tree.column("confidence", width=100)
        self.pattern_tree.column("last_seen", width=150)
        
        # Add scrollbar
        tree_scroll = ttk.Scrollbar(
            self.active_patterns_frame,
            orient="vertical",
            command=self.pattern_tree.yview
        )
        self.pattern_tree.configure(yscrollcommand=tree_scroll.set)
        
        # Pack tree and scrollbar
        self.pattern_tree.pack(side="left", fill="both", expand=True)
        tree_scroll.pack(side="right", fill="y")
        
        # Pattern details tab
        self.details_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.details_frame, text="Pattern Details")
        
        # Details text area
        self.details_text = ScrolledText(
            self.details_frame,
            wrap=tk.WORD,
            width=40,
            height=10
        )
        self.details_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Statistics tab
        self.stats_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.stats_frame, text="Statistics")
        
        # Statistics grid
        stats_grid = ttk.Frame(self.stats_frame)
        stats_grid.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Total patterns
        ttk.Label(stats_grid, text="Total Patterns:").grid(row=0, column=0, sticky="w", padx=(0, 5))
        self.total_patterns = tk.StringVar(value="0")
        ttk.Label(stats_grid, textvariable=self.total_patterns).grid(row=0, column=1, sticky="w")
        
        # Active patterns
        ttk.Label(stats_grid, text="Active Patterns:").grid(row=1, column=0, sticky="w", padx=(0, 5))
        self.active_patterns = tk.StringVar(value="0")
        ttk.Label(stats_grid, textvariable=self.active_patterns).grid(row=1, column=1, sticky="w")
        
        # Average confidence
        ttk.Label(stats_grid, text="Avg Confidence:").grid(row=2, column=0, sticky="w", padx=(0, 5))
        self.avg_confidence = tk.StringVar(value="0%")
        ttk.Label(stats_grid, textvariable=self.avg_confidence).grid(row=2, column=1, sticky="w")
        
        # Bind tree selection event
        self.pattern_tree.bind("<<TreeviewSelect>>", self._on_pattern_selected)
    
    def update_patterns(self, data: Dict[str, Any]):
        """Update the display with new pattern data.
        
        Args:
            data: Dictionary containing pattern update information
        """
        try:
            patterns = data.get("patterns", [])
            if not patterns or not isinstance(patterns, list):
                logger.warning("Invalid pattern data received")
                return
            
            # Clear existing items
            for item in self.pattern_tree.get_children():
                self.pattern_tree.delete(item)
            
            # Add new patterns
            for pattern in patterns:
                self.pattern_tree.insert(
                    "",
                    "end",
                    values=(
                        pattern.get("type", "Unknown"),
                        f"{pattern.get('confidence', 0):.1f}%",
                        pattern.get("last_seen", "N/A")
                    )
                )
            
            # Update statistics
            self.total_patterns.set(str(data.get("total_patterns", 0)))
            self.active_patterns.set(str(len(patterns)))
            self.avg_confidence.set(f"{data.get('avg_confidence', 0):.1f}%")
            
            # Store current patterns
            self.current_patterns = patterns
            
            logger.debug("Pattern viewer updated successfully")
            
        except Exception as e:
            logger.error(f"Error updating pattern viewer: {e}")
    
    def _on_pattern_selected(self, event):
        """Handle pattern selection in tree view."""
        selection = self.pattern_tree.selection()
        if not selection:
            return
            
        # Get selected pattern details
        item = selection[0]
        pattern_type = self.pattern_tree.item(item)["values"][0]
        
        # Find pattern details
        pattern = next(
            (p for p in self.current_patterns if p["type"] == pattern_type),
            None
        )
        
        if pattern:
            # Format pattern details
            details = json.dumps(pattern, indent=2)
            self.details_text.delete("1.0", tk.END)
            self.details_text.insert("1.0", details)
    
    def clear_patterns(self):
        """Clear all patterns and reset to initial state."""
        for item in self.pattern_tree.get_children():
            self.pattern_tree.delete(item)
        self.details_text.delete("1.0", tk.END)
        self.total_patterns.set("0")
        self.active_patterns.set("0")
        self.avg_confidence.set("0%")
        self.current_patterns = []