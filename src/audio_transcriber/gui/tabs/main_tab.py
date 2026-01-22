"""
Main tab for input/output and behavior settings.
"""

import tkinter as tk
from tkinter import filedialog, ttk
from pathlib import Path

from ...constants import VALID_RESPONSE_FORMATS


def create_main_tab(parent: ttk.Frame, gui_instance):
    """Create main settings tab with input/output and behavior options."""
    # Input Section
    input_frame = ttk.LabelFrame(parent, text="Input", padding=10)
    input_frame.pack(fill=tk.X, padx=10, pady=10)

    label1 = ttk.Label(input_frame, text="Audio File or Folder:")
    label1.grid(row=0, column=0, sticky=tk.W, pady=5)

    ttk.Entry(input_frame, textvariable=gui_instance.input_path, width=50).grid(
        row=0, column=1, padx=5, pady=5
    )

    choose_file_btn = ttk.Button(
        input_frame, text="Choose File", command=lambda: browse_file(gui_instance)
    )
    choose_file_btn.grid(row=0, column=2, padx=2)

    choose_folder_btn = ttk.Button(
        input_frame, text="Choose Folder", command=lambda: browse_directory(gui_instance)
    )
    choose_folder_btn.grid(row=0, column=3, padx=2)

    # Output Section
    output_frame = ttk.LabelFrame(parent, text="Output", padding=10)
    output_frame.pack(fill=tk.X, padx=10, pady=10)

    label2 = ttk.Label(output_frame, text="Transcription Folder:")
    label2.grid(row=0, column=0, sticky=tk.W, pady=5)

    ttk.Entry(output_frame, textvariable=gui_instance.output_dir, width=50).grid(
        row=0, column=1, padx=5, pady=5
    )

    browse_output_btn = ttk.Button(
        output_frame, text="Browse", command=lambda: browse_output(gui_instance)
    )
    browse_output_btn.grid(row=0, column=2, padx=2)

    label3 = ttk.Label(output_frame, text="Segments Folder:")
    label3.grid(row=1, column=0, sticky=tk.W, pady=5)

    ttk.Entry(output_frame, textvariable=gui_instance.segments_dir, width=50).grid(
        row=1, column=1, padx=5, pady=5
    )

    browse_segments_btn = ttk.Button(
        output_frame, text="Browse", command=lambda: browse_segments(gui_instance)
    )
    browse_segments_btn.grid(row=1, column=2, padx=2)

    label4 = ttk.Label(output_frame, text="Output Format:")
    label4.grid(row=2, column=0, sticky=tk.W, pady=5)

    format_combo = ttk.Combobox(
        output_frame,
        textvariable=gui_instance.response_format,
        values=list(VALID_RESPONSE_FORMATS),
        state="readonly",
        width=20,
    )
    format_combo.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)

    # Behavior Options
    behavior_frame = ttk.LabelFrame(parent, text="Behavior", padding=10)
    behavior_frame.pack(fill=tk.X, padx=10, pady=10)

    ttk.Checkbutton(
        behavior_frame, text="Keep segment files", variable=gui_instance.keep_segments
    ).grid(row=0, column=0, sticky=tk.W, pady=2)

    ttk.Checkbutton(
        behavior_frame,
        text="Skip existing files",
        variable=gui_instance.skip_existing,
    ).grid(row=1, column=0, sticky=tk.W, pady=2)

    ttk.Checkbutton(
        behavior_frame, text="Verbose logging", variable=gui_instance.verbose
    ).grid(row=2, column=0, sticky=tk.W, pady=2)

    # Advanced Settings (Segmentation & Performance)
    advanced_frame = ttk.LabelFrame(parent, text="Advanced Settings", padding=10)
    advanced_frame.pack(fill=tk.X, padx=10, pady=10)

    # Segment length
    seg_length_label = ttk.Label(advanced_frame, text="Segment Length (seconds):")
    seg_length_label.grid(row=0, column=0, sticky=tk.W, pady=5)

    ttk.Spinbox(advanced_frame, from_=60, to=1800, textvariable=gui_instance.segment_length, width=10).grid(
        row=0, column=1, padx=5, pady=5, sticky=tk.W
    )

    # Overlap
    overlap_label = ttk.Label(advanced_frame, text="Overlap (seconds):")
    overlap_label.grid(row=1, column=0, sticky=tk.W, pady=5)

    ttk.Spinbox(advanced_frame, from_=0, to=60, textvariable=gui_instance.overlap, width=10).grid(
        row=1, column=1, padx=5, pady=5, sticky=tk.W
    )

    # Concurrency
    parallel_label = ttk.Label(advanced_frame, text="Parallel Transcriptions:")
    parallel_label.grid(row=2, column=0, sticky=tk.W, pady=5)

    ttk.Spinbox(advanced_frame, from_=1, to=16, textvariable=gui_instance.concurrency, width=10).grid(
        row=2, column=1, padx=5, pady=5, sticky=tk.W
    )


def browse_file(gui_instance):
    """Browse for audio file."""
    filename = filedialog.askopenfilename(
        title="Audio-Datei wählen",
        filetypes=[
            ("Audio-Dateien", "*.mp3 *.wav *.m4a *.flac *.ogg *.aac *.wma *.mp4"),
            ("Alle Dateien", "*.*"),
        ],
    )
    if filename:
        gui_instance.input_path.set(filename)


def browse_directory(gui_instance):
    """Browse for directory."""
    directory = filedialog.askdirectory(title="Ordner mit Audio-Dateien wählen")
    if directory:
        gui_instance.input_path.set(directory)


def browse_output(gui_instance):
    """Browse for output directory."""
    directory = filedialog.askdirectory(title="Ausgabe-Ordner wählen")
    if directory:
        gui_instance.output_dir.set(directory)


def browse_segments(gui_instance):
    """Browse for segments directory."""
    directory = filedialog.askdirectory(title="Segment-Ordner wählen")
    if directory:
        gui_instance.segments_dir.set(directory)
