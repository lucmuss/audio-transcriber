"""
Main GUI application for Audio Transcriber.
"""

import os
import threading
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import messagebox, ttk
from typing import List, Optional

from .. import __version__
from ..constants import (
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
    get_model_price_per_minute,
)
from ..progress import ProgressTracker
from ..transcriber import AudioTranscriber
from ..utils import find_audio_files, format_duration, setup_logging
from .tabs import (
    create_api_tab,
    create_diarization_tab,
    create_export_tab,
    create_main_tab,
    create_preview_tab,
    create_summary_tab,
    create_transcription_tab,
)
from .utils import apply_theme
from .widgets import create_progress_section


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

        # Behavior - UPDATED DEFAULTS to match constants
        self.keep_segments = tk.BooleanVar(value=True)  # Changed from False to True
        self.skip_existing = tk.BooleanVar(value=False)  # Changed from True to False
        self.verbose = tk.BooleanVar(value=False)

        # Diarization (Speaker Recognition)
        self.enable_diarization = tk.BooleanVar(value=False)
        self.num_speakers = tk.IntVar(value=2)
        self.known_speaker_names: List[str] = []
        self.known_speaker_references: List[str] = []

        # Summarization
        self.summarize = tk.BooleanVar(value=False)
        self.summary_dir = tk.StringVar(value="./summaries")
        self.summary_model = tk.StringVar(
            value=os.getenv(f"{ENV_PREFIX}SUMMARY_MODEL", DEFAULT_SUMMARY_MODEL)
        )
        self.summary_prompt = tk.StringVar(value=DEFAULT_SUMMARY_PROMPT)

        # Export
        self.export_formats: List[str] = []  # List of selected formats
        self.export_dir = tk.StringVar(value="./exports")
        self.export_title = tk.StringVar(value="")
        self.export_author = tk.StringVar(value="")
        # Export format checkboxes (will be set by create_export_tab)
        self.export_docx_var = tk.BooleanVar(value=False)
        self.export_md_var = tk.BooleanVar(value=False)
        self.export_latex_var = tk.BooleanVar(value=False)

        # Processing state
        self.is_processing = False
        self.current_thread: Optional[threading.Thread] = None

        # Build UI
        self.create_widgets()

        # Apply theme
        apply_theme(self.root)

    def create_widgets(self):
        """Create all GUI widgets."""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Tab 1: Main Settings (Input/Output)
        main_frame = ttk.Frame(self.notebook)
        self.notebook.add(main_frame, text="📁 Input/Output")
        create_main_tab(main_frame, self)

        # Tab 2: API Configuration
        api_frame = ttk.Frame(self.notebook)
        self.notebook.add(api_frame, text="🔌 API Config")
        create_api_tab(api_frame, self)

        # Tab 3: Transcription Settings
        trans_frame = ttk.Frame(self.notebook)
        self.notebook.add(trans_frame, text="🎙️ Transcription")
        create_transcription_tab(trans_frame, self)

        # Tab 4: Diarization (Speaker Recognition)
        diarization_frame = ttk.Frame(self.notebook)
        self.notebook.add(diarization_frame, text="👥 Speakers")
        create_diarization_tab(diarization_frame, self)

        # Tab 5: Export Settings
        export_frame = ttk.Frame(self.notebook)
        self.notebook.add(export_frame, text="📄 Export")
        create_export_tab(export_frame, self)

        # Tab 6: Summarization
        summary_frame = ttk.Frame(self.notebook)
        self.notebook.add(summary_frame, text="📝 Summary")
        create_summary_tab(summary_frame, self)

        # Tab 7: File Preview
        preview_frame = ttk.Frame(self.notebook)
        self.notebook.add(preview_frame, text="📊 Preview")
        create_preview_tab(preview_frame, self)

        # Bottom: Progress and Control
        result = create_progress_section(self.root, self)
        (
            self.progress_bar,
            self.progress_label,
            self.eta_label,
            self.throughput_label,
            self.cost_label,
            self.log_text,
            self.start_button,
            self.stop_button,
        ) = result

    def log_message(self, message: str):
        """Add message to log output."""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.root.update()

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
                        num_speakers=(
                            self.num_speakers.get() if self.enable_diarization.get() else None
                        ),
                        known_speaker_names=(
                            self.known_speaker_names if self.enable_diarization.get() else None
                        ),
                        known_speaker_references=(
                            self.known_speaker_references if self.enable_diarization.get() else None
                        ),
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
                                    self.log_message(
                                        f"✅ Summary erstellt: {summary_result['summary_file']}"
                                    )
                                elif summary_result["status"] == "skipped":
                                    self.log_message("⊘ Summary übersprungen: bereits vorhanden")
                                else:
                                    self.log_message(
                                        f"⚠️ Summary-Fehler: {summary_result.get('error', 'Unbekannt')}"
                                    )
                            except Exception as e:
                                self.log_message(f"⚠️ Summary-Ausnahme: {e}")

                        # Export to additional formats if requested
                        if any(
                            [
                                self.export_docx_var.get(),
                                self.export_md_var.get(),
                                self.export_latex_var.get(),
                            ]
                        ):
                            from ..exporter import TranscriptionExporter

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
            if summary["throughput"]["value"]:
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
