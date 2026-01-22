"""
API configuration tab.
"""

import tkinter as tk
from tkinter import ttk

from ...constants import DEFAULT_BASE_URL


def create_api_tab(parent: ttk.Frame, gui_instance):
    """Create API configuration tab."""
    api_settings_frame = ttk.LabelFrame(parent, text="API Settings", padding=10)
    api_settings_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # API Key
    api_key_label = ttk.Label(api_settings_frame, text="API Key:")
    api_key_label.grid(row=0, column=0, sticky=tk.W, pady=5)

    api_entry = ttk.Entry(api_settings_frame, textvariable=gui_instance.api_key, width=50, show="*")
    api_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

    from ..utils import toggle_password_visibility
    show_password_btn = ttk.Button(
        api_settings_frame, text="Show", command=lambda: toggle_password_visibility(api_entry)
    )
    show_password_btn.grid(row=0, column=2, padx=2)

    # Base URL
    base_url_label = ttk.Label(api_settings_frame, text="Base URL:")
    base_url_label.grid(row=1, column=0, sticky=tk.W, pady=5)

    ttk.Entry(api_settings_frame, textvariable=gui_instance.base_url, width=50).grid(
        row=1, column=1, padx=5, pady=5, sticky=tk.W
    )

    # Model
    model_label = ttk.Label(api_settings_frame, text="Model:")
    model_label.grid(row=2, column=0, sticky=tk.W, pady=5)

    ttk.Entry(api_settings_frame, textvariable=gui_instance.model, width=50).grid(
        row=2, column=1, padx=5, pady=5, sticky=tk.W
    )

    # Info Frame
    provider_examples_frame = ttk.LabelFrame(parent, text="Provider Examples", padding=10)
    provider_examples_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    info_text = """
OpenAI:
  Base URL: https://api.openai.com/v1
  Models: whisper-1, gpt-4o-transcribe, gpt-4o-mini-transcribe,
          gpt-4o-mini-transcribe-2025-12-15

Groq:
  Base URL: https://api.groq.com/openai/v1
  Model: whisper-large-v3

Ollama (Local):
  Base URL: http://localhost:11434/v1
  API Key: ollama
  Model: whisper

Together.ai:
  Base URL: https://api.together.xyz/v1
  Model: whisper-large-v3
    """

    ttk.Label(provider_examples_frame, text=info_text, justify=tk.LEFT, font=("Courier", 9)).pack(
        anchor=tk.W
    )
