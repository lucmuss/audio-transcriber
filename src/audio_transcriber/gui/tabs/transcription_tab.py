"""
Transcription settings tab.
"""

import tkinter as tk
from tkinter import ttk


def create_transcription_tab(parent: ttk.Frame, gui_instance):
    """Create transcription settings tab."""
    trans_settings_frame = ttk.LabelFrame(parent, text="Transcription Settings", padding=10)
    trans_settings_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Language
    lang_iso_label = ttk.Label(trans_settings_frame, text="Language (ISO 639-1):")
    lang_iso_label.grid(row=0, column=0, sticky=tk.W, pady=5)

    lang_entry = ttk.Entry(trans_settings_frame, textvariable=gui_instance.language, width=10)
    lang_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

    lang_hint_label = ttk.Label(trans_settings_frame, text="(e.g., en, de, fr - leave empty for auto-detect)", font=("", 9))
    lang_hint_label.grid(row=0, column=2, sticky=tk.W, padx=5)

    auto_detect_check = ttk.Checkbutton(
        trans_settings_frame, text="Auto-detect language", variable=gui_instance.detect_language
    )
    auto_detect_check.grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=2)

    # Temperature
    temp_label = ttk.Label(trans_settings_frame, text="Temperature:")
    temp_label.grid(row=2, column=0, sticky=tk.W, pady=5)

    ttk.Spinbox(
        trans_settings_frame, from_=0.0, to=1.0, increment=0.1, textvariable=gui_instance.temperature, width=10
    ).grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)

    # Prompt
    prompt_label = ttk.Label(trans_settings_frame, text="Context Prompt:")
    prompt_label.grid(row=3, column=0, sticky=tk.NW, pady=5)

    prompt_text = tk.Text(trans_settings_frame, width=50, height=4)
    prompt_text.grid(row=3, column=1, columnspan=2, padx=5, pady=5, sticky=tk.W)
    prompt_text.insert("1.0", gui_instance.prompt.get())

    # Bind text widget to variable
    def update_prompt(*args):
        gui_instance.prompt.set(prompt_text.get("1.0", tk.END).strip())

    prompt_text.bind("<KeyRelease>", update_prompt)

    prompt_tip_label = ttk.Label(
        trans_settings_frame,
        text="Provide context like names, technical terms for better accuracy",
        font=("", 9),
    )
    prompt_tip_label.grid(row=4, column=1, columnspan=2, sticky=tk.W, padx=5)
