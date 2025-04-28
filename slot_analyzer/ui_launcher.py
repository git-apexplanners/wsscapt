"""UI launcher for the slot analyzer application."""

import tkinter as tk
import logging
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

def main():
    """Launch the slot analyzer UI application."""
    try:
        # Create the root window
        root = tk.Tk()
        
        # Import the UI module
        from slot_analyzer.ui import SlotAnalyzerApp
        
        # Create and run the application
        app = SlotAnalyzerApp(root)
        logger.info("Application initialized successfully")
        
        # Start the main loop
        app.run()
        
    except Exception as e:
        logger.error(f"Error launching application: {e}")
        if tk._default_root:
            tk._default_root.destroy()
        sys.exit(1)

if __name__ == "__main__":
    main()
