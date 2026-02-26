"""Summarization settings tab (PySide6)."""

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QFileDialog,
    QGridLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


def create_summary_tab(gui_instance) -> QWidget:
    """Create summarization settings tab."""
    tab = QWidget()
    layout = QVBoxLayout(tab)
    layout.setContentsMargins(8, 8, 8, 8)
    layout.setSpacing(8)

    gui_instance.summarize_check = QCheckBox("Create summary")
    gui_instance.summarize_check.setChecked(gui_instance.summarize_default)
    layout.addWidget(gui_instance.summarize_check, alignment=Qt.AlignLeft)

    settings_group = QGroupBox("Summarization Settings")
    settings_layout = QGridLayout(settings_group)

    settings_layout.addWidget(QLabel("Summary Directory:"), 0, 0)
    gui_instance.summary_dir_edit = QLineEdit(gui_instance.summary_dir_default)
    settings_layout.addWidget(gui_instance.summary_dir_edit, 0, 1)

    browse_summary_btn = QPushButton("Browse")
    browse_summary_btn.clicked.connect(lambda: browse_summary_dir(gui_instance))
    settings_layout.addWidget(browse_summary_btn, 0, 2)

    settings_layout.addWidget(QLabel("Summary Model:"), 1, 0)
    gui_instance.summary_model_edit = QLineEdit(gui_instance.summary_model_default)
    settings_layout.addWidget(gui_instance.summary_model_edit, 1, 1)

    model_hint = QLabel("(e.g., gpt-4o-mini, gpt-4, gpt-3.5-turbo)")
    model_hint.setStyleSheet("color: #6f7782; font-size: 12px;")
    settings_layout.addWidget(model_hint, 1, 2)

    settings_layout.addWidget(QLabel("Summary-Prompt:"), 2, 0, alignment=Qt.AlignTop)
    gui_instance.summary_prompt_edit = QTextEdit()
    gui_instance.summary_prompt_edit.setPlainText(gui_instance.summary_prompt_default)
    gui_instance.summary_prompt_edit.setMinimumHeight(120)
    settings_layout.addWidget(gui_instance.summary_prompt_edit, 2, 1, 1, 2)

    summary_hint = QLabel("Describe how the summary should be generated (Markdown is used by default)")
    summary_hint.setStyleSheet("color: #6f7782; font-size: 12px;")
    settings_layout.addWidget(summary_hint, 3, 1, 1, 2)

    settings_layout.setColumnStretch(1, 1)
    layout.addWidget(settings_group)

    info_group = QGroupBox("Information")
    info_layout = QVBoxLayout(info_group)
    info_label = QLabel(
        """The summarization feature uses an LLM (Large Language Model) 
to automatically create a concise summary of the transcription.

The summary is saved in the specified summary directory.

Note: This incurs additional API costs based on the 
length of the transcription and the chosen model."""
    )
    info_label.setWordWrap(True)
    info_layout.addWidget(info_label)

    layout.addWidget(info_group)
    layout.addStretch(1)
    return tab


def browse_summary_dir(gui_instance):
    """Browse for summary directory."""
    current = gui_instance.summary_dir_edit.text().strip() or str(Path.cwd())
    directory = QFileDialog.getExistingDirectory(gui_instance, "Select Summary Directory", current)
    if directory:
        gui_instance.summary_dir_edit.setText(directory)
