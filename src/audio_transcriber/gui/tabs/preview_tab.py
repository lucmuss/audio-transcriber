"""File preview tab (PySide6)."""

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
    QPlainTextEdit,
)

from ...constants import get_model_price_per_minute
from ...utils import find_audio_files, format_duration


def create_preview_tab(gui_instance) -> QWidget:
    """Create file preview tab."""
    tab = QWidget()
    layout = QVBoxLayout(tab)
    layout.setContentsMargins(8, 8, 8, 8)
    layout.setSpacing(8)

    controls = QHBoxLayout()
    analyze_btn = QPushButton("📂 Dateien analysieren")
    analyze_btn.clicked.connect(lambda: analyze_files(gui_instance))
    controls.addWidget(analyze_btn)

    refresh_btn = QPushButton("🔄 Aktualisieren")
    refresh_btn.clicked.connect(lambda: refresh_preview(gui_instance))
    controls.addWidget(refresh_btn)
    controls.addStretch(1)
    layout.addLayout(controls)

    list_group = QGroupBox("Gefundene Dateien")
    list_layout = QVBoxLayout(list_group)

    gui_instance.file_tree = QTreeWidget()
    gui_instance.file_tree.setColumnCount(4)
    gui_instance.file_tree.setHeaderLabels(["Dateiname", "Dauer", "Größe", "Format"])
    gui_instance.file_tree.setAlternatingRowColors(True)
    gui_instance.file_tree.itemSelectionChanged.connect(lambda: on_file_select(gui_instance))
    gui_instance.file_tree.setMinimumHeight(220)
    gui_instance.file_tree.setColumnWidth(0, 330)
    gui_instance.file_tree.setColumnWidth(1, 120)
    gui_instance.file_tree.setColumnWidth(2, 120)
    gui_instance.file_tree.setColumnWidth(3, 100)

    list_layout.addWidget(gui_instance.file_tree)
    layout.addWidget(list_group)

    metadata_group = QGroupBox("Datei-Details")
    metadata_layout = QVBoxLayout(metadata_group)

    gui_instance.metadata_text = QPlainTextEdit()
    gui_instance.metadata_text.setReadOnly(True)
    gui_instance.metadata_text.setMinimumHeight(180)
    metadata_layout.addWidget(gui_instance.metadata_text)

    layout.addWidget(metadata_group)

    stats_group = QGroupBox("Zusammenfassung")
    stats_layout = QVBoxLayout(stats_group)

    gui_instance.stats_label = QLabel("Keine Dateien geladen. Klicken Sie auf 'Dateien analysieren'.")
    gui_instance.stats_label.setStyleSheet("color: #6f7782; font-size: 12px;")
    stats_layout.addWidget(gui_instance.stats_label)

    layout.addWidget(stats_group)
    return tab


def analyze_files(gui_instance):
    """Analyze audio files and display preview."""
    input_path = gui_instance.input_path_edit.text().strip()

    if not input_path:
        QMessageBox.warning(gui_instance, "Warnung", "Bitte wählen Sie zuerst eine Datei oder einen Ordner aus.")
        return

    path = Path(input_path)
    if not path.exists():
        QMessageBox.critical(gui_instance, "Fehler", f"Pfad existiert nicht: {input_path}")
        return

    gui_instance.file_tree.clear()

    try:
        audio_files = find_audio_files(path)

        if not audio_files:
            QMessageBox.warning(gui_instance, "Warnung", "Keine Audio-Dateien gefunden!")
            return

        from pydub import AudioSegment

        total_duration = 0.0
        total_size = 0

        for audio_file in audio_files:
            try:
                file_size = audio_file.stat().st_size
                total_size += file_size
                size_mb = file_size / (1024 * 1024)

                audio = AudioSegment.from_file(str(audio_file))
                duration_seconds = len(audio) / 1000.0
                total_duration += duration_seconds

                item = QTreeWidgetItem(
                    [
                        audio_file.name,
                        format_duration(duration_seconds),
                        f"{size_mb:.1f} MB",
                        audio_file.suffix.upper().replace(".", ""),
                    ]
                )
                item.setData(0, Qt.UserRole, str(audio_file))
                gui_instance.file_tree.addTopLevelItem(item)

            except Exception:
                item = QTreeWidgetItem(
                    [
                        audio_file.name,
                        "Fehler",
                        "--",
                        audio_file.suffix.upper().replace(".", ""),
                    ]
                )
                item.setData(0, Qt.UserRole, str(audio_file))
                gui_instance.file_tree.addTopLevelItem(item)

        total_duration_str = format_duration(total_duration)
        total_size_mb = total_size / (1024 * 1024)
        model_price = get_model_price_per_minute(gui_instance.model_edit.text().strip())
        estimated_cost = (total_duration / 60.0) * model_price

        gui_instance.stats_label.setText(
            f"📁 Dateien: {len(audio_files)} | "
            f"⏱ Gesamtdauer: {total_duration_str} | "
            f"💾 Gesamtgröße: {total_size_mb:.1f} MB | "
            f"💰 Geschätzte Kosten: ${estimated_cost:.4f}"
        )

    except Exception as error:
        QMessageBox.critical(gui_instance, "Fehler", f"Analyse fehlgeschlagen:\n{error}")


def on_file_select(gui_instance):
    """Handle file selection in tree view."""
    items = gui_instance.file_tree.selectedItems()
    if not items:
        return

    file_path_value = items[0].data(0, Qt.UserRole)
    if not file_path_value:
        return

    display_file_metadata(gui_instance, Path(file_path_value))


def display_file_metadata(gui_instance, file_path: Path):
    """Display detailed metadata for selected file."""
    try:
        from pydub import AudioSegment
        from pydub.utils import mediainfo

        audio = AudioSegment.from_file(str(file_path))
        info = mediainfo(str(file_path))

        lines = [
            f"📄 Datei: {file_path.name}",
            f"📂 Pfad: {file_path.parent}",
            "",
            "=== Audio-Informationen ===",
            f"⏱ Dauer: {format_duration(len(audio) / 1000.0)}",
        ]

        channel_desc = (
            "Stereo"
            if audio.channels == 2
            else "Mono" if audio.channels == 1 else f"{audio.channels} Kanäle"
        )
        lines.append(f"🔊 Kanäle: {audio.channels} ({channel_desc})")
        lines.append(f"📊 Sample-Rate: {audio.frame_rate} Hz")
        lines.append(f"🎚 Sample-Width: {audio.sample_width * 8} bit")
        lines.append(f"💾 Dateigröße: {file_path.stat().st_size / (1024 * 1024):.2f} MB")
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

        duration_minutes = len(audio) / 1000.0 / 60.0
        model_price = get_model_price_per_minute(gui_instance.model_edit.text().strip())
        cost = duration_minutes * model_price

        lines.extend(
            [
                "",
                "=== Transkriptions-Schätzung ===",
                f"💰 Geschätzte Kosten: ${cost:.4f}",
                (
                    f"⏱ Geschätzte Dauer: ca. {duration_minutes / 10:.1f} - "
                    f"{duration_minutes / 5:.1f} Minuten"
                ),
                "   (abhängig von Concurrency und Netzwerk)",
            ]
        )

        gui_instance.metadata_text.setPlainText("\n".join(lines))

    except Exception as error:
        gui_instance.metadata_text.setPlainText(f"Fehler beim Laden der Metadaten:\n{error}")


def refresh_preview(gui_instance):
    """Refresh preview with current input path."""
    analyze_files(gui_instance)
