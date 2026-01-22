"""
Utility functions for GUI.
"""

import tkinter as tk
from tkinter import ttk


def apply_theme(root: tk.Tk):
    """Apply modern theme to the GUI."""
    style = ttk.Style()
    style.theme_use("clam")

    # Configure colors
    bg_color = "#f0f0f0"
    fg_color = "#333333"
    accent_color = "#007ACC"

    root.configure(bg=bg_color)

    style.configure("TFrame", background=bg_color)
    style.configure("TLabel", background=bg_color, foreground=fg_color)
    style.configure("TButton", background=accent_color, foreground="white")
    style.map("TButton", background=[("active", "#005A9E")])
    style.configure("TCheckbutton", background=bg_color, foreground=fg_color)


def toggle_password_visibility(entry: ttk.Entry):
    """Toggle password visibility in an entry widget."""
    if entry.cget("show") == "*":
        entry.config(show="")
    else:
        entry.config(show="*")
