"""
File preview tab.
"""

import tkinter as tk
from pathlib import Path
from tkinter import messagebox, scrolledtext, ttk

from ...constants import get_model_price_per_minute
from ...utils import find_audio_files, format_duration


def create_preview_tab(parent: ttk.Frame, gui_instance):
    """Create file preview tab."""
    # Preview Controls
    control_frame = ttk.Frame(parent)
    control_frame.pack(fill=tk.X, padx=10, pady=10)

    ttk.Button(
        control_frame,
        text="📂 Dateien analysieren",
        command=lambda: analyze_files(gui_instance)
    ).pack(side=tk.LEFT, padx=5)

    ttk.Button(
        control_frame,
        text="🔄 Aktualisieren",
        command=lambda: refresh_preview(gui_instance)
    ).pack(side=tk.LEFT, padx=5)

    # File List Frame
    list_frame = ttk.LabelFrame(parent, text="Gefundene Dateien", padding=10)
    list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Scrollable file list with Treeview
    columns = ("Datei", "Dauer", "Größe", "Format")
    gui_instance.file_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=5)

    # Define headings
    gui_instance.file_tree.heading("Datei", text="Dateiname")
    gui_instance.file_tree.heading("Dauer", text="Dauer")
    gui_instance.file_tree.heading("Größe", text="Größe")
    gui_instance.file_tree.heading("Format", text="Format")

    # Define column widths
    gui_instance.file_tree.column("Datei", width=300)
    gui_instance.file_tree.column("Dauer", width=100)
    gui_instance.file_tree.column("Größe", width=100)
    gui_instance.file_tree.column("Format", width=80)

    # Add scrollbar
    scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=gui_instance.file_tree.yview)
    gui_instance.file_tree.configure(yscrollcommand=scrollbar.set)

    gui_instance.file_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # Bind selection event
    gui_instance.file_tree.bind("<<TreeviewSelect>>", lambda e: on_file_select(gui_instance))

    # Metadata Display Frame
    metadata_frame = ttk.LabelFrame(parent, text="Datei-Details", padding=10)
    metadata_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Metadata text area
    gui_instance.metadata_text = scrolledtext.ScrolledText(
        metadata_frame, height=6, width=80, state=tk.DISABLED, wrap=tk.WORD
    )
    gui_instance.metadata_text.pack(fill=tk.BOTH, expand=True)

    # Summary Stats Frame
    stats_frame = ttk.LabelFrame(parent, text="Zusammenfassung", padding=10)
    stats_frame.pack(fill=tk.X, padx=10, pady=10)

    gui_instance.stats_label = ttk.Label(
        stats_frame,
        text="Keine Dateien geladen. Klicken Sie auf 'Dateien analysieren'.",
        font=("", 9)
    )
    gui_instance.stats_label.pack(anchor=tk.W)


def analyze_files(gui_instance):
    """Analyze audio files and display preview."""
    input_path = gui_instance.input_path.get()

    if not input_path:
        messagebox.showwarning("Warnung", "Bitte wählen Sie zuerst eine Datei oder einen Ordner aus.")
        return

    if not Path(input_path).exists():
        messagebox.showerror("Fehler", f"Pfad existiert nicht: {input_path}")
        return

    # Clear existing items
    for item in gui_instance.file_tree.get_children():
        gui_instance.file_tree.delete(item)

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
                gui_instance.file_tree.insert(
                    "",
                    tk.END,
                    values=(audio_file.name, duration_str, size_str, format_str),
                    tags=(str(audio_file),)  # Store full path in tags
                )

            except Exception as e:
                # If error, still add file but with error info
                gui_instance.file_tree.insert(
                    "",
                    tk.END,
                    values=(audio_file.name, "Fehler", "--", audio_file.suffix.upper().replace(".", "")),
                    tags=(str(audio_file),)
                )

        # Update summary stats
        total_duration_str = format_duration(total_duration)
        total_size_mb = total_size / (1024 * 1024)
        model_price = get_model_price_per_minute(gui_instance.model.get())
        estimated_cost = (total_duration / 60.0) * model_price

        stats_text = (
            f"📁 Dateien: {len(audio_files)} | "
            f"⏱ Gesamtdauer: {total_duration_str} | "
            f"💾 Gesamtgröße: {total_size_mb:.1f} MB | "
            f"💰 Geschätzte Kosten:  ${estimated_cost:.4f}"
        )
        gui_instance.stats_label.config(text=stats_text)

    except Exception as e:
        messagebox.showerror("Fehler", f"Analyse fehlgeschlagen:\n{e}")


def on_file_select(gui_instance):
    """Handle file selection in tree view."""
    selection = gui_instance.file_tree.selection()
    if not selection:
        return

    # Get selected item
    item = selection[0]
    tags = gui_instance.file_tree.item(item, "tags")

    if not tags:
        return

    file_path = Path(tags[0])

    # Display detailed metadata
    display_file_metadata(gui_instance, file_path)


def display_file_metadata(gui_instance, file_path: Path):
    """Display detailed metadata for selected file."""
    gui_instance.metadata_text.config(state=tk.NORMAL)
    gui_instance.metadata_text.delete("1.0", tk.END)

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
        model_price = get_model_price_per_minute(gui_instance.model.get())
        cost = duration_minutes * model_price

        lines.append("")
        lines.append("=== Transkriptions-Schätzung ===")
        lines.append(f"💰 Geschätzte Kosten: ${cost:.4f}")
        lines.append(f"⏱ Geschätzte Dauer: ca. {duration_minutes / 10:.1f} - {duration_minutes / 5:.1f} Minuten")
        lines.append(f"   (abhängig von Concurrency und Netzwerk)")

        gui_instance.metadata_text.insert("1.0", "\n".join(lines))

    except Exception as e:
        gui_instance.metadata_text.insert("1.0", f"Fehler beim Laden der Metadaten:\n{e}")

    gui_instance.metadata_text.config(state=tk.DISABLED)


def refresh_preview(gui_instance):
    """Refresh preview with current input path."""
    analyze_files(gui_instance)
