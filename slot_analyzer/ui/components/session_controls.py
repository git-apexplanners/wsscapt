"""Session control component for managing capture sessions."""

import tkinter as tk
from tkinter import ttk, messagebox
import logging
from typing import Optional, Callable
from ..services.capture import CaptureService

logger = logging.getLogger(__name__)

class SessionControls(ttk.Frame):
    """Component for controlling capture sessions."""
    
    def __init__(self, parent, capture_service: Optional[CaptureService] = None):
        """Initialize the session controls component.
        
        Args:
            parent: Parent widget
            capture_service: Instance of CaptureService for controlling captures
        """
        super().__init__(parent)
        
        self.capture_service = capture_service
        self.session_active = False
        self._capture_callback: Optional[Callable] = None
        
        self._init_ui()
    
    def _init_ui(self):
        """Initialize the UI components."""
        # Controls frame with border
        self.controls_frame = ttk.LabelFrame(self, text="Session Controls")
        self.controls_frame.pack(fill="x", padx=5, pady=5)
        
        # Main controls
        main_controls = ttk.Frame(self.controls_frame)
        main_controls.pack(fill="x", padx=5, pady=5)
        
        # Start/Stop button
        self.start_stop_btn = ttk.Button(
            main_controls,
            text="Start Session",
            command=self._toggle_session,
            style="Action.TButton"
        )
        self.start_stop_btn.pack(side="left", padx=(0, 5))
        
        # Reset button
        self.reset_btn = ttk.Button(
            main_controls,
            text="Reset Session",
            command=self._reset_session,
            state="disabled"
        )
        self.reset_btn.pack(side="left", padx=5)
        
        # Export button
        self.export_btn = ttk.Button(
            main_controls,
            text="Export Data",
            command=self._export_session,
            state="disabled"
        )
        self.export_btn.pack(side="left", padx=5)
        
        # Session info frame
        info_frame = ttk.Frame(self.controls_frame)
        info_frame.pack(fill="x", padx=5, pady=(0, 5))
        
        # Session status
        ttk.Label(info_frame, text="Status:").pack(side="left", padx=(0, 5))
        self.status_var = tk.StringVar(value="Inactive")
        ttk.Label(
            info_frame,
            textvariable=self.status_var,
            style="Status.TLabel"
        ).pack(side="left", padx=(0, 10))
        
        # Session duration
        ttk.Label(info_frame, text="Duration:").pack(side="left", padx=(0, 5))
        self.duration_var = tk.StringVar(value="00:00:00")
        ttk.Label(
            info_frame,
            textvariable=self.duration_var
        ).pack(side="left", padx=(0, 10))
        
        # Configure styles
        style = ttk.Style()
        style.configure("Action.TButton", font=("TkDefaultFont", 9, "bold"))
        style.configure("Status.TLabel", foreground="gray")
        
        # Timer for updating duration
        self._duration_timer = None
        self._start_time = 0
    
    def _toggle_session(self):
        """Toggle the capture session state."""
        if not self.session_active:
            self._start_session()
        else:
            self._stop_session()
    
    def _start_session(self):
        """Start a new capture session."""
        try:
            if self.capture_service:
                self.capture_service.start()
            
            self.session_active = True
            self.status_var.set("Active")
            self.start_stop_btn.configure(text="Stop Session")
            self.reset_btn.configure(state="disabled")
            self.export_btn.configure(state="disabled")
            
            # Start duration timer
            self._start_time = tk.time.time()
            self._update_duration()
            
            logger.info("Capture session started")
            
        except Exception as e:
            logger.error(f"Error starting capture session: {e}")
            messagebox.showerror("Error", f"Failed to start session: {str(e)}")
    
    def _stop_session(self):
        """Stop the current capture session."""
        try:
            if self.capture_service:
                self.capture_service.stop()
            
            self.session_active = False
            self.status_var.set("Stopped")
            self.start_stop_btn.configure(text="Start Session")
            self.reset_btn.configure(state="normal")
            self.export_btn.configure(state="normal")
            
            # Stop duration timer
            if self._duration_timer:
                self.after_cancel(self._duration_timer)
                self._duration_timer = None
            
            logger.info("Capture session stopped")
            
        except Exception as e:
            logger.error(f"Error stopping capture session: {e}")
            messagebox.showerror("Error", f"Failed to stop session: {str(e)}")
    
    def _reset_session(self):
        """Reset the current session data."""
        if messagebox.askyesno(
            "Reset Session",
            "Are you sure you want to reset the current session? This will clear all captured data."
        ):
            try:
                if self.capture_service:
                    self.capture_service.reset()
                
                self.status_var.set("Inactive")
                self.duration_var.set("00:00:00")
                self._start_time = 0
                
                self.reset_btn.configure(state="disabled")
                self.export_btn.configure(state="disabled")
                
                logger.info("Session reset")
                
            except Exception as e:
                logger.error(f"Error resetting session: {e}")
                messagebox.showerror("Error", f"Failed to reset session: {str(e)}")
    
    def _export_session(self):
        """Export the current session data."""
        try:
            if self.capture_service:
                self.capture_service.export_session()
            logger.info("Session data exported")
            messagebox.showinfo("Success", "Session data exported successfully")
            
        except Exception as e:
            logger.error(f"Error exporting session data: {e}")
            messagebox.showerror("Error", f"Failed to export session data: {str(e)}")
    
    def _update_duration(self):
        """Update the session duration display."""
        if self.session_active and self._start_time:
            duration = int(tk.time.time() - self._start_time)
            hours = duration // 3600
            minutes = (duration % 3600) // 60
            seconds = duration % 60
            
            self.duration_var.set(f"{hours:02d}:{minutes:02d}:{seconds:02d}")
            
            # Schedule next update
            self._duration_timer = self.after(1000, self._update_duration)
    
    def set_capture_callback(self, callback: Callable):
        """Set callback for capture events.
        
        Args:
            callback: Function to call when capture events occur
        """
        self._capture_callback = callback