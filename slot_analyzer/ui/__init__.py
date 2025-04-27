"""User interface module for the slot game analyzer.

This module provides the graphical user interface components for analyzing slot games,
including real-time capture monitoring, symbol recognition, pattern analysis, and session management.

Example:
    ```python
    import tkinter as tk
    from slot_analyzer.ui import SlotAnalyzerApp
    
    root = tk.Tk()
    app = SlotAnalyzerApp(root)
    app.run()
    ```
"""

from .main import SlotAnalyzerApp
from . import components

__version__ = "1.0.0"
__all__ = ["SlotAnalyzerApp", "components"]