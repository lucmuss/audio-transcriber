"""Main GUI application for Audio Transcriber using PySide6."""

from __future__ import annotations

import sys
import threading
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import QObject, Qt, Signal, Slot
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QMessageBox,
    QStyle,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

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
    DEFAULT_SUMMARY_TEMPERATURE,
    DEFAULT_TEMPERATURE,
    ENV_PREFIX,
    get_model_price_per_minute,
)
from ..env import env_float, env_int, env_str
from ..progress import ProgressTracker
from ..transcriber import AudioTranscriber
from ..utils import find_audio_files, format_duration, setup_logging
from .tabs import (
    create_api_tab,
    create_diarization_tab,
    create_export_tab,
    create_main_tab,
    create_summary_tab,
    create_transcription_tab,
)
from .utils import apply_theme
from .widgets import create_progress_section


@dataclass
class GUIConfig:
    """Serializable configuration snapshot used by the worker thread."""

    input_path: str
    output_dir: str
    segments_dir: str
    api_key: str
    base_url: str
    model: str
    segment_length: int
    overlap: int
    language: str
    detect_language: bool
    temperature: float
    prompt: str
    response_format: str
    concurrency: int
    keep_segments: bool
    skip_existing: bool
    verbose: bool
    enable_diarization: bool
    num_speakers: int
    known_speaker_names: list[str]
    known_speaker_references: list[str]
    summarize: bool
    summary_dir: str
    summary_model: str
    summary_prompt: str
    summary_temperature: float
    export_md: bool
    export_latex: bool
    export_dir: str


class GUISignals(QObject):
    """Cross-thread signal bridge between worker and UI thread."""

    log = Signal(str)
    progress_summary = Signal(object)
    progress_reset = Signal()
    progress_percent = Signal(float)
    dialog = Signal(str, str, str)
    processing_state = Signal(bool)


