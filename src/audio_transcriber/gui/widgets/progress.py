"""
Progress and control widgets.
"""

import tkinter as tk
from tkinter import scrolledtext, ttk


def create_progress_section(parent: tk.Widget, gui_instance) -> tuple:
    """
    Create bottom section with progress display and control buttons.
    
    Returns:
        Tuple of (progress_bar, progress_label, eta_label, throughput_label, cost_label, log_text, 
                  start_button, stop_button)
    """
    bottom_frame = ttk.Frame(parent)
    bottom_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Progress Section
    progress_frame = ttk.LabelFrame(bottom_frame, text="Progress", padding=10)
    progress_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

    # Progress bar with percentage
    progress_bar_frame = ttk.Frame(progress_frame)
    progress_bar_frame.pack(fill=tk.X, pady=(0, 10))

    progress_bar = ttk.Progressbar(
        progress_bar_frame, orient="horizontal", length=400, mode="determinate"
    )
    progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

    progress_label = ttk.Label(progress_bar_frame, text="0%", width=10)
    progress_label.pack(side=tk.LEFT)

    # Stats frame for ETA, throughput, cost
    stats_frame = ttk.Frame(progress_frame)
    stats_frame.pack(fill=tk.X, pady=(0, 10))

    eta_label = ttk.Label(stats_frame, text="ETA: --", font=("", 9))
    eta_label.pack(side=tk.LEFT, padx=(0, 20))

    throughput_label = ttk.Label(stats_frame, text="Durchsatz: --", font=("", 9))
    throughput_label.pack(side=tk.LEFT, padx=(0, 20))

    cost_label = ttk.Label(stats_frame, text="Kosten: $0.0000", font=("", 9))
    cost_label.pack(side=tk.LEFT)

    # Log output
    log_text = scrolledtext.ScrolledText(
        progress_frame, height=5, width=80, state=tk.DISABLED, wrap=tk.WORD
    )
    log_text.pack(fill=tk.BOTH, expand=True)

    # Control Buttons
    button_frame = ttk.Frame(bottom_frame)
    button_frame.pack(fill=tk.X)

    start_button = ttk.Button(
        button_frame,
        text="Start Transcription",
        command=gui_instance.start_transcription,
        style="Accent.TButton",
    )
    start_button.pack(side=tk.LEFT, padx=5)

    stop_button = ttk.Button(
        button_frame, text="Stop", command=gui_instance.stop_transcription, state=tk.DISABLED
    )
    stop_button.pack(side=tk.LEFT, padx=5)

    clear_log_button = ttk.Button(button_frame, text="Clear Log", command=lambda: clear_log(log_text, gui_instance.root))
    clear_log_button.pack(side=tk.LEFT, padx=5)

    quit_button = ttk.Button(button_frame, text="Quit", command=gui_instance.root.quit)
    quit_button.pack(side=tk.RIGHT, padx=5)

    return (progress_bar, progress_label, eta_label, throughput_label, cost_label, log_text, 
            start_button, stop_button)


def clear_log(log_text: scrolledtext.ScrolledText, root: tk.Tk):
    """Clear log output."""
    log_text.config(state=tk.NORMAL)
    log_text.delete("1.0", tk.END)
    log_text.config(state=tk.DISABLED)
    root.update()
