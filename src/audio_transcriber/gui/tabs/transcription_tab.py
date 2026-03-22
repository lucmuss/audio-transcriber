"""Transcription settings tab (PySide6)."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QDoubleSpinBox,
    QGridLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


def create_transcription_tab(gui_instance) -> QWidget:
    """Create transcription settings tab."""
    tab = QWidget()
    layout = QVBoxLayout(tab)
    layout.setContentsMargins(8, 8, 8, 8)
    layout.setSpacing(8)

    settings_group = QGroupBox("Transcription Settings")
    settings_layout = QGridLayout(settings_group)

    settings_layout.addWidget(QLabel("Language (ISO 639-1):"), 0, 0)
    gui_instance.language_edit = QLineEdit(gui_instance.language_default)
    gui_instance.language_edit.setPlaceholderText("en")
    gui_instance.language_edit.setMaxLength(10)
    gui_instance.language_edit.setMaximumWidth(120)
    settings_layout.addWidget(
        gui_instance.language_edit, 0, 1, alignment=Qt.AlignmentFlag.AlignLeft
    )

    hint = QLabel("(e.g., en, de, fr - leave empty for auto-detect)")
    hint.setStyleSheet("color: #6f7782; font-size: 12px;")
    settings_layout.addWidget(hint, 0, 2)

    gui_instance.detect_language_check = QCheckBox("Auto-detect language")
    gui_instance.detect_language_check.setChecked(gui_instance.detect_language_default)
    settings_layout.addWidget(gui_instance.detect_language_check, 1, 0, 1, 3)

    settings_layout.addWidget(QLabel("Temperature:"), 2, 0)
    gui_instance.temperature_spin = QDoubleSpinBox()
    gui_instance.temperature_spin.setRange(0.0, 1.0)
    gui_instance.temperature_spin.setSingleStep(0.1)
    gui_instance.temperature_spin.setDecimals(2)
    gui_instance.temperature_spin.setValue(0.9)
    settings_layout.addWidget(
        gui_instance.temperature_spin, 2, 1, alignment=Qt.AlignmentFlag.AlignLeft
    )

    settings_layout.addWidget(QLabel("Context Prompt:"), 3, 0, alignment=Qt.AlignmentFlag.AlignTop)
    gui_instance.prompt_edit = QTextEdit()
    gui_instance.prompt_edit.setPlainText(gui_instance.prompt_default)
    gui_instance.prompt_edit.setMinimumHeight(100)
    settings_layout.addWidget(gui_instance.prompt_edit, 3, 1, 1, 2)

    tip = QLabel("Provide context like names, technical terms for better accuracy")
    tip.setStyleSheet("color: #6f7782; font-size: 12px;")
    settings_layout.addWidget(tip, 4, 1, 1, 2)

    settings_layout.setColumnStretch(2, 1)
    layout.addWidget(settings_group)
    layout.addStretch(1)
    return tab
