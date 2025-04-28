"""Theme module for the slot analyzer application.

This module provides a hacker-style theme for the application UI.
"""

import tkinter as tk
from tkinter import ttk, font
import logging
import os
import platform
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Color scheme
COLORS = {
    # Base colors
    "bg_dark": "#0a0a0a",  # Almost black background
    "bg_medium": "#121212",  # Dark gray for panels
    "bg_light": "#1a1a1a",  # Lighter gray for input fields
    
    # Accent colors
    "accent_primary": "#00ff41",  # Matrix green
    "accent_secondary": "#0077ff",  # Neon blue
    "accent_tertiary": "#ff00aa",  # Neon pink
    "accent_warning": "#ffcc00",  # Warning yellow
    "accent_danger": "#ff3333",  # Danger red
    
    # Text colors
    "text_primary": "#e0e0e0",  # Light gray for main text
    "text_secondary": "#a0a0a0",  # Medium gray for secondary text
    "text_disabled": "#505050",  # Dark gray for disabled text
    "text_highlight": "#ffffff",  # White for highlighted text
    
    # Border colors
    "border_dark": "#000000",  # Black borders
    "border_light": "#333333",  # Light borders
    "border_highlight": "#00ff41",  # Highlighted borders
}

# Font configurations
FONTS = {
    "main": {
        "family": "Consolas" if platform.system() == "Windows" else "Courier",
        "size": 9,
        "weight": "normal",
    },
    "title": {
        "family": "Consolas" if platform.system() == "Windows" else "Courier",
        "size": 10,
        "weight": "bold",
    },
    "code": {
        "family": "Consolas" if platform.system() == "Windows" else "Courier",
        "size": 9,
        "weight": "normal",
    },
    "button": {
        "family": "Consolas" if platform.system() == "Windows" else "Courier",
        "size": 9,
        "weight": "bold",
    },
    "small": {
        "family": "Consolas" if platform.system() == "Windows" else "Courier",
        "size": 8,
        "weight": "normal",
    },
}