class AudioTranscriberGUI(QMainWindow):
    """Main GUI application for Audio Transcriber."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setWindowTitle(f"Audio Transcriber v{__version__}")
        self.resize(1120, 860)

        # Defaults from environment
        self.input_path_default = ""
        self.output_dir_default = "./transcriptions"
        self.segments_dir_default = "./segments"

        self.api_key_default = env_str(f"{ENV_PREFIX}API_KEY", "") or ""
        self.base_url_default = env_str(f"{ENV_PREFIX}BASE_URL", DEFAULT_BASE_URL) or ""
        self.model_default = env_str(f"{ENV_PREFIX}MODEL", DEFAULT_MODEL) or ""

        self.segment_length_default = env_int(f"{ENV_PREFIX}SEGMENT_LENGTH", DEFAULT_SEGMENT_LENGTH)
        self.overlap_default = env_int(f"{ENV_PREFIX}OVERLAP", DEFAULT_OVERLAP)

        self.language_default = ""
        self.detect_language_default = True
        self.temperature_default = env_float(f"{ENV_PREFIX}TEMPERATURE", DEFAULT_TEMPERATURE)
        self.prompt_default = env_str(f"{ENV_PREFIX}PROMPT", "") or ""
        self.response_format_default = (
            env_str(f"{ENV_PREFIX}RESPONSE_FORMAT", DEFAULT_RESPONSE_FORMAT) or ""
        )

        self.concurrency_default = env_int(f"{ENV_PREFIX}CONCURRENCY", DEFAULT_CONCURRENCY)

        # Updated defaults to match constants
        self.keep_segments_default = True
        self.skip_existing_default = True
        self.verbose_default = False

        self.enable_diarization_default = False
        self.num_speakers_default = 2
        self.known_speaker_names: list[str] = []
        self.known_speaker_references: list[str] = []

        self.summarize_default = False
        self.summary_dir_default = env_str(f"{ENV_PREFIX}SUMMARY_DIR", "./summaries") or ""
        self.summary_model_default = env_str(f"{ENV_PREFIX}SUMMARY_MODEL", DEFAULT_SUMMARY_MODEL) or ""
        self.summary_prompt_default = (
            env_str(f"{ENV_PREFIX}SUMMARY_PROMPT", DEFAULT_SUMMARY_PROMPT) or ""
        )
        self.summary_temperature_default = env_float(
            f"{ENV_PREFIX}SUMMARY_TEMPERATURE", DEFAULT_SUMMARY_TEMPERATURE
        )

        self.export_dir_default = env_str(f"{ENV_PREFIX}EXPORT_DIR", "./exports") or ""

        # Processing state
        self.is_processing = False
        self.current_thread: threading.Thread | None = None

        # Thread-safe GUI signals
        self.signals = GUISignals(self)
        self.signals.log.connect(self._append_log)
        self.signals.progress_summary.connect(self._apply_progress_summary)
        self.signals.progress_reset.connect(self._reset_progress_ui)
        self.signals.progress_percent.connect(self._set_progress_percent)
        self.signals.dialog.connect(self._show_dialog)
        self.signals.processing_state.connect(self._set_processing_state)

        self._build_ui()

    def _build_ui(self):
        """Create all GUI widgets."""
        central = QWidget(self)
        central.setObjectName("AppCentral")
        self.setCentralWidget(central)

        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(10, 10, 10, 10)
        root_layout.setSpacing(8)

        self.notebook = QTabWidget(central)
        self.notebook.setDocumentMode(True)
        self.notebook.setUsesScrollButtons(True)
        self.notebook.setElideMode(Qt.ElideRight)
        root_layout.addWidget(self.notebook, stretch=3)

        tabs = [
            ("Input/Output", create_main_tab(self), QStyle.SP_DirOpenIcon),
            ("API Config", create_api_tab(self), QStyle.SP_ComputerIcon),
            ("Transcription", create_transcription_tab(self), QStyle.SP_MediaPlay),
            ("Speakers", create_diarization_tab(self), QStyle.SP_FileDialogDetailedView),
            ("Export", create_export_tab(self), QStyle.SP_DialogSaveButton),
            ("Summary", create_summary_tab(self), QStyle.SP_FileDialogInfoView),
        ]
        style = self.style()
        for title, widget, icon_id in tabs:
            self.notebook.addTab(widget, style.standardIcon(icon_id), title)

        (
            progress_widget,
            self.eta_label,
            self.throughput_label,
            self.cost_label,
            self.log_text,
            self.start_button,
            self.stop_button,
        ) = create_progress_section(self)
        root_layout.addWidget(progress_widget, stretch=2)

    def _collect_known_speakers(self) -> tuple[list[str], list[str]]:
        """Read known speakers from list widgets."""
        names: list[str] = []
        refs: list[str] = []

        if hasattr(self, "speaker_names_list"):
            for i in range(self.speaker_names_list.count()):
                names.append(self.speaker_names_list.item(i).text().strip())

        if hasattr(self, "speaker_refs_list"):
            for i in range(self.speaker_refs_list.count()):
                item = self.speaker_refs_list.item(i)
                full_path = item.data(Qt.UserRole)
                refs.append((full_path or item.text()).strip())

        return names, refs

    def _collect_config(self) -> GUIConfig:
        """Collect current UI values into an immutable config snapshot."""
        known_names, known_refs = self._collect_known_speakers()

        return GUIConfig(
            input_path=self.input_path_edit.text().strip(),
            output_dir=self.output_dir_edit.text().strip(),
            segments_dir=self.segments_dir_edit.text().strip(),
            api_key=self.api_key_edit.text().strip(),
            base_url=self.base_url_edit.text().strip(),
            model=self.model_edit.text().strip(),
            segment_length=self.segment_length_spin.value(),
            overlap=self.overlap_spin.value(),
            language=self.language_edit.text().strip(),
            detect_language=self.detect_language_check.isChecked(),
            temperature=float(self.temperature_spin.value()),
            prompt=self.prompt_edit.toPlainText().strip(),
            response_format=self.response_format_combo.currentText().strip(),
            concurrency=self.concurrency_spin.value(),
            keep_segments=self.keep_segments_check.isChecked(),
            skip_existing=self.skip_existing_check.isChecked(),
            verbose=self.verbose_check.isChecked(),
            enable_diarization=self.enable_diarization_check.isChecked(),
            num_speakers=self.num_speakers_spin.value(),
            known_speaker_names=known_names,
            known_speaker_references=known_refs,
            summarize=self.summarize_check.isChecked(),
            summary_dir=self.summary_dir_edit.text().strip(),
            summary_model=self.summary_model_edit.text().strip(),
            summary_prompt=self.summary_prompt_edit.toPlainText().strip(),
            summary_temperature=float(self.summary_temperature_spin.value()),
            export_md=self.export_md_check.isChecked(),
            export_latex=self.export_latex_check.isChecked(),
            export_dir=self.export_dir_edit.text().strip(),
        )

    def validate_inputs(self, config: GUIConfig) -> bool:
        """Validate all inputs before starting."""
        if not config.input_path:
            self._show_dialog("error", "Fehler", "Bitte wählen Sie eine Audio-Datei oder einen Ordner aus.")
            return False

        if not config.api_key:
            self._show_dialog("error", "Fehler", "Bitte geben Sie einen API Key ein.")
            return False

        if not Path(config.input_path).exists():
            self._show_dialog("error", "Fehler", f"Pfad existiert nicht: {config.input_path}")
            return False

        return True

    def log_message(self, message: str):
        """Add message to log output."""
        self.signals.log.emit(message)

    @Slot(str)
    def _append_log(self, message: str):
        self.log_text.appendPlainText(message)
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    @Slot(object)
    def _apply_progress_summary(self, summary: object):
        """Update progress UI with summary dictionary."""
        if not isinstance(summary, dict):
            return

        self.eta_label.setText(f"ETA: {summary['time']['eta_formatted']}")
        self.throughput_label.setText(f"Durchsatz: {summary['throughput']['formatted']}")

        current_cost = float(summary["cost"]["current"])
        total_cost = float(summary["cost"]["total_estimated"])
        self.cost_label.setText(f"Kosten: ${current_cost:.4f} / ${total_cost:.4f}")

    @Slot()
    def _reset_progress_ui(self):
        self.eta_label.setText("ETA: --")
        self.throughput_label.setText("Durchsatz: --")
        self.cost_label.setText("Kosten: $0.0000")

    @Slot(float)
    def _set_progress_percent(self, pct: float):
        # Progress percent slot kept for signal compatibility but does nothing UI-wise
        pass

    @Slot(str, str, str)
    def _show_dialog(self, kind: str, title: str, message: str):
        if kind == "error":
            QMessageBox.critical(self, title, message)
        elif kind == "warning":
            QMessageBox.warning(self, title, message)
        else:
            QMessageBox.information(self, title, message)

    @Slot(bool)
    def _set_processing_state(self, processing: bool):
        self.start_button.setEnabled(not processing)
        self.stop_button.setEnabled(processing)

    def start_transcription(self):
        """Start transcription process."""
        config = self._collect_config()
        if not self.validate_inputs(config):
            return

        if self.is_processing:
            self._show_dialog("warning", "Warnung", "Transkription läuft bereits!")
            return

        setup_logging(config.verbose)

        self.is_processing = True
        self.signals.processing_state.emit(True)

        self.current_thread = threading.Thread(
            target=self.run_transcription, args=(config,), daemon=True
        )
        self.current_thread.start()

    def run_transcription(self, config: GUIConfig):
        """Run transcription in background thread."""
        successful = 0
        failed = 0
        progress: ProgressTracker | None = None

        try:
            self.signals.progress_reset.emit()

            self.log_message("=" * 70)
            self.log_message("Audio Transcriber gestartet")
            self.log_message("=" * 70)

            input_path = Path(config.input_path)
            try:
                audio_files = find_audio_files(input_path)
                self.log_message(f"📁 Gefunden: {len(audio_files)} Audio-Datei(en)")
            except FileNotFoundError as error:
                self.log_message(f"❌ Fehler: {error}")
                self.signals.dialog.emit("error", "Fehler", str(error))
                return

            if not audio_files:
                self.log_message("❌ Keine Audio-Dateien gefunden!")
                self.signals.dialog.emit("warning", "Warnung", "Keine Audio-Dateien gefunden!")
                return

            transcriber = AudioTranscriber(
                api_key=config.api_key,
                base_url=config.base_url,
                model=config.model,
            )

            model_price = get_model_price_per_minute(config.model)
            progress = ProgressTracker(price_per_minute=model_price)
            progress.start()
            progress.set_total_files(len(audio_files))

            self.log_message("\n📊 Analysiere Audio-Dateien...")
            total_duration_seconds = 0.0
            for audio_file in audio_files:
                try:
                    duration = transcriber.segmenter.get_audio_duration(audio_file)
                    total_duration_seconds += duration
                except Exception:
                    pass

            if total_duration_seconds > 0:
                progress.set_total_duration(total_duration_seconds / 60.0)
                self.log_message(f"📁 Gesamtdauer: {format_duration(total_duration_seconds)}")
                self.log_message(f"💰 Geschätzte Kosten: ${progress.stats.total_cost:.4f}\n")
                self.signals.progress_summary.emit(progress.get_summary())

            output_dir = Path(config.output_dir)
            segments_dir = Path(config.segments_dir)

            for index, audio_file in enumerate(audio_files, 1):
                if not self.is_processing:
                    self.log_message("\n⏹ Transkription abgebrochen!")
                    break

                self.log_message(f"\n[{index}/{len(audio_files)}] Verarbeite: {audio_file.name}")

                try:
                    result = transcriber.transcribe_file(
                        file_path=audio_file,
                        output_dir=output_dir,
                        segments_dir=segments_dir,
                        segment_length=config.segment_length,
                        overlap=config.overlap,
                        language=config.language or None,
                        detect_language=config.detect_language,
                        response_format=config.response_format,
                        concurrency=config.concurrency,
                        temperature=config.temperature,
                        prompt=config.prompt or None,
                        keep_segments=config.keep_segments,
                        skip_existing=config.skip_existing,
                        enable_diarization=config.enable_diarization,
                        num_speakers=config.num_speakers if config.enable_diarization else None,
                        known_speaker_names=(
                            config.known_speaker_names if config.enable_diarization else None
                        ),
                        known_speaker_references=(
                            config.known_speaker_references if config.enable_diarization else None
                        ),
                    )

                    if result.get("status") in ("success", "skipped"):
                        if result.get("status") == "success":
                            successful += 1
                            duration_min = result.get("duration_seconds", 0) / 60.0
                            num_segments = result.get("segments", 0)
                            progress.update_file_completed(duration_min, num_segments)
                            self.log_message(f"✅ Erfolgreich: {result['output']}")
                        else:
                            self.log_message(f"⊘ Transkription übersprungen (existiert bereits): {result['output']}")
                            # For progress purposes, treat skipped as completed if it exists
                            successful += 1
                            progress.update_file_skipped()

                        if config.summarize:
                            self.log_message("📝 Erstelle Zusammenfassung...")
                            try:
                                summary_result = transcriber.summarize_transcription(
                                    transcription_file=Path(result["output"]),
                                    summary_dir=Path(config.summary_dir),
                                    summary_model=config.summary_model,
                                    summary_prompt=config.summary_prompt,
                                    summary_temperature=config.summary_temperature,
                                    skip_existing=config.skip_existing,
                                )
                                if summary_result["status"] == "success":
                                    self.log_message(
                                        f"✅ Summary erstellt: {summary_result['summary_file']}"
                                    )
                                elif summary_result["status"] == "skipped":
                                    self.log_message("⊘ Summary übersprungen: bereits vorhanden")
                                else:
                                    self.log_message(
                                        "⚠️ Summary-Fehler: "
                                        f"{summary_result.get('error', 'Unbekannt')}"
                                    )
                            except Exception as error:
                                self.log_message(f"⚠️ Summary-Ausnahme: {error}")

                        if any([config.export_md, config.export_latex]):
                            from ..exporter import TranscriptionExporter

                            self.log_message("📄 Exportiere zu zusätzlichen Formaten...")
                            exporter = TranscriptionExporter()
                            export_dir = Path(config.export_dir)

                            metadata = {
                                "title": audio_file.stem,
                                "date": datetime.now().strftime("%Y-%m-%d"),
                                "duration": format_duration(result.get("duration_seconds", 0)),
                                "language": result.get("language"),
                                "model": config.model,
                            }

                            if config.export_md:
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
                                except Exception as error:
                                    self.log_message(f"  ⚠️  Markdown Export fehlgeschlagen: {error}")

                            if config.export_latex:
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
                                except Exception as error:
                                    self.log_message(f"  ⚠️  LaTeX Export fehlgeschlagen: {error}")

                    elif result.get("status") == "error":
                        failed += 1
                        progress.update_file_failed()
                        self.log_message(f"❌ Fehler: {result.get('error', 'Unbekannt')}")

                    self.signals.progress_summary.emit(progress.get_summary())

                except Exception as error:
                    failed += 1
                    progress.update_file_failed()
                    self.log_message(f"❌ Ausnahme: {error}")
                    self.signals.progress_summary.emit(progress.get_summary())

            self.signals.progress_percent.emit(100.0)

            self.log_message("\n" + "=" * 70)
            self.log_message("ZUSAMMENFASSUNG")
            self.log_message("=" * 70)
            self.log_message(f"✅ Erfolgreich: {successful}")
            self.log_message(f"❌ Fehlgeschlagen: {failed}")

            if progress is not None:
                summary = progress.get_summary()
                self.log_message(f"\n⏱ Vergangene Zeit: {summary['time']['elapsed_formatted']}")
                if summary["throughput"]["value"]:
                    self.log_message(f"📊 Durchsatz: {summary['throughput']['formatted']}")
                self.log_message(f"💰 Endkosten: ${summary['cost']['current']:.4f}")
            self.log_message("=" * 70)

            if failed == 0 and successful > 0:
                self.signals.dialog.emit(
                    "info",
                    "Fertig",
                    (
                        "Transkription abgeschlossen!\n"
                        f"{successful} Datei(en) erfolgreich verarbeitet."
                    ),
                )
            elif failed > 0:
                self.signals.dialog.emit(
                    "warning",
                    "Fertig",
                    f"Transkription abgeschlossen mit {failed} Fehler(n).",
                )

        except Exception as error:
            self.log_message(f"\n❌ Kritischer Fehler: {error}")
            self.signals.dialog.emit("error", "Fehler", f"Kritischer Fehler:\n{error}")

        finally:
            self.is_processing = False
            self.signals.processing_state.emit(False)

    def stop_transcription(self):
        """Stop transcription process."""
        if self.is_processing:
            self.is_processing = False
            self.log_message("\n⏹ Stoppe Transkription...")


def main() -> int:
    """Main entry point for GUI."""
    app = QApplication.instance()
    owns_app = app is None
    if app is None:
        app = QApplication(sys.argv)

    apply_theme(app)
    window = AudioTranscriberGUI()
    window.show()

    if owns_app:
        return app.exec()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
