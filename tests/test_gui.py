"""GUI smoke tests for the PySide6 migration."""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QLineEdit, QPushButton

from audio_transcriber.gui.main import AudioTranscriberGUI
from audio_transcriber.gui.utils import toggle_password_visibility


def _get_app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_gui_initializes_with_expected_tabs():
    _get_app()
    window = AudioTranscriberGUI()

    assert window.windowTitle().startswith("Audio Transcriber v")
    assert window.notebook.count() == 7

    window.close()


def test_toggle_password_visibility_updates_echo_mode_and_label():
    _get_app()
    entry = QLineEdit("secret")
    entry.setEchoMode(QLineEdit.Password)
    button = QPushButton("Show")

    toggle_password_visibility(entry, button)
    assert entry.echoMode() == QLineEdit.Normal
    assert button.text() == "Hide"

    toggle_password_visibility(entry, button)
    assert entry.echoMode() == QLineEdit.Password
    assert button.text() == "Show"
