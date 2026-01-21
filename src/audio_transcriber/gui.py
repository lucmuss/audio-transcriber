"""
Graphical User Interface for Audio Transcriber using Tkinter with i18n support.
"""

import os
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, scrolledtext, ttk
from typing import Any, Dict, Optional, Tuple

from . import __version__
from .constants import (
    DEFAULT_BASE_URL,
    DEFAULT_CONCURRENCY,
    DEFAULT_MODEL,
    DEFAULT_OVERLAP,
    DEFAULT_RESPONSE_FORMAT,
    DEFAULT_SEGMENT_LENGTH,
    DEFAULT_SUMMARY_MODEL,
    DEFAULT_SUMMARY_PROMPT,
    DEFAULT_TEMPERATURE,
    ENV_PREFIX,
    VALID_RESPONSE_FORMATS,
)
from .i18n import I18n, LANGUAGE_NAMES
from .transcriber import AudioTranscriber
from .utils import find_audio_files, setup_logging


class AudioTranscriberGUI:
    """Main GUI application for Audio Transcriber."""

    def __init__(self, root: tk.Tk):
        """Initialize the GUI."""
        self.root = root
        self.root.geometry("900x900")
        self.root.resizable(True, True)

        # Initialize i18n (detect system language or default to English)
        self.i18n = I18n("de")  # Default to German for this user
        self.current_language = tk.StringVar(value="de")

        # Set window title with i18n
        self.root.title(f"{self.i18n.get('window_title')} v{__version__}")

        # Variables
        self.input_path = tk.StringVar()
        self.output_dir = tk.StringVar(value="./transcriptions")
        self.segments_dir = tk.StringVar(value="./segments")

        # API Configuration
        self.api_key = tk.StringVar(value=os.getenv(f"{ENV_PREFIX}API_KEY", ""))
        self.base_url = tk.StringVar(value=os.getenv(f"{ENV_PREFIX}BASE_URL", DEFAULT_BASE_URL))
        self.model = tk.StringVar(value=os.getenv(f"{ENV_PREFIX}MODEL", DEFAULT_MODEL))

        # Segmentation
        self.segment_length = tk.IntVar(value=DEFAULT_SEGMENT_LENGTH)
        self.overlap = tk.IntVar(value=DEFAULT_OVERLAP)

        # Transcription
        self.language = tk.StringVar(value="")
        self.detect_language = tk.BooleanVar(value=True)
        self.temperature = tk.DoubleVar(value=DEFAULT_TEMPERATURE)
        self.prompt = tk.StringVar(value="")
        self.response_format = tk.StringVar(value=DEFAULT_RESPONSE_FORMAT)

        # Performance
        self.concurrency = tk.IntVar(value=DEFAULT_CONCURRENCY)

        # Behavior
        self.keep_segments = tk.BooleanVar(value=False)
        self.skip_existing = tk.BooleanVar(value=True)
        self.verbose = tk.BooleanVar(value=False)

        # Summarization
        self.summarize = tk.BooleanVar(value=False)
        self.summary_dir = tk.StringVar(value="./summaries")
        self.summary_model = tk.StringVar(value=os.getenv(f"{ENV_PREFIX}SUMMARY_MODEL", DEFAULT_SUMMARY_MODEL))
        self.summary_prompt = tk.StringVar(value=DEFAULT_SUMMARY_PROMPT)

        # Processing state
        self.is_processing = False
        self.current_thread: Optional[threading.Thread] = None

        # Store widget references for i18n updates
        self.widgets_to_translate: dict = {}

        # Build UI
        self.create_widgets()

        # Apply theme
        self.apply_theme()

        # Initial text update
        self._update_texts()

    def apply_theme(self):
        """Apply modern theme to the GUI."""
        style = ttk.Style()
        style.theme_use("clam")

        # Configure colors
        bg_color = "#f0f0f0"
        fg_color = "#333333"
        accent_color = "#007ACC"

        self.root.configure(bg=bg_color)

        style.configure("TFrame", background=bg_color)
        style.configure("TLabel", background=bg_color, foreground=fg_color)
        style.configure("TButton", background=accent_color, foreground="white")
        style.map("TButton", background=[("active", "#005A9E")])
        style.configure("TCheckbutton", background=bg_color, foreground=fg_color)

    def create_widgets(self):
        """Create all GUI widgets."""
        # Language selector at top
        lang_frame = ttk.Frame(self.root)
        lang_frame.pack(fill=tk.X, padx=10, pady=(10, 0))

        lang_label = ttk.Label(lang_frame, text=self.i18n.get("language_selector"))
        lang_label.pack(side=tk.LEFT, padx=(0, 5))
        self.widgets_to_translate["lang_label"] = ("language_selector", lang_label)

        lang_combo = ttk.Combobox(
            lang_frame,
            textvariable=self.current_language,
            values=list(LANGUAGE_NAMES.keys()),
            state="readonly",
            width=15,
        )
        lang_combo.pack(side=tk.LEFT)
        lang_combo.bind("<<ComboboxSelected>>", self._change_language)

        # Display language names
        def format_lang(code):
            return f"{code} - {LANGUAGE_NAMES.get(code, code)}"

        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Tab 1: Main Settings
        self.main_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.main_frame, text=self.i18n.get("tab_main"))
        self.create_main_tab(self.main_frame)

        # Tab 2: API Configuration
        self.api_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.api_frame, text=self.i18n.get("tab_api"))
        self.create_api_tab(self.api_frame)

        # Tab 3: Advanced Settings
        self.advanced_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.advanced_frame, text=self.i18n.get("tab_advanced"))
        self.create_advanced_tab(self.advanced_frame)

        # Tab 4: Transcription Settings
        self.trans_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.trans_frame, text=self.i18n.get("tab_transcription"))
        self.create_transcription_tab(self.trans_frame)

        # Tab 5: Summarization Settings
        self.summary_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.summary_frame, text="Zusammenfassung")
        self.create_summarization_tab(self.summary_frame)

        # Bottom: Progress and Control
        self.create_bottom_section()

    def create_main_tab(self, parent: ttk.Frame):
        """Create main settings tab."""
        # Input Section
        self.input_frame = ttk.LabelFrame(parent, text=self.i18n.get("input"), padding=10)
        self.input_frame.pack(fill=tk.X, padx=10, pady=10)

        label1 = ttk.Label(self.input_frame, text=self.i18n.get("audio_file_or_folder"))
        label1.grid(row=0, column=0, sticky=tk.W, pady=5)
        self.widgets_to_translate["audio_label"] = ("audio_file_or_folder", label1)

        ttk.Entry(self.input_frame, textvariable=self.input_path, width=50).grid(
            row=0, column=1, padx=5, pady=5
        )

        self.choose_file_btn = ttk.Button(
            self.input_frame, text=self.i18n.get("choose_file"), command=self.browse_file
        )
        self.choose_file_btn.grid(row=0, column=2, padx=2)
        self.widgets_to_translate["choose_file_btn"] = ("choose_file", self.choose_file_btn)

        self.choose_folder_btn = ttk.Button(
            self.input_frame, text=self.i18n.get("choose_folder"), command=self.browse_directory
        )
        self.choose_folder_btn.grid(row=0, column=3, padx=2)
        self.widgets_to_translate["choose_folder_btn"] = ("choose_folder", self.choose_folder_btn)

        # Output Section
        self.output_frame = ttk.LabelFrame(parent, text=self.i18n.get("output"), padding=10)
        self.output_frame.pack(fill=tk.X, padx=10, pady=10)

        label2 = ttk.Label(self.output_frame, text=self.i18n.get("transcription_folder"))
        label2.grid(row=0, column=0, sticky=tk.W, pady=5)
        self.widgets_to_translate["trans_folder_label"] = ("transcription_folder", label2)

        ttk.Entry(self.output_frame, textvariable=self.output_dir, width=50).grid(
            row=0, column=1, padx=5, pady=5
        )

        self.browse_output_btn = ttk.Button(
            self.output_frame, text=self.i18n.get("browse"), command=self.browse_output
        )
        self.browse_output_btn.grid(row=0, column=2, padx=2)
        self.widgets_to_translate["browse_output_btn"] = ("browse", self.browse_output_btn)

        label3 = ttk.Label(self.output_frame, text=self.i18n.get("segment_folder"))
        label3.grid(row=1, column=0, sticky=tk.W, pady=5)
        self.widgets_to_translate["segment_folder_label"] = ("segment_folder", label3)

        ttk.Entry(self.output_frame, textvariable=self.segments_dir, width=50).grid(
            row=1, column=1, padx=5, pady=5
        )

        self.browse_segments_btn = ttk.Button(
            self.output_frame, text=self.i18n.get("browse"), command=self.browse_segments
        )
        self.browse_segments_btn.grid(row=1, column=2, padx=2)
        self.widgets_to_translate["browse_segments_btn"] = ("browse", self.browse_segments_btn)

        label4 = ttk.Label(self.output_frame, text=self.i18n.get("output_format"))
        label4.grid(row=2, column=0, sticky=tk.W, pady=5)
        self.widgets_to_translate["format_label"] = ("output_format", label4)

        format_combo = ttk.Combobox(
            self.output_frame,
            textvariable=self.response_format,
            values=list(VALID_RESPONSE_FORMATS),
            state="readonly",
            width=20,
        )
        format_combo.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)

        # Behavior Options
        self.behavior_frame = ttk.LabelFrame(parent, text=self.i18n.get("behavior"), padding=10)
        self.behavior_frame.pack(fill=tk.X, padx=10, pady=10)

        self.keep_seg_check = ttk.Checkbutton(
            self.behavior_frame, text=self.i18n.get("keep_segments"), variable=self.keep_segments
        )
        self.keep_seg_check.grid(row=0, column=0, sticky=tk.W, pady=2)
        self.widgets_to_translate["keep_seg_check"] = ("keep_segments", self.keep_seg_check)

        self.skip_exist_check = ttk.Checkbutton(
            self.behavior_frame,
            text=self.i18n.get("skip_existing"),
            variable=self.skip_existing,
        )
        self.skip_exist_check.grid(row=1, column=0, sticky=tk.W, pady=2)
        self.widgets_to_translate["skip_exist_check"] = ("skip_existing", self.skip_exist_check)

        self.verbose_check = ttk.Checkbutton(
            self.behavior_frame, text=self.i18n.get("verbose_logging"), variable=self.verbose
        )
        self.verbose_check.grid(row=2, column=0, sticky=tk.W, pady=2)
        self.widgets_to_translate["verbose_check"] = ("verbose_logging", self.verbose_check)

    def create_api_tab(self, parent: ttk.Frame):
        """Create API configuration tab."""
        self.api_settings_frame = ttk.LabelFrame(parent, text=self.i18n.get("api_settings"), padding=10)
        self.api_settings_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.widgets_to_translate["api_settings_frame"] = ("api_settings", self.api_settings_frame)

        # API Key
        api_key_label = ttk.Label(self.api_settings_frame, text=self.i18n.get("api_key_label"))
        api_key_label.grid(row=0, column=0, sticky=tk.W, pady=5)
        self.widgets_to_translate["api_key_label"] = ("api_key_label", api_key_label)
        
        api_entry = ttk.Entry(self.api_settings_frame, textvariable=self.api_key, width=50, show="*")
        api_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

        self.show_password_btn = ttk.Button(
            self.api_settings_frame, text=self.i18n.get("show_password"), command=lambda: self.toggle_password(api_entry)
        )
        self.show_password_btn.grid(row=0, column=2, padx=2)
        self.widgets_to_translate["show_password_btn"] = ("show_password", self.show_password_btn)

        # Base URL
        base_url_label = ttk.Label(self.api_settings_frame, text=self.i18n.get("base_url_label"))
        base_url_label.grid(row=1, column=0, sticky=tk.W, pady=5)
        self.widgets_to_translate["base_url_label"] = ("base_url_label", base_url_label)
        
        ttk.Entry(self.api_settings_frame, textvariable=self.base_url, width=50).grid(
            row=1, column=1, padx=5, pady=5, sticky=tk.W
        )

        # Model
        model_label = ttk.Label(self.api_settings_frame, text=self.i18n.get("model_label"))
        model_label.grid(row=2, column=0, sticky=tk.W, pady=5)
        self.widgets_to_translate["model_label"] = ("model_label", model_label)
        
        ttk.Entry(self.api_settings_frame, textvariable=self.model, width=50).grid(
            row=2, column=1, padx=5, pady=5, sticky=tk.W
        )

        # Info Frame
        self.provider_examples_frame = ttk.LabelFrame(parent, text=self.i18n.get("provider_examples"), padding=10)
        self.provider_examples_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.widgets_to_translate["provider_examples_frame"] = ("provider_examples", self.provider_examples_frame)

        info_text = """
OpenAI:
  Base URL: https://api.openai.com/v1
  Models: whisper-1, gpt-4o-transcribe, gpt-4o-mini-transcribe,
          gpt-4o-mini-transcribe-2025-12-15

Groq:
  Base URL: https://api.groq.com/openai/v1
  Model: whisper-large-v3

Ollama (Lokal):
  Base URL: http://localhost:11434/v1
  API Key: ollama
  Model: whisper

Together.ai:
  Base URL: https://api.together.xyz/v1
  Model: whisper-large-v3
        """

        ttk.Label(self.provider_examples_frame, text=info_text, justify=tk.LEFT, font=("Courier", 9)).pack(
            anchor=tk.W
        )

    def create_advanced_tab(self, parent: ttk.Frame):
        """Create advanced settings tab."""
        # Segmentation Frame
        self.seg_params_frame = ttk.LabelFrame(parent, text=self.i18n.get("segmentation_params"), padding=10)
        self.seg_params_frame.pack(fill=tk.X, padx=10, pady=10)
        self.widgets_to_translate["seg_params_frame"] = ("segmentation_params", self.seg_params_frame)

        seg_length_label = ttk.Label(self.seg_params_frame, text=self.i18n.get("segment_length_label"))
        seg_length_label.grid(row=0, column=0, sticky=tk.W, pady=5)
        self.widgets_to_translate["seg_length_label"] = ("segment_length_label", seg_length_label)
        
        ttk.Spinbox(self.seg_params_frame, from_=60, to=1800, textvariable=self.segment_length, width=10).grid(
            row=0, column=1, padx=5, pady=5, sticky=tk.W
        )

        overlap_label = ttk.Label(self.seg_params_frame, text=self.i18n.get("overlap_label"))
        overlap_label.grid(row=1, column=0, sticky=tk.W, pady=5)
        self.widgets_to_translate["overlap_label"] = ("overlap_label", overlap_label)
        
        ttk.Spinbox(self.seg_params_frame, from_=0, to=60, textvariable=self.overlap, width=10).grid(
            row=1, column=1, padx=5, pady=5, sticky=tk.W
        )

        # Performance Frame
        self.perf_frame = ttk.LabelFrame(parent, text=self.i18n.get("performance"), padding=10)
        self.perf_frame.pack(fill=tk.X, padx=10, pady=10)
        self.widgets_to_translate["perf_frame"] = ("performance", self.perf_frame)

        parallel_label = ttk.Label(self.perf_frame, text=self.i18n.get("parallel_transcriptions_label"))
        parallel_label.grid(row=0, column=0, sticky=tk.W, pady=5)
        self.widgets_to_translate["parallel_label"] = ("parallel_transcriptions_label", parallel_label)
        
        ttk.Spinbox(self.perf_frame, from_=1, to=16, textvariable=self.concurrency, width=10).grid(
            row=0, column=1, padx=5, pady=5, sticky=tk.W
        )

    def create_transcription_tab(self, parent: ttk.Frame):
        """Create transcription settings tab."""
        self.trans_settings_frame = ttk.LabelFrame(parent, text=self.i18n.get("transcription_settings"), padding=10)
        self.trans_settings_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.widgets_to_translate["trans_settings_frame"] = ("transcription_settings", self.trans_settings_frame)

        # Language
        lang_iso_label = ttk.Label(self.trans_settings_frame, text=self.i18n.get("language_iso_label"))
        lang_iso_label.grid(row=0, column=0, sticky=tk.W, pady=5)
        self.widgets_to_translate["lang_iso_label"] = ("language_iso_label", lang_iso_label)
        
        lang_entry = ttk.Entry(self.trans_settings_frame, textvariable=self.language, width=10)
        lang_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        lang_hint_label = ttk.Label(self.trans_settings_frame, text=self.i18n.get("language_hint"), font=("", 9))
        lang_hint_label.grid(row=0, column=2, sticky=tk.W, padx=5)
        self.widgets_to_translate["lang_hint_label"] = ("language_hint", lang_hint_label)

        self.auto_detect_check = ttk.Checkbutton(
            self.trans_settings_frame, text=self.i18n.get("auto_detect_language"), variable=self.detect_language
        )
        self.auto_detect_check.grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=2)
        self.widgets_to_translate["auto_detect_check"] = ("auto_detect_language", self.auto_detect_check)

        # Temperature
        temp_label = ttk.Label(self.trans_settings_frame, text=self.i18n.get("temperature_label"))
        temp_label.grid(row=2, column=0, sticky=tk.W, pady=5)
        self.widgets_to_translate["temp_label"] = ("temperature_label", temp_label)
        
        ttk.Spinbox(
            self.trans_settings_frame, from_=0.0, to=1.0, increment=0.1, textvariable=self.temperature, width=10
        ).grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)

        # Prompt
        prompt_label = ttk.Label(self.trans_settings_frame, text=self.i18n.get("context_prompt_label"))
        prompt_label.grid(row=3, column=0, sticky=tk.NW, pady=5)
        self.widgets_to_translate["prompt_label"] = ("context_prompt_label", prompt_label)
        
        prompt_text = tk.Text(self.trans_settings_frame, width=50, height=4)
        prompt_text.grid(row=3, column=1, columnspan=2, padx=5, pady=5, sticky=tk.W)
        prompt_text.insert("1.0", self.prompt.get())

        # Bind text widget to variable
        def update_prompt(*args):
            self.prompt.set(prompt_text.get("1.0", tk.END).strip())

        prompt_text.bind("<KeyRelease>", update_prompt)

        prompt_tip_label = ttk.Label(
            self.trans_settings_frame,
            text=self.i18n.get("prompt_tip"),
            font=("", 9),
        )
        prompt_tip_label.grid(row=4, column=1, columnspan=2, sticky=tk.W, padx=5)
        self.widgets_to_translate["prompt_tip_label"] = ("prompt_tip", prompt_tip_label)

    def create_summarization_tab(self, parent: ttk.Frame):
        """Create summarization settings tab."""
        # Enable Summarization
        self.summarize_check = ttk.Checkbutton(
            parent, text="Zusammenfassung erstellen", variable=self.summarize
        )
        self.summarize_check.pack(anchor=tk.W, padx=10, pady=10)
        
        # Summary Settings Frame
        self.summary_settings_frame = ttk.LabelFrame(parent, text="Zusammenfassungs-Einstellungen", padding=10)
        self.summary_settings_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Summary Directory
        summary_dir_label = ttk.Label(self.summary_settings_frame, text="Summary-Ordner:")
        summary_dir_label.grid(row=0, column=0, sticky=tk.W, pady=5)
        
        ttk.Entry(self.summary_settings_frame, textvariable=self.summary_dir, width=50).grid(
            row=0, column=1, padx=5, pady=5
        )
        
        browse_summary_btn = ttk.Button(
            self.summary_settings_frame, text="Durchsuchen", command=self.browse_summary_dir
        )
        browse_summary_btn.grid(row=0, column=2, padx=2)

        # Summary Model
        summary_model_label = ttk.Label(self.summary_settings_frame, text="Summary-Modell:")
        summary_model_label.grid(row=1, column=0, sticky=tk.W, pady=5)
        
        ttk.Entry(self.summary_settings_frame, textvariable=self.summary_model, width=50).grid(
            row=1, column=1, padx=5, pady=5, sticky=tk.W
        )
        
        model_hint = ttk.Label(
            self.summary_settings_frame, 
            text="(z.B. gpt-4o-mini, gpt-4, gpt-3.5-turbo)", 
            font=("", 9)
        )
        model_hint.grid(row=1, column=2, sticky=tk.W, padx=5)

        # Summary Prompt
        summary_prompt_label = ttk.Label(self.summary_settings_frame, text="Summary-Prompt:")
        summary_prompt_label.grid(row=2, column=0, sticky=tk.NW, pady=5)
        
        summary_prompt_text = tk.Text(self.summary_settings_frame, width=50, height=6)
        summary_prompt_text.grid(row=2, column=1, columnspan=2, padx=5, pady=5, sticky=tk.W)
        summary_prompt_text.insert("1.0", self.summary_prompt.get())

        # Bind text widget to variable
        def update_summary_prompt(*args):
            self.summary_prompt.set(summary_prompt_text.get("1.0", tk.END).strip())

        summary_prompt_text.bind("<KeyRelease>", update_summary_prompt)

        summary_tip_label = ttk.Label(
            self.summary_settings_frame,
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

    def create_bottom_section(self):
        """Create bottom section with progress and control buttons."""
        bottom_frame = ttk.Frame(self.root)
        bottom_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Progress Section
        self.progress_frame = ttk.LabelFrame(bottom_frame, text=self.i18n.get("progress"), padding=10)
        self.progress_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        self.widgets_to_translate["progress_frame"] = ("progress", self.progress_frame)

        # Log output
        self.log_text = scrolledtext.ScrolledText(
            self.progress_frame, height=10, width=80, state=tk.DISABLED, wrap=tk.WORD
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # Control Buttons
        button_frame = ttk.Frame(bottom_frame)
        button_frame.pack(fill=tk.X)

        self.start_button = ttk.Button(
            button_frame,
            text=self.i18n.get("start_transcription_btn"),
            command=self.start_transcription,
            style="Accent.TButton",
        )
        self.start_button.pack(side=tk.LEFT, padx=5)
        self.widgets_to_translate["start_button"] = ("start_transcription_btn", self.start_button)

        self.stop_button = ttk.Button(
            button_frame, text=self.i18n.get("stop_btn"), command=self.stop_transcription, state=tk.DISABLED
        )
        self.stop_button.pack(side=tk.LEFT, padx=5)
        self.widgets_to_translate["stop_button"] = ("stop_btn", self.stop_button)

        self.clear_log_button = ttk.Button(button_frame, text=self.i18n.get("clear_log_btn"), command=self.clear_log)
        self.clear_log_button.pack(side=tk.LEFT, padx=5)
        self.widgets_to_translate["clear_log_button"] = ("clear_log_btn", self.clear_log_button)

        self.quit_button = ttk.Button(button_frame, text=self.i18n.get("quit_btn"), command=self.root.quit)
        self.quit_button.pack(side=tk.RIGHT, padx=5)
        self.widgets_to_translate["quit_button"] = ("quit_btn", self.quit_button)

    def browse_file(self):
        """Browse for audio file."""
        filename = filedialog.askopenfilename(
            title="Audio-Datei wählen",
            filetypes=[
                ("Audio-Dateien", "*.mp3 *.wav *.m4a *.flac *.ogg *.aac *.wma *.mp4"),
                ("Alle Dateien", "*.*"),
            ],
        )
        if filename:
            self.input_path.set(filename)

    def browse_directory(self):
        """Browse for directory."""
        directory = filedialog.askdirectory(title="Ordner mit Audio-Dateien wählen")
        if directory:
            self.input_path.set(directory)

    def browse_output(self):
        """Browse for output directory."""
        directory = filedialog.askdirectory(title="Ausgabe-Ordner wählen")
        if directory:
            self.output_dir.set(directory)

    def browse_segments(self):
        """Browse for segments directory."""
        directory = filedialog.askdirectory(title="Segment-Ordner wählen")
        if directory:
            self.segments_dir.set(directory)

    def browse_summary_dir(self):
        """Browse for summary directory."""
        directory = filedialog.askdirectory(title="Summary-Ordner wählen")
        if directory:
            self.summary_dir.set(directory)

    def toggle_password(self, entry: ttk.Entry):
        """Toggle password visibility."""
        if entry.cget("show") == "*":
            entry.config(show="")
        else:
            entry.config(show="*")

    def log_message(self, message: str):
        """Add message to log output."""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.root.update()

    def clear_log(self):
        """Clear log output."""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete("1.0", tk.END)
        self.log_text.config(state=tk.DISABLED)

    def validate_inputs(self) -> bool:
        """Validate all inputs before starting."""
        if not self.input_path.get():
            messagebox.showerror(
                "Fehler", "Bitte wählen Sie eine Audio-Datei oder einen Ordner aus."
            )
            return False

        if not self.api_key.get():
            messagebox.showerror("Fehler", "Bitte geben Sie einen API Key ein.")
            return False

        if not Path(self.input_path.get()).exists():
            messagebox.showerror("Fehler", f"Pfad existiert nicht: {self.input_path.get()}")
            return False

        return True

    def start_transcription(self):
        """Start transcription process."""
        if not self.validate_inputs():
            return

        if self.is_processing:
            messagebox.showwarning("Warnung", "Transkription läuft bereits!")
            return

        # Setup logging to GUI
        setup_logging(self.verbose.get())

        # Start in thread to keep GUI responsive
        self.is_processing = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

        self.current_thread = threading.Thread(target=self.run_transcription, daemon=True)
        self.current_thread.start()

    def run_transcription(self):
        """Run transcription in background thread."""
        try:
            self.log_message("=" * 70)
            self.log_message("Audio Transcriber gestartet")
            self.log_message("=" * 70)

            # Find audio files
            input_path = Path(self.input_path.get())
            try:
                audio_files = find_audio_files(input_path)
                self.log_message(f"📁 Gefunden: {len(audio_files)} Audio-Datei(en)")
            except FileNotFoundError as e:
                self.log_message(f"❌ Fehler: {e}")
                messagebox.showerror("Fehler", str(e))
                return

            if not audio_files:
                self.log_message("❌ Keine Audio-Dateien gefunden!")
                messagebox.showwarning("Warnung", "Keine Audio-Dateien gefunden!")
                return

            # Initialize transcriber
            transcriber = AudioTranscriber(
                api_key=self.api_key.get(),
                base_url=self.base_url.get(),
                model=self.model.get(),
            )

            # Process files
            output_dir = Path(self.output_dir.get())
            segments_dir = Path(self.segments_dir.get())

            successful = 0
            failed = 0

            for i, audio_file in enumerate(audio_files, 1):
                if not self.is_processing:
                    self.log_message("\n⏹ Transkription abgebrochen!")
                    break

                self.log_message(f"\n[{i}/{len(audio_files)}] Verarbeite: {audio_file.name}")

                try:
                    result = transcriber.transcribe_file(
                        file_path=audio_file,
                        output_dir=output_dir,
                        segments_dir=segments_dir,
                        segment_length=self.segment_length.get(),
                        overlap=self.overlap.get(),
                        language=self.language.get() or None,
                        detect_language=self.detect_language.get(),
                        response_format=self.response_format.get(),
                        concurrency=self.concurrency.get(),
                        temperature=self.temperature.get(),
                        prompt=self.prompt.get() or None,
                        keep_segments=self.keep_segments.get(),
                        skip_existing=self.skip_existing.get(),
                    )

                    if result["status"] == "success":
                        successful += 1
                        self.log_message(f"✅ Erfolgreich: {result['output']}")
                        
                        # Generate summary if requested
                        if self.summarize.get():
                            self.log_message("📝 Erstelle Zusammenfassung...")
                            try:
                                summary_result = transcriber.summarize_transcription(
                                    transcription_file=Path(result["output"]),
                                    summary_dir=Path(self.summary_dir.get()),
                                    summary_model=self.summary_model.get(),
                                    summary_prompt=self.summary_prompt.get(),
                                    skip_existing=self.skip_existing.get(),
                                )
                                if summary_result["status"] == "success":
                                    self.log_message(f"✅ Summary erstellt: {summary_result['summary_file']}")
                                elif summary_result["status"] == "skipped":
                                    self.log_message("⊘ Summary übersprungen: bereits vorhanden")
                                else:
                                    self.log_message(f"⚠️ Summary-Fehler: {summary_result.get('error', 'Unbekannt')}")
                            except Exception as e:
                                self.log_message(f"⚠️ Summary-Ausnahme: {e}")
                                
                    elif result["status"] == "skipped":
                        self.log_message("⊘ Übersprungen: bereits vorhanden")
                    else:
                        failed += 1
                        self.log_message(f"❌ Fehler: {result.get('error', 'Unbekannt')}")

                except Exception as e:
                    failed += 1
                    self.log_message(f"❌ Ausnahme: {e}")

            # Summary
            self.log_message("\n" + "=" * 70)
            self.log_message("ZUSAMMENFASSUNG")
            self.log_message("=" * 70)
            self.log_message(f"✅ Erfolgreich: {successful}")
            self.log_message(f"❌ Fehlgeschlagen: {failed}")
            self.log_message("=" * 70)

            if failed == 0 and successful > 0:
                messagebox.showinfo(
                    "Fertig",
                    f"Transkription abgeschlossen!\n{successful} Datei(en) erfolgreich verarbeitet.",
                )
            elif failed > 0:
                messagebox.showwarning(
                    "Fertig", f"Transkription abgeschlossen mit {failed} Fehler(n)."
                )

        except Exception as e:
            self.log_message(f"\n❌ Kritischer Fehler: {e}")
            messagebox.showerror("Fehler", f"Kritischer Fehler:\n{e}")

        finally:
            self.is_processing = False
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)

    def stop_transcription(self):
        """Stop transcription process."""
        if self.is_processing:
            self.is_processing = False
            self.log_message("\n⏹ Stoppe Transkription...")

    def _change_language(self, event=None):
        """Change application language."""
        new_lang = self.current_language.get()
        self.i18n.set_language(new_lang)
        self._update_texts()

    def _update_texts(self):
        """Update all UI texts according to current language."""
        _ = self.i18n

        # Update window title
        self.root.title(f"{_.get('window_title')} v{__version__}")

        # Update tab titles
        self.notebook.tab(0, text=_.get("tab_main"))
        self.notebook.tab(1, text=_.get("tab_api"))
        self.notebook.tab(2, text="Segmente")
        self.notebook.tab(3, text=_.get("tab_transcription"))

        # Update LabelFrame texts
        self.input_frame.config(text=_.get("input"))
        self.output_frame.config(text=_.get("output"))
        self.behavior_frame.config(text=_.get("behavior"))

        # Update all stored widgets
        for key, (trans_key, widget) in self.widgets_to_translate.items():
            try:
                if isinstance(widget, (ttk.Label, ttk.Button, ttk.Checkbutton)):
                    widget.config(text=_.get(trans_key))
                elif isinstance(widget, ttk.LabelFrame):
                    widget.config(text=_.get(trans_key))
            except Exception:
                # Silently ignore if widget no longer exists
                pass


def main():
    """Main entry point for GUI."""
    root = tk.Tk()
    AudioTranscriberGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
