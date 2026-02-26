"""Main tab for input/output and behavior settings (PySide6)."""

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from ...constants import VALID_RESPONSE_FORMATS


AUDIO_FILTER = "Audio Files (*.mp3 *.wav *.m4a *.flac *.ogg *.aac *.wma *.mp4);;All Files (*)"


def create_main_tab(gui_instance) -> QWidget:
    """Create main settings tab with input/output and behavior options."""
    tab = QWidget()
    layout = QVBoxLayout(tab)
    layout.setContentsMargins(8, 8, 8, 8)
    layout.setSpacing(8)

    input_group = QGroupBox("Input")
    input_layout = QGridLayout(input_group)

    input_layout.addWidget(QLabel("Audio File or Folder:"), 0, 0)

    gui_instance.input_path_edit = QLineEdit(gui_instance.input_path_default)
    gui_instance.input_path_edit.setPlaceholderText("Select an audio file or folder")
    input_layout.addWidget(gui_instance.input_path_edit, 0, 1)

    choose_file_btn = QPushButton("Choose File")
    choose_file_btn.clicked.connect(lambda: browse_file(gui_instance))
    input_layout.addWidget(choose_file_btn, 0, 2)

    choose_folder_btn = QPushButton("Choose Folder")
    choose_folder_btn.clicked.connect(lambda: browse_directory(gui_instance))
    input_layout.addWidget(choose_folder_btn, 0, 3)

    input_layout.setColumnStretch(1, 1)
    layout.addWidget(input_group)

    output_group = QGroupBox("Output")
    output_layout = QGridLayout(output_group)

    output_layout.addWidget(QLabel("Transcription Folder:"), 0, 0)
    gui_instance.output_dir_edit = QLineEdit(gui_instance.output_dir_default)
    output_layout.addWidget(gui_instance.output_dir_edit, 0, 1)

    browse_output_btn = QPushButton("Browse")
    browse_output_btn.clicked.connect(lambda: browse_output(gui_instance))
    output_layout.addWidget(browse_output_btn, 0, 2)

    output_layout.addWidget(QLabel("Segments Folder:"), 1, 0)
    gui_instance.segments_dir_edit = QLineEdit(gui_instance.segments_dir_default)
    output_layout.addWidget(gui_instance.segments_dir_edit, 1, 1)

    browse_segments_btn = QPushButton("Browse")
    browse_segments_btn.clicked.connect(lambda: browse_segments(gui_instance))
    output_layout.addWidget(browse_segments_btn, 1, 2)

    output_layout.addWidget(QLabel("Output Format:"), 2, 0)
    gui_instance.response_format_combo = QComboBox()
    gui_instance.response_format_combo.addItems(sorted(VALID_RESPONSE_FORMATS))
    default_format = gui_instance.response_format_default
    format_index = gui_instance.response_format_combo.findText(default_format)
    if format_index >= 0:
        gui_instance.response_format_combo.setCurrentIndex(format_index)
    output_layout.addWidget(gui_instance.response_format_combo, 2, 1, alignment=Qt.AlignLeft)

    output_layout.setColumnStretch(1, 1)
    layout.addWidget(output_group)

    behavior_group = QGroupBox("Behavior")
    behavior_layout = QVBoxLayout(behavior_group)

    gui_instance.keep_segments_check = QCheckBox("Keep segment files")
    gui_instance.keep_segments_check.setChecked(gui_instance.keep_segments_default)
    behavior_layout.addWidget(gui_instance.keep_segments_check)

    gui_instance.skip_existing_check = QCheckBox("Skip existing files")
    gui_instance.skip_existing_check.setChecked(gui_instance.skip_existing_default)
    behavior_layout.addWidget(gui_instance.skip_existing_check)

    gui_instance.verbose_check = QCheckBox("Verbose logging")
    gui_instance.verbose_check.setChecked(gui_instance.verbose_default)
    behavior_layout.addWidget(gui_instance.verbose_check)

    layout.addWidget(behavior_group)

    advanced_group = QGroupBox("Advanced Settings")
    advanced_layout = QGridLayout(advanced_group)

    advanced_layout.addWidget(QLabel("Segment Length (seconds):"), 0, 0)
    gui_instance.segment_length_spin = QSpinBox()
    gui_instance.segment_length_spin.setRange(60, 1800)
    gui_instance.segment_length_spin.setValue(gui_instance.segment_length_default)
    advanced_layout.addWidget(gui_instance.segment_length_spin, 0, 1, alignment=Qt.AlignLeft)

    advanced_layout.addWidget(QLabel("Overlap (seconds):"), 1, 0)
    gui_instance.overlap_spin = QSpinBox()
    gui_instance.overlap_spin.setRange(0, 60)
    gui_instance.overlap_spin.setValue(gui_instance.overlap_default)
    advanced_layout.addWidget(gui_instance.overlap_spin, 1, 1, alignment=Qt.AlignLeft)

    advanced_layout.addWidget(QLabel("Parallel Transcriptions:"), 2, 0)
    gui_instance.concurrency_spin = QSpinBox()
    gui_instance.concurrency_spin.setRange(1, 16)
    gui_instance.concurrency_spin.setValue(gui_instance.concurrency_default)
    advanced_layout.addWidget(gui_instance.concurrency_spin, 2, 1, alignment=Qt.AlignLeft)

    advanced_layout.setColumnStretch(2, 1)
    layout.addWidget(advanced_group)

    layout.addStretch(1)
    return tab


def browse_file(gui_instance):
    """Browse for audio file."""
    filename, _ = QFileDialog.getOpenFileName(gui_instance, "Select Audio File", "", AUDIO_FILTER)
    if filename:
        gui_instance.input_path_edit.setText(filename)


def browse_directory(gui_instance):
    """Browse for directory."""
    directory = QFileDialog.getExistingDirectory(gui_instance, "Select Folder with Audio Files")
    if directory:
        gui_instance.input_path_edit.setText(directory)


def browse_output(gui_instance):
    """Browse for output directory."""
    current = gui_instance.output_dir_edit.text().strip() or str(Path.cwd())
    directory = QFileDialog.getExistingDirectory(gui_instance, "Select Output Folder", current)
    if directory:
        gui_instance.output_dir_edit.setText(directory)


def browse_segments(gui_instance):
    """Browse for segments directory."""
    current = gui_instance.segments_dir_edit.text().strip() or str(Path.cwd())
    directory = QFileDialog.getExistingDirectory(gui_instance, "Select Segments Folder", current)
    if directory:
        gui_instance.segments_dir_edit.setText(directory)
