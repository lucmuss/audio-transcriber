"""
Speaker diarization tab.
"""

import tkinter as tk
import tkinter.simpledialog
from pathlib import Path
from tkinter import filedialog, ttk


def create_diarization_tab(parent: ttk.Frame, gui_instance):
    """Create speaker diarization tab."""
    # Enable Diarization
    enable_frame = ttk.Frame(parent)
    enable_frame.pack(fill=tk.X, padx=10, pady=10)

    ttk.Checkbutton(
        enable_frame,
        text="Enable Speaker Diarization (Automatically uses gpt-4o-transcribe-diarize model)",
        variable=gui_instance.enable_diarization
    ).pack(anchor=tk.W)

    # Diarization Settings Frame
    settings_frame = ttk.LabelFrame(parent, text="Diarization Settings", padding=10)
    settings_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Number of Speakers
    ttk.Label(settings_frame, text="Number of Speakers:").grid(row=0, column=0, sticky=tk.W, pady=5)
    ttk.Spinbox(settings_frame, from_=1, to=20, textvariable=gui_instance.num_speakers, width=10).grid(
        row=0, column=1, padx=5, pady=5, sticky=tk.W
    )
    ttk.Label(settings_frame, text="(Optional: leave for auto-detection)", font=("", 9)).grid(
        row=0, column=2, sticky=tk.W, padx=5
    )

    # Known Speaker Names
    ttk.Label(settings_frame, text="Known Speaker Names:").grid(row=1, column=0, sticky=tk.NW, pady=5)

    names_frame = ttk.Frame(settings_frame)
    names_frame.grid(row=1, column=1, columnspan=2, sticky=tk.W, padx=5, pady=5)

    gui_instance.speaker_names_list = tk.Listbox(names_frame, height=4, width=40)
    gui_instance.speaker_names_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    names_scrollbar = ttk.Scrollbar(names_frame, orient=tk.VERTICAL, command=gui_instance.speaker_names_list.yview)
    gui_instance.speaker_names_list.configure(yscrollcommand=names_scrollbar.set)
    names_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    names_btn_frame = ttk.Frame(settings_frame)
    names_btn_frame.grid(row=2, column=1, columnspan=2, sticky=tk.W, padx=5, pady=5)

    ttk.Button(names_btn_frame, text="Add Name", command=lambda: add_speaker_name(gui_instance)).pack(side=tk.LEFT, padx=2)
    ttk.Button(names_btn_frame, text="Remove Selected", command=lambda: remove_speaker_name(gui_instance)).pack(side=tk.LEFT, padx=2)

    # Known Speaker References (Audio Files)
    ttk.Label(settings_frame, text="Reference Audio Files:").grid(row=3, column=0, sticky=tk.NW, pady=5)

    refs_frame = ttk.Frame(settings_frame)
    refs_frame.grid(row=3, column=1, columnspan=2, sticky=tk.W, padx=5, pady=5)

    gui_instance.speaker_refs_list = tk.Listbox(refs_frame, height=4, width=40)
    gui_instance.speaker_refs_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    refs_scrollbar = ttk.Scrollbar(refs_frame, orient=tk.VERTICAL, command=gui_instance.speaker_refs_list.yview)
    gui_instance.speaker_refs_list.configure(yscrollcommand=refs_scrollbar.set)
    refs_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    refs_btn_frame = ttk.Frame(settings_frame)
    refs_btn_frame.grid(row=4, column=1, columnspan=2, sticky=tk.W, padx=5, pady=5)

    ttk.Button(refs_btn_frame, text="Add Audio File", command=lambda: add_speaker_reference(gui_instance)).pack(side=tk.LEFT, padx=2)
    ttk.Button(refs_btn_frame, text="Remove Selected", command=lambda: remove_speaker_reference(gui_instance)).pack(side=tk.LEFT, padx=2)

    # Info Frame
    info_frame = ttk.LabelFrame(parent, text="Information", padding=10)
    info_frame.pack(fill=tk.X, padx=10, pady=10)

    info_text = """Speaker Diarization identifies different speakers in the audio.

Options:
• Number of Speakers: Expected speaker count (auto-detected if not set)
• Known Speaker Names: List of speaker names to identify
• Reference Audio: Audio samples of known speakers for better identification

Note: Diarization requires specific models and may incur additional costs."""

    ttk.Label(info_frame, text=info_text, justify=tk.LEFT).pack(anchor=tk.W)


def add_speaker_name(gui_instance):
    """Add a speaker name to the list."""
    name = tk.simpledialog.askstring("Add Speaker", "Enter speaker name:")
    if name and name.strip():
        gui_instance.speaker_names_list.insert(tk.END, name.strip())
        gui_instance.known_speaker_names.append(name.strip())


def remove_speaker_name(gui_instance):
    """Remove selected speaker name."""
    selection = gui_instance.speaker_names_list.curselection()
    if selection:
        index = selection[0]
        gui_instance.speaker_names_list.delete(index)
        if index < len(gui_instance.known_speaker_names):
            gui_instance.known_speaker_names.pop(index)


def add_speaker_reference(gui_instance):
    """Add a reference audio file."""
    filename = filedialog.askopenfilename(
        title="Select Reference Audio",
        filetypes=[("Audio Files", "*.mp3 *.wav *.m4a *.flac *.ogg"), ("All Files", "*.*")]
    )
    if filename:
        gui_instance.speaker_refs_list.insert(tk.END, Path(filename).name)
        gui_instance.known_speaker_references.append(filename)


def remove_speaker_reference(gui_instance):
    """Remove selected reference audio."""
    selection = gui_instance.speaker_refs_list.curselection()
    if selection:
        index = selection[0]
        gui_instance.speaker_refs_list.delete(index)
        if index < len(gui_instance.known_speaker_references):
            gui_instance.known_speaker_references.pop(index)
