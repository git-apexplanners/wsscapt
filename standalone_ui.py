"""Standalone hacker-style UI that doesn't depend on the existing module structure."""

import tkinter as tk
import random
import time
from pathlib import Path
import sys

class HackerTheme:
    """Hacker-style theme for the application."""
    
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
    }
    
    @classmethod
    def apply(cls, root):
        """Apply the hacker theme to the root window."""
        root.configure(bg=cls.COLORS["bg_dark"])
        
        # Set default colors for all widgets
        root.option_add("*Background", cls.COLORS["bg_medium"])
        root.option_add("*Foreground", cls.COLORS["text_primary"])
        root.option_add("*Font", ("Consolas", 9))
        
        # Button styling
        root.option_add("*Button.Background", cls.COLORS["bg_light"])
        root.option_add("*Button.Foreground", cls.COLORS["accent_primary"])
        root.option_add("*Button.activeBackground", cls.COLORS["bg_light"])
        root.option_add("*Button.activeForeground", cls.COLORS["accent_primary"])
        root.option_add("*Button.borderWidth", 1)
        root.option_add("*Button.relief", "flat")
        
        # Entry styling
        root.option_add("*Entry.Background", cls.COLORS["bg_light"])
        root.option_add("*Entry.Foreground", cls.COLORS["text_primary"])
        root.option_add("*Entry.borderWidth", 1)
        
        # Label styling
        root.option_add("*Label.Background", cls.COLORS["bg_medium"])
        root.option_add("*Label.Foreground", cls.COLORS["text_primary"])
        
        # Frame styling
        root.option_add("*Frame.Background", cls.COLORS["bg_medium"])
        root.option_add("*Frame.borderWidth", 0)
        
        # LabelFrame styling
        root.option_add("*LabelFrame.Background", cls.COLORS["bg_medium"])
        root.option_add("*LabelFrame.Foreground", cls.COLORS["accent_primary"])
        root.option_add("*LabelFrame.borderWidth", 1)
        
        # Text styling
        root.option_add("*Text.Background", cls.COLORS["bg_light"])
        root.option_add("*Text.Foreground", cls.COLORS["text_primary"])
        root.option_add("*Text.borderWidth", 1)
        
        return cls

class MatrixEffect:
    """Simple matrix-style falling code animation effect."""
    
    def __init__(self, canvas, color="#00ff41", density=0.05, speed=100):
        """Initialize the matrix effect."""
        self.canvas = canvas
        self.color = color
        self.density = density
        self.speed = speed
        self.running = False
        self.chars = []
        self.timer_id = None
        
    def start(self):
        """Start the animation."""
        if not self.running:
            self.running = True
            self._animate()
    
    def stop(self):
        """Stop the animation."""
        self.running = False
        if self.timer_id:
            self.canvas.after_cancel(self.timer_id)
            self.timer_id = None
    
    def _animate(self):
        """Animate one frame of the matrix effect."""
        if not self.running:
            return
        
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        
        # Clear canvas
        self.canvas.delete("matrix")
        
        # Add new characters
        if random.random() < self.density:
            x = random.randint(0, width)
            y = 0
            char = random.choice("01")
            self.chars.append([x, y, char])
        
        # Update and draw characters
        new_chars = []
        for x, y, char in self.chars:
            y += 5
            if y < height:
                self.canvas.create_text(x, y, text=char, fill=self.color, tags="matrix")
                new_chars.append([x, y, char])
        
        self.chars = new_chars
        
        # Schedule next frame
        self.timer_id = self.canvas.after(self.speed, self._animate)

