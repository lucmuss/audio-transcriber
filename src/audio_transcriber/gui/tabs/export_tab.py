"""
Export settings tab.
"""

import tkinter as tk
from tkinter import filedialog, ttk


def create_export_tab(parent: ttk.Frame, gui_instance):
    """Create export settings tab."""
    # Export Formats Frame
    formats_frame = ttk.LabelFrame(parent, text="Export Formats", padding=10)
    formats_frame.pack(fill=tk.X, padx=10, pady=10)

    ttk.Label(formats_frame, text="Select additional export formats:").pack(anchor=tk.W, pady=(0, 10))

    # Checkboxes for each format
    gui_instance.export_docx_var = tk.BooleanVar(value=False)
    gui_instance.export_md_var = tk.BooleanVar(value=False)
    gui_instance.export_latex_var = tk.BooleanVar(value=False)

    ttk.Checkbutton(formats_frame, text="DOCX (Microsoft Word)", variable=gui_instance.export_docx_var).pack(anchor=tk.W, pady=2)
    ttk.Checkbutton(formats_frame, text="Markdown (.md)", variable=gui_instance.export_md_var).pack(anchor=tk.W, pady=2)
    ttk.Checkbutton(formats_frame, text="LaTeX (.tex)", variable=gui_instance.export_latex_var).pack(anchor=tk.W, pady=2)

    # Export Settings Frame
    settings_frame = ttk.LabelFrame(parent, text="Export Settings", padding=10)
    settings_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Export Directory
    ttk.Label(settings_frame, text="Export Directory:").grid(row=0, column=0, sticky=tk.W, pady=5)
    ttk.Entry(settings_frame, textvariable=gui_instance.export_dir, width=50).grid(row=0, column=1, padx=5, pady=5)
    ttk.Button(settings_frame, text="Browse", command=lambda: browse_export_dir(gui_instance)).grid(row=0, column=2, padx=2)

    # Document Title
    ttk.Label(settings_frame, text="Document Title:").grid(row=1, column=0, sticky=tk.W, pady=5)
    ttk.Entry(settings_frame, textvariable=gui_instance.export_title, width=50).grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
    ttk.Label(settings_frame, text="(Optional - uses filename if empty)", font=("", 9)).grid(row=1, column=2, sticky=tk.W, padx=5)

    # Document Author
    ttk.Label(settings_frame, text="Author:").grid(row=2, column=0, sticky=tk.W, pady=5)
    ttk.Entry(settings_frame, textvariable=gui_instance.export_author, width=50).grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
    ttk.Label(settings_frame, text="(Optional)", font=("", 9)).grid(row=2, column=2, sticky=tk.W, padx=5)

    # Info Frame
    info_frame = ttk.LabelFrame(parent, text="Information", padding=10)
    info_frame.pack(fill=tk.X, padx=10, pady=10)

    info_text = """Export transcriptions to additional formats for various use cases:

• DOCX: Microsoft Word documents with metadata and formatting
• Markdown: Clean, portable text format for documentation
• LaTeX: Scientific/academic documents with proper formatting

All formats include metadata (title, author, date, duration, etc.)"""

    ttk.Label(info_frame, text=info_text, justify=tk.LEFT).pack(anchor=tk.W)


def browse_export_dir(gui_instance):
    """Browse for export directory."""
    directory = filedialog.askdirectory(title="Select Export Directory")
    if directory:
        gui_instance.export_dir.set(directory)
