"""Export settings tab (PySide6)."""

from pathlib import Path

from PySide6.QtWidgets import (
    QCheckBox,
    QFileDialog,
    QGridLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


def create_export_tab(gui_instance) -> QWidget:
    """Create export settings tab."""
    tab = QWidget()
    layout = QVBoxLayout(tab)
    layout.setContentsMargins(8, 8, 8, 8)
    layout.setSpacing(8)

    formats_group = QGroupBox("Export Formats")
    formats_layout = QVBoxLayout(formats_group)

    formats_layout.addWidget(QLabel("Select additional export formats:"))

    gui_instance.export_md_check = QCheckBox("Markdown (.md)")
    gui_instance.export_md_check.setChecked(True)  # Enabled by default
    gui_instance.export_latex_check = QCheckBox("LaTeX (.tex)")

    formats_layout.addWidget(gui_instance.export_md_check)
    formats_layout.addWidget(gui_instance.export_latex_check)

    layout.addWidget(formats_group)

    settings_group = QGroupBox("Export Settings")
    settings_layout = QGridLayout(settings_group)

    settings_layout.addWidget(QLabel("Export Directory:"), 0, 0)
    gui_instance.export_dir_edit = QLineEdit(gui_instance.export_dir_default)
    settings_layout.addWidget(gui_instance.export_dir_edit, 0, 1)

    browse_btn = QPushButton("Browse")
    browse_btn.clicked.connect(lambda: browse_export_dir(gui_instance))
    settings_layout.addWidget(browse_btn, 0, 2)

    settings_layout.setColumnStretch(1, 1)
    layout.addWidget(settings_group)

    info_group = QGroupBox("Information")
    info_layout = QVBoxLayout(info_group)
    info_label = QLabel("""Export transcriptions into additional formats:

• Markdown: Clean, portable text format for documentation
• LaTeX: Scientific documents with correct formatting""")
    info_label.setWordWrap(True)
    info_layout.addWidget(info_label)

    layout.addWidget(info_group)
    layout.addStretch(1)
    return tab


def browse_export_dir(gui_instance):
    """Browse for export directory."""
    current = gui_instance.export_dir_edit.text().strip() or str(Path.cwd())
    directory = QFileDialog.getExistingDirectory(gui_instance, "Select Export Directory", current)
    if directory:
        gui_instance.export_dir_edit.setText(directory)
