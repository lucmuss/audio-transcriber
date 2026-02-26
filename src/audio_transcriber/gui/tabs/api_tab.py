"""API configuration tab (PySide6)."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QFontDatabase
from PySide6.QtWidgets import (
    QGridLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ..utils import toggle_password_visibility


def create_api_tab(gui_instance) -> QWidget:
    """Create API configuration tab."""
    tab = QWidget()
    layout = QVBoxLayout(tab)
    layout.setContentsMargins(8, 8, 8, 8)
    layout.setSpacing(8)

    api_group = QGroupBox("API Settings")
    api_layout = QGridLayout(api_group)

    api_layout.addWidget(QLabel("API Key:"), 0, 0)
    gui_instance.api_key_edit = QLineEdit(gui_instance.api_key_default)
    gui_instance.api_key_edit.setEchoMode(QLineEdit.Password)
    api_layout.addWidget(gui_instance.api_key_edit, 0, 1)

    show_password_btn = QPushButton("Show")
    show_password_btn.clicked.connect(
        lambda: toggle_password_visibility(gui_instance.api_key_edit, show_password_btn)
    )
    api_layout.addWidget(show_password_btn, 0, 2)

    api_layout.addWidget(QLabel("Base URL:"), 1, 0)
    gui_instance.base_url_edit = QLineEdit(gui_instance.base_url_default)
    api_layout.addWidget(gui_instance.base_url_edit, 1, 1, 1, 2)

    api_layout.addWidget(QLabel("Model:"), 2, 0)
    gui_instance.model_edit = QLineEdit(gui_instance.model_default)
    api_layout.addWidget(gui_instance.model_edit, 2, 1, 1, 2)

    api_layout.setColumnStretch(1, 1)
    layout.addWidget(api_group)

    info_group = QGroupBox("Provider Examples")
    info_layout = QVBoxLayout(info_group)

    info_text = QLabel(
        """
OpenAI:
  Base URL: https://api.openai.com/v1
  Models: whisper-1, gpt-4o-transcribe, gpt-4o-mini-transcribe,
          gpt-4o-mini-transcribe-2025-12-15

Groq:
  Base URL: https://api.groq.com/openai/v1
  Model: whisper-large-v3

Ollama (Local):
  Base URL: http://localhost:11434/v1
  API Key: ollama
  Model: whisper

Together.ai:
  Base URL: https://api.together.xyz/v1
  Model: whisper-large-v3
        """.strip()
    )
    info_text.setTextInteractionFlags(Qt.TextSelectableByMouse)
    info_text.setAlignment(Qt.AlignLeft | Qt.AlignTop)
    mono = QFontDatabase.systemFont(QFontDatabase.FixedFont)
    mono.setPointSize(9)
    info_text.setFont(mono)
    info_layout.addWidget(info_text)

    layout.addWidget(info_group)
    layout.addStretch(1)
    return tab
