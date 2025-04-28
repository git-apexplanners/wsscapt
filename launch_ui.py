"""Simple launcher for the hacker-style UI.

This script creates a minimal environment to launch the UI without
requiring all the backend services to be available.
"""

import tkinter as tk
import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Create mock services to avoid dependency issues
class MockService:
    """Mock service that does nothing but allows the UI to initialize."""
    
    def __init__(self, *args, **kwargs):
        pass
        
    def start(self):
        pass
        
    def stop(self):
        pass
        
    def subscribe(self, event, callback):
        pass
        
    def close(self):
        pass

# Create mock modules
import sys
from types import ModuleType

# Create mock modules to avoid import errors
mock_modules = [
    'slot_analyzer.services.capture',
    'slot_analyzer.services.symbol',
    'slot_analyzer.services.pattern',
    'slot_analyzer.queue'
]

for module_name in mock_modules:
    if module_name not in sys.modules:
        module = ModuleType(module_name)
        module.CaptureService = MockService
        module.SymbolRecognizer = MockService
        module.PatternAnalyzer = MockService
        module.MessageQueue = MockService
        sys.modules[module_name] = module

# Now we can import our UI modules
from slot_analyzer.ui.theme import apply_theme

class SimpleHackerUI:
    """A simplified version of the slot analyzer UI with hacker styling."""
    
    def __init__(self, root):
        """Initialize the UI.
        
        Args:
            root: The root tkinter window
        """
        self.root = root
        self.root.title("H4CK3R SLOT ANALYZER")
        
        # Apply hacker theme
        self.theme = apply_theme(self.root)
        
        # Set up the window
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)
        
        # Configure grid weights
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Create main container
        self.main_frame = tk.Frame(self.root, bg="#121212", bd=1, relief="solid")
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Add status bar
        self.status_bar = tk.Frame(self.root, bg="#121212")
        self.status_bar.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 5))
        
        # Status message
        self.status_message = tk.StringVar(value="System ready. Awaiting command...")
        status_label = tk.Label(
            self.status_bar,
            textvariable=self.status_message,
            bg="#121212",
            fg="#a0a0a0",
            font=("Consolas", 8)
        )
        status_label.pack(side="left")
        
        # Version info
        version_label = tk.Label(
            self.status_bar,
            text="v0.1.0 | SECURE CONNECTION",
            bg="#121212",
            fg="#a0a0a0",
            font=("Consolas", 8)
        )
        version_label.pack(side="right")
        
        # Set up the main content
        self._setup_content()
    
    def _setup_content(self):
        """Set up the main content area."""
        # Configure main frame grid
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=1)
        
        # Header
        header = tk.Frame(self.main_frame, bg="#121212", height=50)
        header.grid(row=0, column=0, columnspan=3, sticky="ew", padx=5, pady=5)
        
        # Title
        title = tk.Label(
            header,
            text="SLOT ANALYZER CONTROL PANEL",
            bg="#121212",
            fg="#00ff41",
            font=("Consolas", 14, "bold")
        )
        title.pack(side="left", padx=10)
        
        # Control buttons
        btn_frame = tk.Frame(header, bg="#121212")
        btn_frame.pack(side="right", padx=10)
        
        start_btn = tk.Button(
            btn_frame,
            text="START SESSION",
            bg="#1a1a1a",
            fg="#00ff41",
            font=("Consolas", 9, "bold"),
            bd=1,
            relief="flat",
            padx=10,
            pady=5,
            activebackground="#1a1a1a",
            activeforeground="#00ff41"
        )
        start_btn.pack(side="left", padx=5)
        
        reset_btn = tk.Button(
            btn_frame,
            text="RESET",
            bg="#1a1a1a",
            fg="#a0a0a0",
            font=("Consolas", 9),
            bd=1,
            relief="flat",
            padx=10,
            pady=5,
            state="disabled"
        )
        reset_btn.pack(side="left", padx=5)
        
        # Left panel
        left_panel = tk.Frame(self.main_frame, bg="#121212", width=250)
        left_panel.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        left_panel.grid_propagate(False)
        
        # Left panel title
        left_title = tk.Label(
            left_panel,
            text="SESSION CONTROL",
            bg="#121212",
            fg="#00ff41",
            font=("Consolas", 10, "bold")
        )
        left_title.pack(anchor="w", padx=10, pady=5)
        
        # Session list
        session_frame = tk.LabelFrame(
            left_panel,
            text="ACTIVE SESSIONS",
            bg="#121212",
            fg="#00ff41",
            font=("Consolas", 9),
            bd=1
        )
        session_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Center panel
        center_panel = tk.Frame(self.main_frame, bg="#121212")
        center_panel.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)
        
        # Center panel title
        center_title = tk.Label(
            center_panel,
            text="SYMBOL GRID",
            bg="#121212",
            fg="#00ff41",
            font=("Consolas", 10, "bold")
        )
        center_title.pack(anchor="w", padx=10, pady=5)
        
        # Symbol grid
        grid_frame = tk.LabelFrame(
            center_panel,
            text="CURRENT SYMBOLS",
            bg="#121212",
            fg="#00ff41",
            font=("Consolas", 9),
            bd=1
        )
        grid_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Create grid cells
        for row in range(3):
            for col in range(5):
                cell = tk.Label(
                    grid_frame,
                    text="?",
                    width=4,
                    height=2,
                    bg="#1a1a1a",
                    fg="#e0e0e0",
                    font=("Consolas", 12),
                    bd=1,
                    relief="solid"
                )
                cell.grid(row=row, column=col, padx=2, pady=2, sticky="nsew")
        
        # Right panel
        right_panel = tk.Frame(self.main_frame, bg="#121212", width=300)
        right_panel.grid(row=1, column=2, sticky="nsew", padx=5, pady=5)
        right_panel.grid_propagate(False)
        
        # Right panel title
        right_title = tk.Label(
            right_panel,
            text="DATA MONITOR",
            bg="#121212",
            fg="#00ff41",
            font=("Consolas", 10, "bold")
        )
        right_title.pack(anchor="w", padx=10, pady=5)
        
        # Capture monitor
        monitor_frame = tk.LabelFrame(
            right_panel,
            text="CAPTURE FEED",
            bg="#121212",
            fg="#00ff41",
            font=("Consolas", 9),
            bd=1
        )
        monitor_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Status display
        status_display = tk.Label(
            monitor_frame,
            text="Waiting for capture...",
            bg="#1a1a1a",
            fg="#a0a0a0",
            font=("Consolas", 9),
            bd=1,
            relief="solid",
            width=30,
            height=10
        )
        status_display.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Update status periodically to simulate activity
        self._update_status()
    
    def _update_status(self):
        """Update status messages to simulate activity."""
        import random
        
        messages = [
            "System ready. Awaiting command...",
            "Scanning network for slot patterns...",
            "Analyzing symbol distribution...",
            "Pattern recognition active...",
            "Monitoring data stream...",
            "Secure connection established...",
            "Processing capture data...",
            "Symbol recognition initialized..."
        ]
        
        self.status_message.set(random.choice(messages))
        self.root.after(3000, self._update_status)
    
    def run(self):
        """Run the application."""
        self.root.mainloop()

def main():
    """Main entry point."""
    try:
        # Create the root window
        root = tk.Tk()
        
        # Create and run the application
        app = SimpleHackerUI(root)
        app.run()
        
    except Exception as e:
        print(f"Error launching application: {e}")
        if tk._default_root:
            tk._default_root.destroy()
        sys.exit(1)

if __name__ == "__main__":
    main()
