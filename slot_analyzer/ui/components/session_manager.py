"""Session manager component for browsing and managing analysis sessions."""

import tkinter as tk
from tkinter import ttk, messagebox
import logging
from typing import Dict, Any, List, Optional
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class SessionManager(ttk.Frame):
    """Component for managing analysis sessions."""
    
    def __init__(self, parent):
        """Initialize the session manager component.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.sessions: List[Dict[str, Any]] = []
        self.selected_session: Optional[Dict[str, Any]] = None
        
        self._init_ui()
    
    def _init_ui(self):
        """Initialize the UI components."""
        # Title frame
        title_frame = ttk.Frame(self)
        title_frame.pack(fill="x", padx=5, pady=(0, 5))
        ttk.Label(title_frame, text="Session Manager", font=("TkDefaultFont", 10, "bold")).pack(side="left")
        
        # Create main container
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Filter frame
        filter_frame = ttk.LabelFrame(self.main_frame, text="Filters")
        filter_frame.pack(fill="x", padx=5, pady=(0, 5))
        
        # Date range
        date_frame = ttk.Frame(filter_frame)
        date_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(date_frame, text="Date Range:").pack(side="left", padx=(0, 5))
        self.start_date = ttk.Entry(date_frame, width=10)
        self.start_date.pack(side="left", padx=(0, 5))
        ttk.Label(date_frame, text="to").pack(side="left", padx=5)
        self.end_date = ttk.Entry(date_frame, width=10)
        self.end_date.pack(side="left", padx=(0, 5))
        
        # Pattern filter
        pattern_frame = ttk.Frame(filter_frame)
        pattern_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(pattern_frame, text="Pattern Type:").pack(side="left", padx=(0, 5))
        self.pattern_var = tk.StringVar(value="All")
        pattern_combo = ttk.Combobox(
            pattern_frame,
            textvariable=self.pattern_var,
            values=["All", "Simple", "Complex", "Custom"],
            state="readonly",
            width=15
        )
        pattern_combo.pack(side="left", padx=(0, 5))
        
        # Apply filters button
        ttk.Button(
            filter_frame,
            text="Apply Filters",
            command=self._apply_filters
        ).pack(side="right", padx=5, pady=5)
        
        # Sessions list
        list_frame = ttk.LabelFrame(self.main_frame, text="Sessions")
        list_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Create treeview
        self.session_tree = ttk.Treeview(
            list_frame,
            columns=("date", "duration", "patterns"),
            show="headings",
            selectmode="browse"
        )
        
        # Configure columns
        self.session_tree.heading("date", text="Date")
        self.session_tree.heading("duration", text="Duration")
        self.session_tree.heading("patterns", text="Patterns")
        
        self.session_tree.column("date", width=120)
        self.session_tree.column("duration", width=80)
        self.session_tree.column("patterns", width=80)
        
        # Add scrollbar
        tree_scroll = ttk.Scrollbar(
            list_frame,
            orient="vertical",
            command=self.session_tree.yview
        )
        self.session_tree.configure(yscrollcommand=tree_scroll.set)
        
        # Pack tree and scrollbar
        self.session_tree.pack(side="left", fill="both", expand=True)
        tree_scroll.pack(side="right", fill="y")
        
        # Action buttons frame
        action_frame = ttk.Frame(self.main_frame)
        action_frame.pack(fill="x", padx=5, pady=5)
        
        # Load button
        self.load_btn = ttk.Button(
            action_frame,
            text="Load Session",
            command=self._load_session,
            state="disabled"
        )
        self.load_btn.pack(side="left", padx=(0, 5))
        
        # Delete button
        self.delete_btn = ttk.Button(
            action_frame,
            text="Delete Session",
            command=self._delete_session,
            state="disabled"
        )
        self.delete_btn.pack(side="left")
        
        # Export button
        ttk.Button(
            action_frame,
            text="Export All",
            command=self._export_all
        ).pack(side="right")
        
        # Bind selection event
        self.session_tree.bind("<<TreeviewSelect>>", self._on_session_selected)
    
    def _apply_filters(self):
        """Apply filters to session list."""
        try:
            # Clear current items
            for item in self.session_tree.get_children():
                self.session_tree.delete(item)
            
            # Get filter values
            try:
                start = datetime.strptime(self.start_date.get(), "%Y-%m-%d").date()
            except ValueError:
                start = None
                
            try:
                end = datetime.strptime(self.end_date.get(), "%Y-%m-%d").date()
            except ValueError:
                end = None
                
            pattern_type = self.pattern_var.get()
            
            # Filter sessions
            filtered_sessions = self.sessions
            
            if start:
                filtered_sessions = [
                    s for s in filtered_sessions
                    if datetime.fromtimestamp(s["timestamp"]).date() >= start
                ]
                
            if end:
                filtered_sessions = [
                    s for s in filtered_sessions
                    if datetime.fromtimestamp(s["timestamp"]).date() <= end
                ]
                
            if pattern_type != "All":
                filtered_sessions = [
                    s for s in filtered_sessions
                    if s.get("pattern_type") == pattern_type
                ]
            
            # Update tree
            for session in filtered_sessions:
                date = datetime.fromtimestamp(session["timestamp"]).strftime("%Y-%m-%d %H:%M")
                duration = str(datetime.timedelta(seconds=session["duration"]))
                patterns = len(session.get("patterns", []))
                
                self.session_tree.insert(
                    "",
                    "end",
                    values=(date, duration, patterns),
                    tags=(str(session["id"]),)
                )
            
            logger.debug("Filters applied successfully")
            
        except Exception as e:
            logger.error(f"Error applying filters: {e}")
            messagebox.showerror("Error", f"Failed to apply filters: {str(e)}")
    
    def _on_session_selected(self, event):
        """Handle session selection."""
        selection = self.session_tree.selection()
        if selection:
            # Enable action buttons
            self.load_btn.configure(state="normal")
            self.delete_btn.configure(state="normal")
            
            # Find selected session
            session_id = self.session_tree.item(selection[0])["tags"][0]
            self.selected_session = next(
                (s for s in self.sessions if str(s["id"]) == session_id),
                None
            )
        else:
            # Disable action buttons
            self.load_btn.configure(state="disabled")
            self.delete_btn.configure(state="disabled")
            self.selected_session = None
    
    def _load_session(self):
        """Load the selected session."""
        if not self.selected_session:
            return
            
        try:
            # Load session data
            logger.info(f"Loading session {self.selected_session['id']}")
            
            # Emit session loaded event
            self.event_generate("<<SessionLoaded>>")
            
        except Exception as e:
            logger.error(f"Error loading session: {e}")
            messagebox.showerror("Error", f"Failed to load session: {str(e)}")
    
    def _delete_session(self):
        """Delete the selected session."""
        if not self.selected_session:
            return
            
        if messagebox.askyesno(
            "Delete Session",
            "Are you sure you want to delete this session?"
        ):
            try:
                # Remove from sessions list
                self.sessions = [
                    s for s in self.sessions
                    if s["id"] != self.selected_session["id"]
                ]
                
                # Remove from tree
                selection = self.session_tree.selection()
                if selection:
                    self.session_tree.delete(selection[0])
                
                self.selected_session = None
                logger.info(f"Session {self.selected_session['id']} deleted")
                
            except Exception as e:
                logger.error(f"Error deleting session: {e}")
                messagebox.showerror("Error", f"Failed to delete session: {str(e)}")
    
    def _export_all(self):
        """Export all sessions to file."""
        try:
            # Export sessions
            with open("sessions_export.json", "w") as f:
                json.dump(self.sessions, f, indent=2)
                
            logger.info("All sessions exported successfully")
            messagebox.showinfo(
                "Success",
                "Sessions exported to sessions_export.json"
            )
            
        except Exception as e:
            logger.error(f"Error exporting sessions: {e}")
            messagebox.showerror("Error", f"Failed to export sessions: {str(e)}")
    
    def add_session(self, session: Dict[str, Any]):
        """Add a new session to the manager.
        
        Args:
            session: Session data dictionary
        """
        self.sessions.append(session)
        self._apply_filters()  # Refresh display
    
    def get_selected_session(self) -> Optional[Dict[str, Any]]:
        """Get the currently selected session.
        
        Returns:
            Selected session data or None if no selection
        """
        return self.selected_session.copy() if self.selected_session else None