"""Speaker diarization tab (PySide6)."""

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QFileDialog,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)


AUDIO_FILTER = "Audio Files (*.mp3 *.wav *.m4a *.flac *.ogg);;All Files (*)"


def create_diarization_tab(gui_instance) -> QWidget:
    """Create speaker diarization tab."""
    tab = QWidget()
    layout = QVBoxLayout(tab)
    layout.setContentsMargins(8, 8, 8, 8)
    layout.setSpacing(8)

    enable_row = QHBoxLayout()
    gui_instance.enable_diarization_check = QCheckBox(
        "Enable Speaker Diarization (Automatically uses gpt-4o-transcribe-diarize model)"
    )
    gui_instance.enable_diarization_check.setChecked(gui_instance.enable_diarization_default)
    enable_row.addWidget(gui_instance.enable_diarization_check)
    enable_row.addStretch(1)
    layout.addLayout(enable_row)

    settings_group = QGroupBox("Diarization Settings")
    settings_layout = QGridLayout(settings_group)

    settings_layout.addWidget(QLabel("Number of Speakers:"), 0, 0)
    gui_instance.num_speakers_spin = QSpinBox()
    gui_instance.num_speakers_spin.setRange(0, 20)
    gui_instance.num_speakers_spin.setSpecialValueText("Auto")
    gui_instance.num_speakers_spin.setValue(gui_instance.num_speakers_default)
    settings_layout.addWidget(gui_instance.num_speakers_spin, 0, 1, alignment=Qt.AlignLeft)

    speaker_hint = QLabel("(Select 'Auto' for automatic detection)")
    speaker_hint.setStyleSheet("color: #6f7782; font-size: 12px;")
    settings_layout.addWidget(speaker_hint, 0, 2)

    settings_layout.addWidget(QLabel("Known Speaker Names:"), 1, 0, alignment=Qt.AlignTop)
    gui_instance.speaker_names_list = QListWidget()
    gui_instance.speaker_names_list.setMinimumHeight(100)
    settings_layout.addWidget(gui_instance.speaker_names_list, 1, 1, 1, 2)

    names_buttons = QHBoxLayout()
    add_name_btn = QPushButton("Add Name")
    add_name_btn.clicked.connect(lambda: add_speaker_name(gui_instance))
    names_buttons.addWidget(add_name_btn)

    remove_name_btn = QPushButton("Remove Selected")
    remove_name_btn.clicked.connect(lambda: remove_speaker_name(gui_instance))
    names_buttons.addWidget(remove_name_btn)
    names_buttons.addStretch(1)
    settings_layout.addLayout(names_buttons, 2, 1, 1, 2)

    settings_layout.addWidget(QLabel("Reference Audio Files:"), 3, 0, alignment=Qt.AlignTop)
    gui_instance.speaker_refs_list = QListWidget()
    gui_instance.speaker_refs_list.setMinimumHeight(100)
    settings_layout.addWidget(gui_instance.speaker_refs_list, 3, 1, 1, 2)

    refs_buttons = QHBoxLayout()
    add_ref_btn = QPushButton("Add Audio File")
    add_ref_btn.clicked.connect(lambda: add_speaker_reference(gui_instance))
    refs_buttons.addWidget(add_ref_btn)

    remove_ref_btn = QPushButton("Remove Selected")
    remove_ref_btn.clicked.connect(lambda: remove_speaker_reference(gui_instance))
    refs_buttons.addWidget(remove_ref_btn)
    refs_buttons.addStretch(1)
    settings_layout.addLayout(refs_buttons, 4, 1, 1, 2)

    layout.addWidget(settings_group)

    info_group = QGroupBox("Information")
    info_layout = QVBoxLayout(info_group)
    info_label = QLabel(
        """Speaker Diarization identifies different speakers in the audio.

Options:
• Number of Speakers: Expected speaker count (auto-detected if not set)
• Known Speaker Names: List of speaker names to identify
• Reference Audio: Audio samples of known speakers for better identification

Note: Diarization requires specific models and may incur additional costs."""
    )
    info_label.setWordWrap(True)
    info_layout.addWidget(info_label)
    layout.addWidget(info_group)

    layout.addStretch(1)
    return tab


def add_speaker_name(gui_instance):
    """Add a speaker name to the list."""
    name, ok = QInputDialog.getText(gui_instance, "Add Speaker", "Enter speaker name:")
    if ok and name.strip():
        clean = name.strip()
        gui_instance.speaker_names_list.addItem(clean)
        gui_instance.known_speaker_names.append(clean)


def remove_speaker_name(gui_instance):
    """Remove selected speaker name."""
    row = gui_instance.speaker_names_list.currentRow()
    if row >= 0:
        gui_instance.speaker_names_list.takeItem(row)
        if row < len(gui_instance.known_speaker_names):
            gui_instance.known_speaker_names.pop(row)


def add_speaker_reference(gui_instance):
    """Add a reference audio file."""
    filename, _ = QFileDialog.getOpenFileName(gui_instance, "Select Reference Audio", "", AUDIO_FILTER)
    if filename:
        item = QListWidgetItem(Path(filename).name)
        item.setData(Qt.UserRole, filename)
        gui_instance.speaker_refs_list.addItem(item)
        gui_instance.known_speaker_references.append(filename)


def remove_speaker_reference(gui_instance):
    """Remove selected reference audio."""
    row = gui_instance.speaker_refs_list.currentRow()
    if row >= 0:
        gui_instance.speaker_refs_list.takeItem(row)
        if row < len(gui_instance.known_speaker_references):
            gui_instance.known_speaker_references.pop(row)
