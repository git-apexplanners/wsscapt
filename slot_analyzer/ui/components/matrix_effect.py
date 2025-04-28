"""Matrix-style animation effect for the UI."""

import tkinter as tk
import random
import string
from typing import List, Tuple, Optional

class MatrixEffect:
    """Matrix-style falling code animation effect."""
    
    def __init__(
        self, 
        canvas: tk.Canvas, 
        color: str = "#00ff41", 
        density: float = 0.05,
        speed: int = 100
    ):
        """Initialize the matrix effect.
        
        Args:
            canvas: The canvas to draw on
            color: The color of the characters (default: matrix green)
            density: The density of the falling characters (0.0-1.0)
            speed: Animation speed in milliseconds
        """
        self.canvas = canvas
        self.color = color
        self.density = density
        self.speed = speed
        self.running = False
        self.columns: List[Tuple[int, List[int], List[str]]] = []
        self.timer_id: Optional[str] = None
        
        # Bind resize event
        self.canvas.bind("<Configure>", self._on_resize)
        
        # Initialize columns
        self._init_columns()
    
    def _init_columns(self):
        """Initialize the columns of falling characters."""
        self.columns = []
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        
        if width <= 1 or height <= 1:
            # Canvas not ready yet
            return
        
        # Calculate number of columns based on width
        col_width = 10
        num_cols = width // col_width
        
        # Create columns
        for i in range(num_cols):
            x = i * col_width
            # Each column has: x-position, y-positions, characters
            y_positions = []
            chars = []
            
            # Only create initial characters for some columns
            if random.random() < self.density:
                # Random starting position
                y = random.randint(-height // 2, height // 2)
                # Random length of the column
                length = random.randint(5, 15)
                
                for j in range(length):
                    y_positions.append(y + j * 15)
                    chars.append(random.choice(string.ascii_letters + string.digits))
            
            self.columns.append((x, y_positions, chars))
    
    def _on_resize(self, event):
        """Handle canvas resize event."""
        self._init_columns()
    
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
        
        # Update and draw each column
        for i, (x, y_positions, chars) in enumerate(self.columns):
            # Move characters down
            y_positions = [y + 5 for y in y_positions]
            
            # Remove characters that have fallen off the bottom
            while y_positions and y_positions[0] > height:
                y_positions.pop(0)
                chars.pop(0)
            
            # Randomly add new characters at the top
            if (not y_positions or y_positions[-1] > 20) and random.random() < 0.1:
                y_positions.append(0)
                chars.append(random.choice(string.ascii_letters + string.digits))
            
            # Draw characters
            for j, (y, char) in enumerate(zip(y_positions, chars)):
                # Vary color intensity based on position
                alpha = 255
                if j == len(y_positions) - 1:
                    # Head of the column is brightest
                    color = self.color
                else:
                    # Fade out older characters
                    fade = max(0, 255 - (j * 25))
                    r, g, b = int(self.color[1:3], 16), int(self.color[3:5], 16), int(self.color[5:7], 16)
                    r = min(255, int(r * fade / 255))
                    g = min(255, int(g * fade / 255))
                    b = min(255, int(b * fade / 255))
                    color = f"#{r:02x}{g:02x}{b:02x}"
                
                # Draw the character
                self.canvas.create_text(
                    x, y, 
                    text=char, 
                    fill=color, 
                    font=("Courier", 10), 
                    tags="matrix"
                )
            
            # Update the column
            self.columns[i] = (x, y_positions, chars)
        
        # Randomly change some characters
        for i, (x, y_positions, chars) in enumerate(self.columns):
            for j in range(len(chars)):
                if random.random() < 0.05:
                    chars[j] = random.choice(string.ascii_letters + string.digits)
            self.columns[i] = (x, y_positions, chars)
        
        # Schedule next frame
        self.timer_id = self.canvas.after(self.speed, self._animate)

class MatrixBackground(tk.Frame):
    """A frame with a matrix animation background."""
    
    def __init__(self, parent, **kwargs):
        """Initialize the matrix background frame.
        
        Args:
            parent: The parent widget
            **kwargs: Additional arguments to pass to the Frame constructor
        """
        super().__init__(parent, **kwargs)
        
        # Create canvas for the matrix effect
        self.canvas = tk.Canvas(
            self, 
            bg="#000000", 
            highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True)
        
        # Create the matrix effect
        self.matrix = MatrixEffect(self.canvas)
        
        # Start the animation when shown
        self.bind("<Map>", self._on_map)
        self.bind("<Unmap>", self._on_unmap)
    
    def _on_map(self, event):
        """Handle widget map event."""
        self.matrix.start()
    
    def _on_unmap(self, event):
        """Handle widget unmap event."""
        self.matrix.stop()
    
    def start_animation(self):
        """Start the matrix animation."""
        self.matrix.start()
    
    def stop_animation(self):
        """Stop the matrix animation."""
        self.matrix.stop()