class HackerTheme:
    """Hacker-style theme for the application."""
    
    def __init__(self, root: tk.Tk):
        """Initialize the theme.
        
        Args:
            root: The root tkinter window
        """
        self.root = root
        self.style = ttk.Style()
        self._custom_fonts: Dict[str, font.Font] = {}
        
        # Initialize theme
        self._init_fonts()
        self._configure_ttk_styles()
        self._configure_tk_styles()
        
        logger.info("Hacker theme initialized")
    
    def _init_fonts(self):
        """Initialize custom fonts."""
        for name, config in FONTS.items():
            self._custom_fonts[name] = font.Font(
                family=config["family"],
                size=config["size"],
                weight=config["weight"]
            )
        
        # Set default font
        self.root.option_add("*Font", self._custom_fonts["main"])
    
    def _configure_ttk_styles(self):
        """Configure ttk widget styles."""
        # Use 'clam' as base theme as it's more customizable
        self.style.theme_use("clam")
        
        # Configure TFrame
        self.style.configure(
            "TFrame",
            background=COLORS["bg_medium"]
        )
        
        # Configure TLabel
        self.style.configure(
            "TLabel",
            background=COLORS["bg_medium"],
            foreground=COLORS["text_primary"],
            font=self._custom_fonts["main"]
        )
        
        # Configure TButton
        self.style.configure(
            "TButton",
            background=COLORS["bg_light"],
            foreground=COLORS["text_primary"],
            borderwidth=1,
            relief="flat",
            font=self._custom_fonts["button"]
        )
        self.style.map(
            "TButton",
            background=[
                ("active", COLORS["bg_light"]),
                ("pressed", COLORS["bg_dark"])
            ],
            foreground=[
                ("active", COLORS["accent_primary"]),
                ("pressed", COLORS["accent_primary"])
            ],
            bordercolor=[
                ("active", COLORS["accent_primary"]),
                ("focus", COLORS["accent_primary"])
            ]
        )
        
        # Configure Action.TButton (for primary actions)
        self.style.configure(
            "Action.TButton",
            background=COLORS["bg_light"],
            foreground=COLORS["accent_primary"],
            borderwidth=1,
            relief="flat",
            font=self._custom_fonts["button"]
        )
        self.style.map(
            "Action.TButton",
            background=[
                ("active", COLORS["bg_light"]),
                ("pressed", COLORS["bg_dark"])
            ],
            foreground=[
                ("active", COLORS["accent_primary"]),
                ("pressed", COLORS["accent_primary"])
            ],
            bordercolor=[
                ("active", COLORS["accent_primary"]),
                ("focus", COLORS["accent_primary"])
            ]
        )
        
        # Configure Danger.TButton (for destructive actions)
        self.style.configure(
            "Danger.TButton",
            background=COLORS["bg_light"],
            foreground=COLORS["accent_danger"],
            borderwidth=1,
            relief="flat",
            font=self._custom_fonts["button"]
        )
        self.style.map(
            "Danger.TButton",
            background=[
                ("active", COLORS["bg_light"]),
                ("pressed", COLORS["bg_dark"])
            ],
            foreground=[
                ("active", COLORS["accent_danger"]),
                ("pressed", COLORS["accent_danger"])
            ],
            bordercolor=[
                ("active", COLORS["accent_danger"]),
                ("focus", COLORS["accent_danger"])
            ]
        )
        
        # Configure TEntry
        self.style.configure(
            "TEntry",
            fieldbackground=COLORS["bg_light"],
            foreground=COLORS["text_primary"],
            bordercolor=COLORS["border_light"],
            lightcolor=COLORS["border_light"],
            darkcolor=COLORS["border_light"],
            borderwidth=1,
            font=self._custom_fonts["main"]
        )
        self.style.map(
            "TEntry",
            fieldbackground=[
                ("disabled", COLORS["bg_dark"])
            ],
            foreground=[
                ("disabled", COLORS["text_disabled"])
            ],
            bordercolor=[
                ("focus", COLORS["accent_primary"])
            ]
        )
        
        # Configure TCheckbutton
        self.style.configure(
            "TCheckbutton",
            background=COLORS["bg_medium"],
            foreground=COLORS["text_primary"],
            font=self._custom_fonts["main"]
        )
        self.style.map(
            "TCheckbutton",
            background=[
                ("active", COLORS["bg_medium"])
            ],
            foreground=[
                ("active", COLORS["accent_primary"]),
                ("selected", COLORS["accent_primary"])
            ]
        )
        
        # Configure TRadiobutton
        self.style.configure(
            "TRadiobutton",
            background=COLORS["bg_medium"],
            foreground=COLORS["text_primary"],
            font=self._custom_fonts["main"]
        )
        self.style.map(
            "TRadiobutton",
            background=[
                ("active", COLORS["bg_medium"])
            ],
            foreground=[
                ("active", COLORS["accent_primary"]),
                ("selected", COLORS["accent_primary"])
            ]
        )
        
        # Configure TLabelframe
        self.style.configure(
            "TLabelframe",
            background=COLORS["bg_medium"],
            foreground=COLORS["text_primary"],
            bordercolor=COLORS["border_light"],
            lightcolor=COLORS["border_light"],
            darkcolor=COLORS["border_light"],
            borderwidth=1
        )
        self.style.configure(
            "TLabelframe.Label",
            background=COLORS["bg_medium"],
            foreground=COLORS["accent_primary"],
            font=self._custom_fonts["title"]
        )
        
        # Configure TNotebook
        self.style.configure(
            "TNotebook",
            background=COLORS["bg_dark"],
            bordercolor=COLORS["border_light"],
            lightcolor=COLORS["border_light"],
            darkcolor=COLORS["border_light"],
            borderwidth=1
        )
        self.style.configure(
            "TNotebook.Tab",
            background=COLORS["bg_dark"],
            foreground=COLORS["text_secondary"],
            bordercolor=COLORS["border_light"],
            lightcolor=COLORS["border_light"],
            darkcolor=COLORS["border_light"],
            padding=[5, 2],
            font=self._custom_fonts["main"]
        )
        self.style.map(
            "TNotebook.Tab",
            background=[
                ("selected", COLORS["bg_medium"]),
                ("active", COLORS["bg_light"])
            ],
            foreground=[
                ("selected", COLORS["accent_primary"]),
                ("active", COLORS["text_primary"])
            ],
            bordercolor=[
                ("selected", COLORS["accent_primary"]),
                ("active", COLORS["border_light"])
            ]
        )
        
        # Configure TProgressbar
        self.style.configure(
            "TProgressbar",
            background=COLORS["accent_primary"],
            troughcolor=COLORS["bg_light"],
            bordercolor=COLORS["border_light"],
            lightcolor=COLORS["border_light"],
            darkcolor=COLORS["border_light"]
        )
        
        # Configure Treeview
        self.style.configure(
            "Treeview",
            background=COLORS["bg_light"],
            foreground=COLORS["text_primary"],
            fieldbackground=COLORS["bg_light"],
            bordercolor=COLORS["border_light"],
            lightcolor=COLORS["border_light"],
            darkcolor=COLORS["border_light"],
            borderwidth=1,
            font=self._custom_fonts["main"]
        )
        self.style.configure(
            "Treeview.Heading",
            background=COLORS["bg_dark"],
            foreground=COLORS["accent_primary"],
            bordercolor=COLORS["border_light"],
            lightcolor=COLORS["border_light"],
            darkcolor=COLORS["border_light"],
            font=self._custom_fonts["title"]
        )
        self.style.map(
            "Treeview",
            background=[
                ("selected", COLORS["bg_dark"])
            ],
            foreground=[
                ("selected", COLORS["accent_primary"])
            ]
        )
        
        # Configure Grid.TLabel (for symbol grid)
        self.style.configure(
            "Grid.TLabel",
            background=COLORS["bg_light"],
            foreground=COLORS["text_primary"],
            bordercolor=COLORS["border_light"],
            relief="solid",
            anchor="center",
            font=self._custom_fonts["main"]
        )
        
        # Configure Status.TLabel
        self.style.configure(
            "Status.TLabel",
            background=COLORS["bg_medium"],
            foreground=COLORS["text_secondary"],
            font=self._custom_fonts["small"]
        )
        
        # Configure Title.TLabel
        self.style.configure(
            "Title.TLabel",
            background=COLORS["bg_medium"],
            foreground=COLORS["accent_primary"],
            font=self._custom_fonts["title"]
        )
    
    def _configure_tk_styles(self):
        """Configure native tk widget styles."""
        # Configure root window
        self.root.configure(background=COLORS["bg_dark"])
        
        # Configure Text widget
        self.root.option_add("*Text.background", COLORS["bg_light"])
        self.root.option_add("*Text.foreground", COLORS["text_primary"])
        self.root.option_add("*Text.borderwidth", 1)
        self.root.option_add("*Text.relief", "solid")
        self.root.option_add("*Text.font", self._custom_fonts["code"])
        
        # Configure Listbox widget
        self.root.option_add("*Listbox.background", COLORS["bg_light"])
        self.root.option_add("*Listbox.foreground", COLORS["text_primary"])
        self.root.option_add("*Listbox.selectBackground", COLORS["bg_dark"])
        self.root.option_add("*Listbox.selectForeground", COLORS["accent_primary"])
        self.root.option_add("*Listbox.font", self._custom_fonts["main"])
        
        # Configure Menu widget
        self.root.option_add("*Menu.background", COLORS["bg_dark"])
        self.root.option_add("*Menu.foreground", COLORS["text_primary"])
        self.root.option_add("*Menu.activeBackground", COLORS["bg_light"])
        self.root.option_add("*Menu.activeForeground", COLORS["accent_primary"])
        self.root.option_add("*Menu.font", self._custom_fonts["main"])
    
    def get_font(self, name: str) -> Optional[font.Font]:
        """Get a custom font by name.
        
        Args:
            name: Name of the font to retrieve
            
        Returns:
            Font object or None if not found
        """
        return self._custom_fonts.get(name)
    
    def apply_text_tags(self, text_widget: tk.Text):
        """Apply syntax highlighting tags to a Text widget.
        
        Args:
            text_widget: The Text widget to configure
        """
        # JSON key highlighting
        text_widget.tag_configure("key", foreground=COLORS["accent_secondary"])
        
        # JSON string value highlighting
        text_widget.tag_configure("string", foreground=COLORS["accent_primary"])
        
        # JSON number highlighting
        text_widget.tag_configure("number", foreground=COLORS["accent_tertiary"])
        
        # JSON boolean/null highlighting
        text_widget.tag_configure("keyword", foreground=COLORS["accent_warning"])
        
        # Error highlighting
        text_widget.tag_configure("error", foreground=COLORS["accent_danger"])
        
        # Success highlighting
        text_widget.tag_configure("success", foreground=COLORS["accent_primary"])

def apply_theme(root: tk.Tk) -> HackerTheme:
    """Apply the hacker theme to the application.
    
    Args:
        root: The root tkinter window
        
    Returns:
        HackerTheme instance
    """
    return HackerTheme(root)
