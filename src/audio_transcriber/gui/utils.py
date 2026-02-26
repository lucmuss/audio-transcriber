"""Utility functions for the PySide6 GUI."""

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication, QLineEdit, QPushButton


def apply_theme(app: QApplication):
    """Apply a modern, higher-contrast theme to the GUI."""
    app.setStyle("Fusion")
    app.setFont(QFont("IBM Plex Sans", 10))
    app.setStyleSheet(
        """
        QMainWindow, QWidget#AppCentral {
            background: qlineargradient(
                x1: 0, y1: 0, x2: 1, y2: 1,
                stop: 0 #eef3f9,
                stop: 1 #e7edf6
            );
            color: #172033;
            font-size: 13px;
        }

        QGroupBox {
            border: 1px solid #d4dcea;
            border-radius: 10px;
            margin-top: 10px;
            padding-top: 10px;
            font-weight: 600;
            background-color: #ffffff;
        }

        QGroupBox::title {
            subcontrol-origin: margin;
            left: 12px;
            padding: 1px 6px;
            color: #0f2d6e;
        }

        QLabel {
            color: #172033;
            background: transparent;
        }

        QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox, QDoubleSpinBox, QComboBox, QTreeWidget, QListWidget {
            background-color: #ffffff;
            border: 1px solid #c6cfde;
            border-radius: 8px;
            padding: 6px 8px;
        }

        QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox, QPushButton {
            min-height: 32px;
        }

        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus, QTreeWidget:focus, QListWidget:focus {
            border: 1px solid #2e70ed;
            outline: none;
        }

        QPlainTextEdit, QTextEdit {
            selection-background-color: #cfe2ff;
        }

        QPlainTextEdit#LogView {
            background-color: #f8fbff;
        }

        QTreeWidget::item {
            min-height: 24px;
        }

        QPushButton {
            background-color: #266fe6;
            color: #ffffff;
            border: 1px solid #195bca;
            border-radius: 8px;
            padding: 6px 12px;
            font-weight: 600;
        }

        QPushButton:hover {
            background-color: #1f63d1;
        }

        QPushButton:disabled {
            background-color: #a6b8d7;
            border-color: #9cb0d1;
            color: #eef4ff;
        }

        QPushButton#StartButton {
            background-color: #1d7d46;
            border-color: #156239;
            font-weight: 700;
        }

        QPushButton#StartButton:hover {
            background-color: #176739;
        }

        QPushButton#StopButton {
            background-color: #bfcde6;
            border-color: #acbedf;
            color: #27436f;
        }

        QPushButton#ClearLogButton {
            background-color: #2a5fbb;
            border-color: #204f9f;
        }

        QPushButton#QuitButton {
            background-color: #2d3f5c;
            border-color: #22324d;
        }

        QTabWidget::pane {
            border: 1px solid #d4dcea;
            background-color: #ffffff;
            border-radius: 10px;
            top: -1px;
        }

        QTabBar::tab {
            background-color: #e5ebf5;
            border: 1px solid #d2dbe9;
            border-bottom: none;
            padding: 9px 14px;
            margin-right: 2px;
            border-top-left-radius: 9px;
            border-top-right-radius: 9px;
            min-height: 28px;
            color: #1f304b;
        }

        QTabBar::tab:selected {
            background-color: #ffffff;
            font-weight: 700;
            color: #0f2d6e;
        }

        QTabBar::tab:hover {
            background-color: #edf3fd;
        }

        QCheckBox {
            background: transparent;
            spacing: 8px;
            padding: 2px 0;
        }

        QCheckBox::indicator {
            width: 16px;
            height: 16px;
            border-radius: 4px;
            border: 1px solid #a6b2c4;
            background-color: #ffffff;
        }

        QCheckBox::indicator:checked {
            border-color: #1e67d8;
            background-color: #1e67d8;
        }

        QProgressBar {
            border: 1px solid #c5cfde;
            border-radius: 8px;
            background-color: #ffffff;
            min-height: 22px;
        }

        QProgressBar::chunk {
            border-radius: 6px;
            background: qlineargradient(
                x1: 0, y1: 0, x2: 1, y2: 0,
                stop: 0 #2d80f1,
                stop: 1 #1e67d8
            );
        }
        """
    )


def toggle_password_visibility(entry: QLineEdit, button: QPushButton):
    """Toggle password visibility in a line edit widget."""
    is_hidden = entry.echoMode() == QLineEdit.Password
    entry.setEchoMode(QLineEdit.Normal if is_hidden else QLineEdit.Password)
    button.setText("Hide" if is_hidden else "Show")