class HackerSlotUI:
    """Hacker-style UI for the slot analyzer."""
    
    def __init__(self, root):
        """Initialize the UI."""
        self.root = root
        self.root.title("H4CK3R SLOT ANALYZER")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)
        
        # Apply hacker theme
        self.theme = HackerTheme.apply(self.root)
        
        # Configure grid weights
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Create matrix background
        self.bg_canvas = tk.Canvas(self.root, bg=HackerTheme.COLORS["bg_dark"], highlightthickness=0)
        self.bg_canvas.grid(row=0, column=0, sticky="nsew")
        self.matrix = MatrixEffect(self.bg_canvas)
        self.matrix.start()
        
        # Create main container
        self.main_frame = tk.Frame(
            self.root,
            bg=HackerTheme.COLORS["bg_medium"],
            bd=1,
            relief="solid"
        )
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Configure main frame grid
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=1)
        
        # Add status bar
        self.status_bar = tk.Frame(self.root, bg=HackerTheme.COLORS["bg_medium"])
        self.status_bar.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 5))
        
        # Status message
        self.status_message = tk.StringVar(value="System ready. Awaiting command...")
        status_label = tk.Label(
            self.status_bar,
            textvariable=self.status_message,
            bg=HackerTheme.COLORS["bg_medium"],
            fg=HackerTheme.COLORS["text_secondary"],
            font=("Consolas", 8)
        )
        status_label.pack(side="left")
        
        # Version info
        version_label = tk.Label(
            self.status_bar,
            text="v0.1.0 | SECURE CONNECTION",
            bg=HackerTheme.COLORS["bg_medium"],
            fg=HackerTheme.COLORS["text_secondary"],
            font=("Consolas", 8)
        )
        version_label.pack(side="right")
        
        # Set up the main content
        self._setup_content()
        
        # Start status updates
        self._update_status()
    
    def _setup_content(self):
        """Set up the main content area."""
        # Header
        header = tk.Frame(self.main_frame, bg=HackerTheme.COLORS["bg_medium"], height=50)
        header.grid(row=0, column=0, columnspan=3, sticky="ew", padx=5, pady=5)
        
        # Title
        title = tk.Label(
            header,
            text="SLOT ANALYZER CONTROL PANEL",
            bg=HackerTheme.COLORS["bg_medium"],
            fg=HackerTheme.COLORS["accent_primary"],
            font=("Consolas", 14, "bold")
        )
        title.pack(side="left", padx=10)
        
        # Control buttons
        btn_frame = tk.Frame(header, bg=HackerTheme.COLORS["bg_medium"])
        btn_frame.pack(side="right", padx=10)
        
        start_btn = tk.Button(
            btn_frame,
            text="START SESSION",
            bg=HackerTheme.COLORS["bg_light"],
            fg=HackerTheme.COLORS["accent_primary"],
            font=("Consolas", 9, "bold"),
            bd=1,
            relief="flat",
            padx=10,
            pady=5,
            activebackground=HackerTheme.COLORS["bg_light"],
            activeforeground=HackerTheme.COLORS["accent_primary"],
            command=self._toggle_session
        )
        start_btn.pack(side="left", padx=5)
        self.start_btn = start_btn
        
        reset_btn = tk.Button(
            btn_frame,
            text="RESET",
            bg=HackerTheme.COLORS["bg_light"],
            fg=HackerTheme.COLORS["text_secondary"],
            font=("Consolas", 9),
            bd=1,
            relief="flat",
            padx=10,
            pady=5,
            state="disabled"
        )
        reset_btn.pack(side="left", padx=5)
        self.reset_btn = reset_btn
        
        # Left panel
        left_panel = tk.Frame(self.main_frame, bg=HackerTheme.COLORS["bg_medium"], width=250)
        left_panel.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        left_panel.grid_propagate(False)
        
        # Left panel title
        left_title = tk.Label(
            left_panel,
            text="SESSION CONTROL",
            bg=HackerTheme.COLORS["bg_medium"],
            fg=HackerTheme.COLORS["accent_primary"],
            font=("Consolas", 10, "bold")
        )
        left_title.pack(anchor="w", padx=10, pady=5)
        
        # Session list
        session_frame = tk.LabelFrame(
            left_panel,
            text="ACTIVE SESSIONS",
            bg=HackerTheme.COLORS["bg_medium"],
            fg=HackerTheme.COLORS["accent_primary"],
            font=("Consolas", 9),
            bd=1
        )
        session_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Session list content
        session_list = tk.Listbox(
            session_frame,
            bg=HackerTheme.COLORS["bg_light"],
            fg=HackerTheme.COLORS["text_primary"],
            font=("Consolas", 9),
            bd=0,
            highlightthickness=0,
            selectbackground=HackerTheme.COLORS["bg_dark"],
            selectforeground=HackerTheme.COLORS["accent_primary"]
        )
        session_list.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Center panel
        center_panel = tk.Frame(self.main_frame, bg=HackerTheme.COLORS["bg_medium"])
        center_panel.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)
        
        # Center panel title
        center_title = tk.Label(
            center_panel,
            text="SYMBOL GRID",
            bg=HackerTheme.COLORS["bg_medium"],
            fg=HackerTheme.COLORS["accent_primary"],
            font=("Consolas", 10, "bold")
        )
        center_title.pack(anchor="w", padx=10, pady=5)
        
        # Symbol grid
        grid_frame = tk.LabelFrame(
            center_panel,
            text="CURRENT SYMBOLS",
            bg=HackerTheme.COLORS["bg_medium"],
            fg=HackerTheme.COLORS["accent_primary"],
            font=("Consolas", 9),
            bd=1
        )
        grid_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Create grid cells
        grid_container = tk.Frame(grid_frame, bg=HackerTheme.COLORS["bg_medium"])
        grid_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.cells = []
        for row in range(3):
            cell_row = []
            for col in range(5):
                cell = tk.Label(
                    grid_container,
                    text="?",
                    width=4,
                    height=2,
                    bg=HackerTheme.COLORS["bg_light"],
                    fg=HackerTheme.COLORS["text_primary"],
                    font=("Consolas", 12),
                    bd=1,
                    relief="solid"
                )
                cell.grid(row=row, column=col, padx=2, pady=2, sticky="nsew")
                cell_row.append(cell)
            self.cells.append(cell_row)
        
        # Right panel
        right_panel = tk.Frame(self.main_frame, bg=HackerTheme.COLORS["bg_medium"], width=300)
        right_panel.grid(row=1, column=2, sticky="nsew", padx=5, pady=5)
        right_panel.grid_propagate(False)
        
        # Right panel title
        right_title = tk.Label(
            right_panel,
            text="DATA MONITOR",
            bg=HackerTheme.COLORS["bg_medium"],
            fg=HackerTheme.COLORS["accent_primary"],
            font=("Consolas", 10, "bold")
        )
        right_title.pack(anchor="w", padx=10, pady=5)
        
        # Capture monitor
        monitor_frame = tk.LabelFrame(
            right_panel,
            text="CAPTURE FEED",
            bg=HackerTheme.COLORS["bg_medium"],
            fg=HackerTheme.COLORS["accent_primary"],
            font=("Consolas", 9),
            bd=1
        )
        monitor_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Status display
        self.status_display = tk.Label(
            monitor_frame,
            text="Waiting for capture...",
            bg=HackerTheme.COLORS["bg_light"],
            fg=HackerTheme.COLORS["text_secondary"],
            font=("Consolas", 9),
            bd=1,
            relief="solid",
            width=30,
            height=10,
            anchor="nw",
            justify="left"
        )
        self.status_display.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Data viewer
        data_frame = tk.LabelFrame(
            right_panel,
            text="DATA ANALYSIS",
            bg=HackerTheme.COLORS["bg_medium"],
            fg=HackerTheme.COLORS["accent_primary"],
            font=("Consolas", 9),
            bd=1
        )
        data_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Data text
        self.data_text = tk.Text(
            data_frame,
            bg=HackerTheme.COLORS["bg_light"],
            fg=HackerTheme.COLORS["text_primary"],
            font=("Consolas", 9),
            bd=1,
            relief="solid",
            height=10,
            width=30
        )
        self.data_text.pack(fill="both", expand=True, padx=5, pady=5)
        self.data_text.insert("1.0", "// Waiting for data...\n")
        self.data_text.config(state="disabled")
        
        # Session state
        self.session_active = False
    
    def _toggle_session(self):
        """Toggle the session state."""
        if not self.session_active:
            self._start_session()
        else:
            self._stop_session()
    
    def _start_session(self):
        """Start a session."""
        self.session_active = True
        self.start_btn.config(text="STOP SESSION")
        self.reset_btn.config(state="disabled")
        self.status_message.set("Session active. Capturing data...")
        
        # Simulate activity
        self._simulate_activity()
    
    def _stop_session(self):
        """Stop a session."""
        self.session_active = False
        self.start_btn.config(text="START SESSION")
        self.reset_btn.config(state="normal")
        self.status_message.set("Session stopped. Ready for analysis.")
        
        # Stop simulation
        if hasattr(self, "_activity_timer") and self._activity_timer:
            self.root.after_cancel(self._activity_timer)
            self._activity_timer = None
    
    def _simulate_activity(self):
        """Simulate activity in the UI."""
        if not self.session_active:
            return
        
        # Update a random cell
        row = random.randint(0, 2)
        col = random.randint(0, 4)
        symbols = ["7", "BAR", "♦", "♥", "♠", "♣", "WILD", "$"]
        self.cells[row][col].config(text=random.choice(symbols))
        
        # Update status display
        timestamp = time.strftime("%H:%M:%S")
        self.status_display.config(
            text=f"[{timestamp}] Captured frame #{random.randint(1, 1000)}\n"
                f"Processing symbols...\n"
                f"Recognition rate: {random.randint(85, 99)}%\n"
                f"Network latency: {random.randint(5, 50)}ms"
        )
        
        # Update data text
        self.data_text.config(state="normal")
        self.data_text.delete("1.0", "end")
        self.data_text.insert("1.0", f"// Data analysis at {timestamp}\n\n")
        self.data_text.insert("end", "{\n")
        self.data_text.insert("end", f'  "session_id": "{random.randint(1000, 9999)}",\n')
        self.data_text.insert("end", f'  "frames_processed": {random.randint(10, 500)},\n')
        self.data_text.insert("end", f'  "win_probability": {random.random():.4f},\n')
        self.data_text.insert("end", f'  "pattern_detected": {random.choice(["true", "false"])},\n')
        self.data_text.insert("end", f'  "confidence": {random.randint(80, 99)}\n')
        self.data_text.insert("end", "}")
        self.data_text.config(state="disabled")
        
        # Schedule next update
        self._activity_timer = self.root.after(random.randint(1000, 3000), self._simulate_activity)
    
    def _update_status(self):
        """Update status messages to simulate activity."""
        if not self.session_active:
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
        app = HackerSlotUI(root)
        app.run()
        
    except Exception as e:
        print(f"Error launching application: {e}")
        if tk._default_root:
            tk._default_root.destroy()
        sys.exit(1)

if __name__ == "__main__":
    main()
