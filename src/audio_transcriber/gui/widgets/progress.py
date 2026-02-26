"""Progress and control widgets for the PySide6 GUI."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


def create_progress_section(gui_instance) -> tuple:
    """
    Create bottom section with progress display and control buttons.

    Returns:
        Tuple of (container, eta_label, throughput_label,
        cost_label, log_text, start_button, stop_button)
    """
    container = QWidget()
    root_layout = QVBoxLayout(container)
    root_layout.setContentsMargins(0, 0, 0, 0)
    root_layout.setSpacing(8)

    progress_group = QGroupBox("Status")
    progress_layout = QVBoxLayout(progress_group)
    progress_layout.setSpacing(8)

    stats_row = QHBoxLayout()
    eta_label = QLabel("ETA: --")
    throughput_label = QLabel("Durchsatz: --")
    cost_label = QLabel("Kosten: $0.0000")

    stats_row.addWidget(eta_label)
    stats_row.addSpacing(20)
    stats_row.addWidget(throughput_label)
    stats_row.addSpacing(20)
    stats_row.addWidget(cost_label)
    stats_row.addStretch(1)
    progress_layout.addLayout(stats_row)

    log_text = QPlainTextEdit()
    log_text.setObjectName("LogView")
    log_text.setReadOnly(True)
    log_text.setMinimumHeight(140)
    progress_layout.addWidget(log_text)

    root_layout.addWidget(progress_group)

    button_row = QHBoxLayout()
    button_row.setSpacing(8)

    start_button = QPushButton("Start Transcription")
    start_button.setObjectName("StartButton")
    start_button.clicked.connect(gui_instance.start_transcription)
    button_row.addWidget(start_button)

    stop_button = QPushButton("Stop")
    stop_button.setObjectName("StopButton")
    stop_button.clicked.connect(gui_instance.stop_transcription)
    stop_button.setEnabled(False)
    button_row.addWidget(stop_button)

    clear_log_button = QPushButton("Clear Log")
    clear_log_button.setObjectName("ClearLogButton")
    clear_log_button.clicked.connect(lambda: clear_log(log_text))
    button_row.addWidget(clear_log_button)

    button_row.addStretch(1)

    quit_button = QPushButton("Quit")
    quit_button.setObjectName("QuitButton")
    quit_button.clicked.connect(gui_instance.close)
    button_row.addWidget(quit_button, alignment=Qt.AlignRight)

    root_layout.addLayout(button_row)

    return (
        container,
        eta_label,
        throughput_label,
        cost_label,
        log_text,
        start_button,
        stop_button,
    )


def clear_log(log_text: QPlainTextEdit):
    """Clear log output."""
    log_text.clear()
