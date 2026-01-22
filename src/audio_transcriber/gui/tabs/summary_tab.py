"""
Summarization settings tab.
"""

import tkinter as tk
from tkinter import filedialog, ttk


def create_summary_tab(parent: ttk.Frame, gui_instance):
    """Create summarization settings tab."""
    # Enable Summarization
    summarize_check = ttk.Checkbutton(
        parent, text="Zusammenfassung erstellen", variable=gui_instance.summarize
    )
    summarize_check.pack(anchor=tk.W, padx=10, pady=10)

    # Summary Settings Frame
    summary_settings_frame = ttk.LabelFrame(parent, text="Zusammenfassungs-Einstellungen", padding=10)
    summary_settings_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Summary Directory
    summary_dir_label = ttk.Label(summary_settings_frame, text="Summary-Ordner:")
    summary_dir_label.grid(row=0, column=0, sticky=tk.W, pady=5)

    ttk.Entry(summary_settings_frame, textvariable=gui_instance.summary_dir, width=50).grid(
        row=0, column=1, padx=5, pady=5
    )

    browse_summary_btn = ttk.Button(
        summary_settings_frame, text="Durchsuchen", command=lambda: browse_summary_dir(gui_instance)
    )
    browse_summary_btn.grid(row=0, column=2, padx=2)

    # Summary Model
    summary_model_label = ttk.Label(summary_settings_frame, text="Summary-Modell:")
    summary_model_label.grid(row=1, column=0, sticky=tk.W, pady=5)

    ttk.Entry(summary_settings_frame, textvariable=gui_instance.summary_model, width=50).grid(
        row=1, column=1, padx=5, pady=5, sticky=tk.W
    )

    model_hint = ttk.Label(
        summary_settings_frame,
        text="(z.B. gpt-4o-mini, gpt-4, gpt-3.5-turbo)",
        font=("", 9)
    )
    model_hint.grid(row=1, column=2, sticky=tk.W, padx=5)

    # Summary Prompt
    summary_prompt_label = ttk.Label(summary_settings_frame, text="Summary-Prompt:")
    summary_prompt_label.grid(row=2, column=0, sticky=tk.NW, pady=5)

    summary_prompt_text = tk.Text(summary_settings_frame, width=50, height=6)
    summary_prompt_text.grid(row=2, column=1, columnspan=2, padx=5, pady=5, sticky=tk.W)
    summary_prompt_text.insert("1.0", gui_instance.summary_prompt.get())

    # Bind text widget to variable
    def update_summary_prompt(*args):
        gui_instance.summary_prompt.set(summary_prompt_text.get("1.0", tk.END).strip())

    summary_prompt_text.bind("<KeyRelease>", update_summary_prompt)

    summary_tip_label = ttk.Label(
        summary_settings_frame,
        text="Beschreiben Sie, wie die Zusammenfassung erstellt werden soll",
        font=("", 9),
    )
    summary_tip_label.grid(row=3, column=1, columnspan=2, sticky=tk.W, padx=5)

    # Info Frame
    info_frame = ttk.LabelFrame(parent, text="Information", padding=10)
    info_frame.pack(fill=tk.X, padx=10, pady=10)

    info_text = """Die Zusammenfassungs-Funktion nutzt ein LLM (Large Language Model), 
um automatisch eine prägnante Zusammenfassung der Transkription zu erstellen. 

Die Zusammenfassung wird im angegebenen Summary-Ordner gespeichert.

Hinweis: Dies verursacht zusätzliche API-Kosten basierend auf der 
Länge der Transkription und dem gewählten Modell."""

    ttk.Label(info_frame, text=info_text, justify=tk.LEFT).pack(anchor=tk.W)


def browse_summary_dir(gui_instance):
    """Browse for summary directory."""
    directory = filedialog.askdirectory(title="Summary-Ordner wählen")
    if directory:
        gui_instance.summary_dir.set(directory)
