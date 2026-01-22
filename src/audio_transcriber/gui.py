"""
Graphical User Interface for Audio Transcriber using Tkinter (English-only).
"""

import base64
import os
import threading
import tkinter as tk
import tkinter.simpledialog
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox, scrolledtext, ttk
from typing import Any, Dict, List, Optional, Tuple

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
    get_model_price_per_minute,
)
from .progress import ProgressTracker
from .transcriber import AudioTranscriber
from .utils import find_audio_files, format_duration, setup_logging


class AudioTranscriberGUI:
    """Main GUI application for Audio Transcriber."""

    def __init__(self, root: tk.Tk):
        """Initialize the GUI."""
        self.root = root
        self.root.geometry("1100x950")
        self.root.resizable(True, True)

        # Set window title (English only)
        self.root.title(f"Audio Transcriber v{__version__}")

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

        # Diarization (Speaker Recognition)
        self.enable_diarization = tk.BooleanVar(value=False)
        self.num_speakers = tk.IntVar(value=2)
        self.known_speaker_names: List[str] = []
        self.known_speaker_references: List[str] = []

        # Summarization
        self.summarize = tk.BooleanVar(value=False)
        self.summary_dir = tk.StringVar(value="./summaries")
        self.summary_model = tk.StringVar(value=os.getenv(f"{ENV_PREFIX}SUMMARY_MODEL", DEFAULT_SUMMARY_MODEL))
        self.summary_prompt = tk.StringVar(value=DEFAULT_SUMMARY_PROMPT)

        # Export
        self.export_formats: List[str] = []  # List of selected formats
        self.export_dir = tk.StringVar(value="./exports")
        self.export_title = tk.StringVar(value="")
        self.export_author = tk.StringVar(value="")

        # Processing state
        self.is_processing = False
        self.current_thread: Optional[threading.Thread] = None

        # Build UI
        self.create_widgets()

        # Apply theme
        self.apply_theme()

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
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Tab 1: Main Settings (Input/Output)
        self.main_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.main_frame, text="📁 Input/Output")
        self.create_main_tab(self.main_frame)

        # Tab 2: API Configuration
        self.api_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.api_frame, text="🔌 API Config")
        self.create_api_tab(self.api_frame)

        # Tab 3: Transcription Settings
        self.trans_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.trans_frame, text="🎙️ Transcription")
        self.create_transcription_tab(self.trans_frame)

        # Tab 4: Diarization (Speaker Recognition)
        self.diarization_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.diarization_frame, text="👥 Speakers")
        self.create_diarization_tab(self.diarization_frame)

        # Tab 5: Export Settings
        self.export_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.export_frame, text="📄 Export")
        self.create_export_tab(self.export_frame)

        # Tab 6: Summarization
        self.summary_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.summary_frame, text="📝 Summary")
        self.create_summarization_tab(self.summary_frame)

        # Tab 7: File Preview
        self.preview_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.preview_frame, text="📊 Preview")
        self.create_preview_tab(self.preview_frame)

        # Bottom: Progress and Control
        self.create_bottom_section()

    def create_main_tab(self, parent: ttk.Frame):
        """Create main settings tab."""
        # Input Section
        self.input_frame = ttk.LabelFrame(parent, text="Input", padding=10)
        self.input_frame.pack(fill=tk.X, padx=10, pady=10)

        label1 = ttk.Label(self.input_frame, text="Audio File or Folder:")
        label1.grid(row=0, column=0, sticky=tk.W, pady=5)

        ttk.Entry(self.input_frame, textvariable=self.input_path, width=50).grid(
            row=0, column=1, padx=5, pady=5
        )

        self.choose_file_btn = ttk.Button(
            self.input_frame, text="Choose File", command=self.browse_file
        )
        self.choose_file_btn.grid(row=0, column=2, padx=2)

        self.choose_folder_btn = ttk.Button(
            self.input_frame, text="Choose Folder", command=self.browse_directory
        )
        self.choose_folder_btn.grid(row=0, column=3, padx=2)

        # Output Section
        self.output_frame = ttk.LabelFrame(parent, text="Output", padding=10)
        self.output_frame.pack(fill=tk.X, padx=10, pady=10)

        label2 = ttk.Label(self.output_frame, text="Transcription Folder:")
        label2.grid(row=0, column=0, sticky=tk.W, pady=5)

        ttk.Entry(self.output_frame, textvariable=self.output_dir, width=50).grid(
            row=0, column=1, padx=5, pady=5
        )

        self.browse_output_btn = ttk.Button(
            self.output_frame, text="Browse", command=self.browse_output
        )
        self.browse_output_btn.grid(row=0, column=2, padx=2)

        label3 = ttk.Label(self.output_frame, text="Segments Folder:")
        label3.grid(row=1, column=0, sticky=tk.W, pady=5)

        ttk.Entry(self.output_frame, textvariable=self.segments_dir, width=50).grid(
            row=1, column=1, padx=5, pady=5
        )

        self.browse_segments_btn = ttk.Button(
            self.output_frame, text="Browse", command=self.browse_segments
        )
        self.browse_segments_btn.grid(row=1, column=2, padx=2)

        label4 = ttk.Label(self.output_frame, text="Output Format:")
        label4.grid(row=2, column=0, sticky=tk.W, pady=5)

        format_combo = ttk.Combobox(
            self.output_frame,
            textvariable=self.response_format,
            values=list(VALID_RESPONSE_FORMATS),
            state="readonly",
            width=20,
        )
        format_combo.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)

        # Behavior Options
        self.behavior_frame = ttk.LabelFrame(parent, text="Behavior", padding=10)
        self.behavior_frame.pack(fill=tk.X, padx=10, pady=10)

        self.keep_seg_check = ttk.Checkbutton(
            self.behavior_frame, text="Keep segment files", variable=self.keep_segments
        )
        self.keep_seg_check.grid(row=0, column=0, sticky=tk.W, pady=2)

        self.skip_exist_check = ttk.Checkbutton(
            self.behavior_frame,
            text="Skip existing files",
            variable=self.skip_existing,
        )
        self.skip_exist_check.grid(row=1, column=0, sticky=tk.W, pady=2)

        self.verbose_check = ttk.Checkbutton(
            self.behavior_frame, text="Verbose logging", variable=self.verbose
        )
        self.verbose_check.grid(row=2, column=0, sticky=tk.W, pady=2)

    def create_api_tab(self, parent: ttk.Frame):
        """Create API configuration tab."""
        self.api_settings_frame = ttk.LabelFrame(parent, text="API Settings", padding=10)
        self.api_settings_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # API Key
        api_key_label = ttk.Label(self.api_settings_frame, text="API Key:")
        api_key_label.grid(row=0, column=0, sticky=tk.W, pady=5)
        
        api_entry = ttk.Entry(self.api_settings_frame, textvariable=self.api_key, width=50, show="*")
        api_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

        self.show_password_btn = ttk.Button(
            self.api_settings_frame, text="Show", command=lambda: self.toggle_password(api_entry)
        )
        self.show_password_btn.grid(row=0, column=2, padx=2)

        # Base URL
        base_url_label = ttk.Label(self.api_settings_frame, text="Base URL:")
        base_url_label.grid(row=1, column=0, sticky=tk.W, pady=5)
        
        ttk.Entry(self.api_settings_frame, textvariable=self.base_url, width=50).grid(
            row=1, column=1, padx=5, pady=5, sticky=tk.W
        )

        # Model
        model_label = ttk.Label(self.api_settings_frame, text="Model:")
        model_label.grid(row=2, column=0, sticky=tk.W, pady=5)
        
        ttk.Entry(self.api_settings_frame, textvariable=self.model, width=50).grid(
            row=2, column=1, padx=5, pady=5, sticky=tk.W
        )

        # Info Frame
        self.provider_examples_frame = ttk.LabelFrame(parent, text="Provider Examples", padding=10)
        self.provider_examples_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

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
        self.seg_params_frame = ttk.LabelFrame(parent, text="Segmentation Parameters", padding=10)
        self.seg_params_frame.pack(fill=tk.X, padx=10, pady=10)

        seg_length_label = ttk.Label(self.seg_params_frame, text="Segment Length (seconds):")
        seg_length_label.grid(row=0, column=0, sticky=tk.W, pady=5)
        
        ttk.Spinbox(self.seg_params_frame, from_=60, to=1800, textvariable=self.segment_length, width=10).grid(
            row=0, column=1, padx=5, pady=5, sticky=tk.W
        )

        overlap_label = ttk.Label(self.seg_params_frame, text="Overlap (seconds):")
        overlap_label.grid(row=1, column=0, sticky=tk.W, pady=5)
        
        ttk.Spinbox(self.seg_params_frame, from_=0, to=60, textvariable=self.overlap, width=10).grid(
            row=1, column=1, padx=5, pady=5, sticky=tk.W
        )

        # Performance Frame
        self.perf_frame = ttk.LabelFrame(parent, text="Performance", padding=10)
        self.perf_frame.pack(fill=tk.X, padx=10, pady=10)

        parallel_label = ttk.Label(self.perf_frame, text="Parallel Transcriptions:")
        parallel_label.grid(row=0, column=0, sticky=tk.W, pady=5)
        
        ttk.Spinbox(self.perf_frame, from_=1, to=16, textvariable=self.concurrency, width=10).grid(
            row=0, column=1, padx=5, pady=5, sticky=tk.W
        )

    def create_transcription_tab(self, parent: ttk.Frame):
        """Create transcription settings tab."""
        self.trans_settings_frame = ttk.LabelFrame(parent, text="Transcription Settings", padding=10)
        self.trans_settings_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Language
        lang_iso_label = ttk.Label(self.trans_settings_frame, text="Language (ISO 639-1):")
        lang_iso_label.grid(row=0, column=0, sticky=tk.W, pady=5)
        
        lang_entry = ttk.Entry(self.trans_settings_frame, textvariable=self.language, width=10)
        lang_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        lang_hint_label = ttk.Label(self.trans_settings_frame, text="(e.g., en, de, fr - leave empty for auto-detect)", font=("", 9))
        lang_hint_label.grid(row=0, column=2, sticky=tk.W, padx=5)

        self.auto_detect_check = ttk.Checkbutton(
            self.trans_settings_frame, text="Auto-detect language", variable=self.detect_language
        )
        self.auto_detect_check.grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=2)

        # Temperature
        temp_label = ttk.Label(self.trans_settings_frame, text="Temperature:")
        temp_label.grid(row=2, column=0, sticky=tk.W, pady=5)
        
        ttk.Spinbox(
            self.trans_settings_frame, from_=0.0, to=1.0, increment=0.1, textvariable=self.temperature, width=10
        ).grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)

        # Prompt
        prompt_label = ttk.Label(self.trans_settings_frame, text="Context Prompt:")
        prompt_label.grid(row=3, column=0, sticky=tk.NW, pady=5)
        
        prompt_text = tk.Text(self.trans_settings_frame, width=50, height=4)
        prompt_text.grid(row=3, column=1, columnspan=2, padx=5, pady=5, sticky=tk.W)
        prompt_text.insert("1.0", self.prompt.get())

        # Bind text widget to variable
        def update_prompt(*args):
            self.prompt.set(prompt_text.get("1.0", tk.END).strip())

        prompt_text.bind("<KeyRelease>", update_prompt)

        prompt_tip_label = ttk.Label(
            self.trans_settings_frame,
            text="Provide context like names, technical terms for better accuracy",
            font=("", 9),
        )
        prompt_tip_label.grid(row=4, column=1, columnspan=2, sticky=tk.W, padx=5)

    def create_diarization_tab(self, parent: ttk.Frame):
        """Create speaker diarization tab."""
        # Enable Diarization
        enable_frame = ttk.Frame(parent)
        enable_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Checkbutton(
            enable_frame,
            text="Enable Speaker Diarization (Automatically uses gpt-4o-transcribe-diarize model)",
            variable=self.enable_diarization
        ).pack(anchor=tk.W)
        
        # Diarization Settings Frame
        settings_frame = ttk.LabelFrame(parent, text="Diarization Settings", padding=10)
        settings_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Number of Speakers
        ttk.Label(settings_frame, text="Number of Speakers:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Spinbox(settings_frame, from_=1, to=20, textvariable=self.num_speakers, width=10).grid(
            row=0, column=1, padx=5, pady=5, sticky=tk.W
        )
        ttk.Label(settings_frame, text="(Optional: leave for auto-detection)", font=("", 9)).grid(
            row=0, column=2, sticky=tk.W, padx=5
        )
        
        # Known Speaker Names
        ttk.Label(settings_frame, text="Known Speaker Names:").grid(row=1, column=0, sticky=tk.NW, pady=5)
        
        names_frame = ttk.Frame(settings_frame)
        names_frame.grid(row=1, column=1, columnspan=2, sticky=tk.W, padx=5, pady=5)
        
        self.speaker_names_list = tk.Listbox(names_frame, height=4, width=40)
        self.speaker_names_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        names_scrollbar = ttk.Scrollbar(names_frame, orient=tk.VERTICAL, command=self.speaker_names_list.yview)
        self.speaker_names_list.configure(yscrollcommand=names_scrollbar.set)
        names_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        names_btn_frame = ttk.Frame(settings_frame)
        names_btn_frame.grid(row=2, column=1, columnspan=2, sticky=tk.W, padx=5, pady=5)
        
        ttk.Button(names_btn_frame, text="Add Name", command=self.add_speaker_name).pack(side=tk.LEFT, padx=2)
        ttk.Button(names_btn_frame, text="Remove Selected", command=self.remove_speaker_name).pack(side=tk.LEFT, padx=2)
        
        # Known Speaker References (Audio Files)
        ttk.Label(settings_frame, text="Reference Audio Files:").grid(row=3, column=0, sticky=tk.NW, pady=5)
        
        refs_frame = ttk.Frame(settings_frame)
        refs_frame.grid(row=3, column=1, columnspan=2, sticky=tk.W, padx=5, pady=5)
        
        self.speaker_refs_list = tk.Listbox(refs_frame, height=4, width=40)
        self.speaker_refs_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        refs_scrollbar = ttk.Scrollbar(refs_frame, orient=tk.VERTICAL, command=self.speaker_refs_list.yview)
        self.speaker_refs_list.configure(yscrollcommand=refs_scrollbar.set)
        refs_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        refs_btn_frame = ttk.Frame(settings_frame)
        refs_btn_frame.grid(row=4, column=1, columnspan=2, sticky=tk.W, padx=5, pady=5)
        
        ttk.Button(refs_btn_frame, text="Add Audio File", command=self.add_speaker_reference).pack(side=tk.LEFT, padx=2)
        ttk.Button(refs_btn_frame, text="Remove Selected", command=self.remove_speaker_reference).pack(side=tk.LEFT, padx=2)
        
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
    
    def add_speaker_name(self):
        """Add a speaker name to the list."""
        name = tk.simpledialog.askstring("Add Speaker", "Enter speaker name:")
        if name and name.strip():
            self.speaker_names_list.insert(tk.END, name.strip())
            self.known_speaker_names.append(name.strip())
    
    def remove_speaker_name(self):
        """Remove selected speaker name."""
        selection = self.speaker_names_list.curselection()
        if selection:
            index = selection[0]
            self.speaker_names_list.delete(index)
            if index < len(self.known_speaker_names):
                self.known_speaker_names.pop(index)
    
    def add_speaker_reference(self):
        """Add a reference audio file."""
        filename = filedialog.askopenfilename(
            title="Select Reference Audio",
            filetypes=[("Audio Files", "*.mp3 *.wav *.m4a *.flac *.ogg"), ("All Files", "*.*")]
        )
        if filename:
            self.speaker_refs_list.insert(tk.END, Path(filename).name)
            self.known_speaker_references.append(filename)
    
    def remove_speaker_reference(self):
        """Remove selected reference audio."""
        selection = self.speaker_refs_list.curselection()
        if selection:
            index = selection[0]
            self.speaker_refs_list.delete(index)
            if index < len(self.known_speaker_references):
                self.known_speaker_references.pop(index)

    def create_export_tab(self, parent: ttk.Frame):
        """Create export settings tab."""
        # Export Formats Frame
        formats_frame = ttk.LabelFrame(parent, text="Export Formats", padding=10)
        formats_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(formats_frame, text="Select additional export formats:").pack(anchor=tk.W, pady=(0, 10))
        
        # Checkboxes for each format
        self.export_docx_var = tk.BooleanVar(value=False)
        self.export_md_var = tk.BooleanVar(value=False)
        self.export_latex_var = tk.BooleanVar(value=False)
        
        ttk.Checkbutton(formats_frame, text="DOCX (Microsoft Word)", variable=self.export_docx_var).pack(anchor=tk.W, pady=2)
        ttk.Checkbutton(formats_frame, text="Markdown (.md)", variable=self.export_md_var).pack(anchor=tk.W, pady=2)
        ttk.Checkbutton(formats_frame, text="LaTeX (.tex)", variable=self.export_latex_var).pack(anchor=tk.W, pady=2)
        
        # Export Settings Frame
        settings_frame = ttk.LabelFrame(parent, text="Export Settings", padding=10)
        settings_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Export Directory
        ttk.Label(settings_frame, text="Export Directory:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(settings_frame, textvariable=self.export_dir, width=50).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(settings_frame, text="Browse", command=self.browse_export_dir).grid(row=0, column=2, padx=2)
        
        # Document Title
        ttk.Label(settings_frame, text="Document Title:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(settings_frame, textvariable=self.export_title, width=50).grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        ttk.Label(settings_frame, text="(Optional - uses filename if empty)", font=("", 9)).grid(row=1, column=2, sticky=tk.W, padx=5)
        
        # Document Author
        ttk.Label(settings_frame, text="Author:").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(settings_frame, textvariable=self.export_author, width=50).grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
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
    
    def browse_export_dir(self):
        """Browse for export directory."""
        directory = filedialog.askdirectory(title="Select Export Directory")
        if directory:
            self.export_dir.set(directory)

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

    def create_preview_tab(self, parent: ttk.Frame):
        """Create file preview tab."""
        # Preview Controls
        control_frame = ttk.Frame(parent)
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(
            control_frame,
            text="📂 Dateien analysieren",
            command=self.analyze_files
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            control_frame,
            text="🔄 Aktualisieren",
            command=self.refresh_preview
        ).pack(side=tk.LEFT, padx=5)
        
        # File List Frame
        list_frame = ttk.LabelFrame(parent, text="Gefundene Dateien", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Scrollable file list with Treeview
        columns = ("Datei", "Dauer", "Größe", "Format")
        self.file_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=5)
        
        # Define headings
        self.file_tree.heading("Datei", text="Dateiname")
        self.file_tree.heading("Dauer", text="Dauer")
        self.file_tree.heading("Größe", text="Größe")
        self.file_tree.heading("Format", text="Format")
        
        # Define column widths
        self.file_tree.column("Datei", width=300)
        self.file_tree.column("Dauer", width=100)
        self.file_tree.column("Größe", width=100)
        self.file_tree.column("Format", width=80)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.file_tree.yview)
        self.file_tree.configure(yscrollcommand=scrollbar.set)
        
        self.file_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind selection event
        self.file_tree.bind("<<TreeviewSelect>>", self.on_file_select)
        
        # Metadata Display Frame
        metadata_frame = ttk.LabelFrame(parent, text="Datei-Details", padding=10)
        metadata_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Metadata text area
        self.metadata_text = scrolledtext.ScrolledText(
            metadata_frame, height=6, width=80, state=tk.DISABLED, wrap=tk.WORD
        )
        self.metadata_text.pack(fill=tk.BOTH, expand=True)
        
        # Summary Stats Frame
        stats_frame = ttk.LabelFrame(parent, text="Zusammenfassung", padding=10)
        stats_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.stats_label = ttk.Label(
            stats_frame,
            text="Keine Dateien geladen. Klicken Sie auf 'Dateien analysieren'.",
            font=("", 9)
        )
        self.stats_label.pack(anchor=tk.W)

    def analyze_files(self):
        """Analyze audio files and display preview."""
        input_path = self.input_path.get()
        
        if not input_path:
            messagebox.showwarning("Warnung", "Bitte wählen Sie zuerst eine Datei oder einen Ordner aus.")
            return
        
        if not Path(input_path).exists():
            messagebox.showerror("Fehler", f"Pfad existiert nicht: {input_path}")
            return
        
        # Clear existing items
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)
        
        try:
            # Find audio files
            audio_files = find_audio_files(input_path)
            
            if not audio_files:
                messagebox.showwarning("Warnung", "Keine Audio-Dateien gefunden!")
                return
            
            # Create a temporary transcriber just for metadata
            from pydub import AudioSegment
            
            total_duration = 0.0
            total_size = 0
            
            for audio_file in audio_files:
                try:
                    # Get file size
                    file_size = audio_file.stat().st_size
                    total_size += file_size
                    size_mb = file_size / (1024 * 1024)
                    
                    # Get audio duration using pydub
                    audio = AudioSegment.from_file(str(audio_file))
                    duration_seconds = len(audio) / 1000.0  # pydub uses milliseconds
                    total_duration += duration_seconds
                    
                    # Format values
                    duration_str = format_duration(duration_seconds)
                    size_str = f"{size_mb:.1f} MB"
                    format_str = audio_file.suffix.upper().replace(".", "")
                    
                    # Add to tree
                    self.file_tree.insert(
                        "",
                        tk.END,
                        values=(audio_file.name, duration_str, size_str, format_str),
                        tags=(str(audio_file),)  # Store full path in tags
                    )
                    
                except Exception as e:
                    # If error, still add file but with error info
                    self.file_tree.insert(
                        "",
                        tk.END,
                        values=(audio_file.name, "Fehler", "--", audio_file.suffix.upper().replace(".", "")),
                        tags=(str(audio_file),)
                    )
            
            # Update summary stats
            total_duration_str = format_duration(total_duration)
            total_size_mb = total_size / (1024 * 1024)
            model_price = get_model_price_per_minute(self.model.get())
            estimated_cost = (total_duration / 60.0) * model_price
            
            stats_text = (
                f"📁 Dateien: {len(audio_files)} | "
                f"⏱ Gesamtdauer: {total_duration_str} | "
                f"💾 Gesamtgröße: {total_size_mb:.1f} MB | "
                f"💰 Geschätzte Kosten:  ${estimated_cost:.4f}"
            )
            self.stats_label.config(text=stats_text)
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Analyse fehlgeschlagen:\n{e}")

    def on_file_select(self, event):
        """Handle file selection in tree view."""
        selection = self.file_tree.selection()
        if not selection:
            return
        
        # Get selected item
        item = selection[0]
        tags = self.file_tree.item(item, "tags")
        
        if not tags:
            return
        
        file_path = Path(tags[0])
        
        # Display detailed metadata
        self.display_file_metadata(file_path)

    def display_file_metadata(self, file_path: Path):
        """Display detailed metadata for selected file."""
        self.metadata_text.config(state=tk.NORMAL)
        self.metadata_text.delete("1.0", tk.END)
        
        try:
            from pydub import AudioSegment
            from pydub.utils import mediainfo
            
            # Load audio file
            audio = AudioSegment.from_file(str(file_path))
            info = mediainfo(str(file_path))
            
            # Format metadata
            lines = []
            lines.append(f"📄 Datei: {file_path.name}")
            lines.append(f"📂 Pfad: {file_path.parent}")
            lines.append("")
            lines.append("=== Audio-Informationen ===")
            lines.append(f"⏱ Dauer: {format_duration(len(audio) / 1000.0)}")
            lines.append(f"🔊 Kanäle: {audio.channels} ({'Stereo' if audio.channels == 2 else 'Mono' if audio.channels == 1 else f'{audio.channels} Kanäle'})")
            lines.append(f"📊 Sample-Rate: {audio.frame_rate} Hz")
            lines.append(f"🎚 Sample-Width: {audio.sample_width * 8} bit")
            lines.append(f"💾 Dateigröße: {file_path.stat().st_size / (1024*1024):.2f} MB")
            lines.append(f"📦 Format: {file_path.suffix.upper().replace('.', '')}")
            
            if info:
                lines.append("")
                lines.append("=== Erweiterte Metadaten ===")
                
                if "bit_rate" in info:
                    bitrate_kbps = int(info["bit_rate"]) / 1000
                    lines.append(f"📈 Bitrate: {bitrate_kbps:.0f} kbps")
                
                if "codec_name" in info:
                    lines.append(f"🔧 Codec: {info['codec_name']}")
                
                if "duration" in info:
                    lines.append(f"⏱ Präzise Dauer: {float(info['duration']):.2f}s")
            
            # Calculate estimated cost
            duration_minutes = len(audio) / 1000.0 / 60.0
            model_price = get_model_price_per_minute(self.model.get())
            cost = duration_minutes * model_price
            
            lines.append("")
            lines.append("=== Transkriptions-Schätzung ===")
            lines.append(f"💰 Geschätzte Kosten: ${cost:.4f}")
            lines.append(f"⏱ Geschätzte Dauer: ca. {duration_minutes / 10:.1f} - {duration_minutes / 5:.1f} Minuten")
            lines.append(f"   (abhängig von Concurrency und Netzwerk)")
            
            self.metadata_text.insert("1.0", "\n".join(lines))
            
        except Exception as e:
            self.metadata_text.insert("1.0", f"Fehler beim Laden der Metadaten:\n{e}")
        
        self.metadata_text.config(state=tk.DISABLED)

    def refresh_preview(self):
        """Refresh preview with current input path."""
        self.analyze_files()

    def create_bottom_section(self):
        """Create bottom section with progress and control buttons."""
        bottom_frame = ttk.Frame(self.root)
        bottom_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Progress Section
        self.progress_frame = ttk.LabelFrame(bottom_frame, text="Progress", padding=10)
        self.progress_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Progress bar with percentage
        progress_bar_frame = ttk.Frame(self.progress_frame)
        progress_bar_frame.pack(fill=tk.X, pady=(0, 10))

        self.progress_bar = ttk.Progressbar(
            progress_bar_frame, orient="horizontal", length=400, mode="determinate"
        )
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        self.progress_label = ttk.Label(progress_bar_frame, text="0%", width=10)
        self.progress_label.pack(side=tk.LEFT)

        # Stats frame for ETA, throughput, cost
        stats_frame = ttk.Frame(self.progress_frame)
        stats_frame.pack(fill=tk.X, pady=(0, 10))

        self.eta_label = ttk.Label(stats_frame, text="ETA: --", font=("", 9))
        self.eta_label.pack(side=tk.LEFT, padx=(0, 20))

        self.throughput_label = ttk.Label(stats_frame, text="Durchsatz: --", font=("", 9))
        self.throughput_label.pack(side=tk.LEFT, padx=(0, 20))

        self.cost_label = ttk.Label(stats_frame, text="Kosten: $0.0000", font=("", 9))
        self.cost_label.pack(side=tk.LEFT)

        # Log output
        self.log_text = scrolledtext.ScrolledText(
            self.progress_frame, height=5, width=80, state=tk.DISABLED, wrap=tk.WORD
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # Control Buttons
        button_frame = ttk.Frame(bottom_frame)
        button_frame.pack(fill=tk.X)

        self.start_button = ttk.Button(
            button_frame,
            text="Start Transcription",
            command=self.start_transcription,
            style="Accent.TButton",
        )
        self.start_button.pack(side=tk.LEFT, padx=5)

        self.stop_button = ttk.Button(
            button_frame, text="Stop", command=self.stop_transcription, state=tk.DISABLED
        )
        self.stop_button.pack(side=tk.LEFT, padx=5)

        self.clear_log_button = ttk.Button(button_frame, text="Clear Log", command=self.clear_log)
        self.clear_log_button.pack(side=tk.LEFT, padx=5)

        self.quit_button = ttk.Button(button_frame, text="Quit", command=self.root.quit)
        self.quit_button.pack(side=tk.RIGHT, padx=5)

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

    def update_progress_ui(self, progress_tracker: ProgressTracker):
        """Update progress UI elements with current progress."""
        summary = progress_tracker.get_summary()
        
        # Update progress bar and percentage
        progress_pct = summary["files"]["progress_pct"]
        self.progress_bar["value"] = progress_pct
        self.progress_label.config(text=f"{progress_pct:.1f}%")
        
        # Update ETA
        eta_str = summary["time"]["eta_formatted"]
        self.eta_label.config(text=f"ETA: {eta_str}")
        
        # Update throughput
        throughput_str = summary["throughput"]["formatted"]
        self.throughput_label.config(text=f"Durchsatz: {throughput_str}")
        
        # Update cost
        current_cost = summary["cost"]["current"]
        total_cost = summary["cost"]["total_estimated"]
        self.cost_label.config(text=f"Kosten: ${current_cost:.4f} / ${total_cost:.4f}")
        
        # Force UI update
        self.root.update_idletasks()

    def run_transcription(self):
        """Run transcription in background thread."""
        try:
            # Reset progress UI
            self.progress_bar["value"] = 0
            self.progress_label.config(text="0%")
            self.eta_label.config(text="ETA: --")
            self.throughput_label.config(text="Durchsatz: --")
            self.cost_label.config(text="Kosten: $0.0000")
            
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

            # Initialize progress tracker with model-specific pricing
            model_price = get_model_price_per_minute(self.model.get())
            progress = ProgressTracker(price_per_minute=model_price)
            progress.start()
            progress.set_total_files(len(audio_files))

            # Calculate total duration for better ETA
            self.log_message("\n📊 Analysiere Audio-Dateien...")
            total_duration_seconds = 0.0
            for audio_file in audio_files:
                try:
                    duration = transcriber.segmenter.get_audio_duration(audio_file)
                    total_duration_seconds += duration
                except Exception:
                    pass  # Skip if duration cannot be determined

            if total_duration_seconds > 0:
                progress.set_total_duration(total_duration_seconds / 60.0)
                self.log_message(f"📁 Gesamtdauer: {format_duration(total_duration_seconds)}")
                self.log_message(f"💰 Geschätzte Kosten: ${progress.stats.total_cost:.4f}\n")
                self.update_progress_ui(progress)

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
                        enable_diarization=self.enable_diarization.get(),
                        num_speakers=self.num_speakers.get() if self.enable_diarization.get() else None,
                        known_speaker_names=self.known_speaker_names if self.enable_diarization.get() else None,
                        known_speaker_references=self.known_speaker_references if self.enable_diarization.get() else None,
                    )

                    # Update progress tracker
                    if result.get("status") == "success":
                        successful += 1
                        duration_min = result.get("duration_seconds", 0) / 60.0
                        num_segments = result.get("segments", 0)
                        progress.update_file_completed(duration_min, num_segments)
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
                        
                        # Export to additional formats if requested
                        if any([self.export_docx_var.get(), self.export_md_var.get(), self.export_latex_var.get()]):
                            from .exporter import TranscriptionExporter
                            
                            self.log_message("📄 Exportiere zu zusätzlichen Formaten...")
                            exporter = TranscriptionExporter()
                            export_dir = Path(self.export_dir.get())
                            
                            # Prepare metadata
                            metadata = {
                                "title": self.export_title.get() or audio_file.stem,
                                "author": self.export_author.get(),
                                "date": datetime.now().strftime("%Y-%m-%d"),
                                "duration": format_duration(result.get("duration_seconds", 0)),
                                "language": result.get("language"),
                                "model": self.model.get(),
                            }
                            
                            # Export DOCX
                            if self.export_docx_var.get():
                                try:
                                    export_file = export_dir / f"{audio_file.stem}.docx"
                                    export_result = exporter.export(
                                        transcription_file=Path(result["output"]),
                                        output_file=export_file,
                                        export_format="docx",
                                        metadata=metadata,
                                    )
                                    if export_result.get("status") == "success":
                                        self.log_message(f"  ✅ DOCX: {export_file.name}")
                                except Exception as e:
                                    self.log_message(f"  ⚠️  DOCX Export fehlgeschlagen: {e}")
                            
                            # Export Markdown
                            if self.export_md_var.get():
                                try:
                                    export_file = export_dir / f"{audio_file.stem}.md"
                                    export_result = exporter.export(
                                        transcription_file=Path(result["output"]),
                                        output_file=export_file,
                                        export_format="md",
                                        metadata=metadata,
                                    )
                                    if export_result.get("status") == "success":
                                        self.log_message(f"  ✅ Markdown: {export_file.name}")
                                except Exception as e:
                                    self.log_message(f"  ⚠️  Markdown Export fehlgeschlagen: {e}")
                            
                            # Export LaTeX
                            if self.export_latex_var.get():
                                try:
                                    export_file = export_dir / f"{audio_file.stem}.tex"
                                    export_result = exporter.export(
                                        transcription_file=Path(result["output"]),
                                        output_file=export_file,
                                        export_format="latex",
                                        metadata=metadata,
                                    )
                                    if export_result.get("status") == "success":
                                        self.log_message(f"  ✅ LaTeX: {export_file.name}")
                                except Exception as e:
                                    self.log_message(f"  ⚠️  LaTeX Export fehlgeschlagen: {e}")
                                
                    elif result.get("status") == "error":
                        failed += 1
                        progress.update_file_failed()
                        self.log_message(f"❌ Fehler: {result.get('error', 'Unbekannt')}")
                    elif result.get("status") == "skipped":
                        progress.update_file_skipped()
                        self.log_message("⊘ Übersprungen: bereits vorhanden")

                    # Update progress UI in real-time
                    self.update_progress_ui(progress)

                except Exception as e:
                    failed += 1
                    progress.update_file_failed()
                    self.log_message(f"❌ Ausnahme: {e}")
                    self.update_progress_ui(progress)

            # Final progress update
            self.progress_bar["value"] = 100
            self.progress_label.config(text="100%")

            # Summary
            self.log_message("\n" + "=" * 70)
            self.log_message("ZUSAMMENFASSUNG")
            self.log_message("=" * 70)
            self.log_message(f"✅ Erfolgreich: {successful}")
            self.log_message(f"❌ Fehlgeschlagen: {failed}")
            
            # Print detailed progress summary
            summary = progress.get_summary()
            self.log_message(f"\n⏱ Vergangene Zeit: {summary['time']['elapsed_formatted']}")
            if summary['throughput']['value']:
                self.log_message(f"📊 Durchsatz: {summary['throughput']['formatted']}")
            self.log_message(f"💰 Endkosten: ${summary['cost']['current']:.4f}")
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




def main():
    """Main entry point for GUI."""
    root = tk.Tk()
    AudioTranscriberGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
