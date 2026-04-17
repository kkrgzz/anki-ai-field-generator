from collections.abc import Callable
from PyQt6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
)
from PyQt6.QtCore import QThread, Qt

from .styles import apply_stylesheet, SPACING_MD, SPACING_LG


class ProgressDialog(QDialog):
    def __init__(self, worker: QThread, success_callback: Callable):
        super().__init__()
        self.success_callback = success_callback
        self.setWindowTitle("Processing")
        self.setModal(True)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.resize(450, 200)

        apply_stylesheet(self)

        self.layout = QVBoxLayout()
        self.layout.setSpacing(SPACING_LG)

        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(100)
        self.layout.addWidget(self.progress_bar)

        self.label = QLabel("Starting processing...")
        self.label.setWordWrap(True)
        self.layout.addWidget(self.label)

        self.layout.addStretch()

        button_layout = QHBoxLayout()
        button_layout.setSpacing(SPACING_MD)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.cancel)
        button_layout.addWidget(self.cancel_button)

        self.resume_button = QPushButton("Continue")
        self.resume_button.clicked.connect(self.resume)
        self.resume_button.hide()
        button_layout.addWidget(self.resume_button)

        self.close_button = QPushButton("Close")
        self.close_button.setProperty("cssClass", "primary")
        self.close_button.clicked.connect(self.on_success)
        self.close_button.hide()
        button_layout.addWidget(self.close_button)

        self.layout.addLayout(button_layout)
        self.setLayout(self.layout)

        self.worker = worker
        self.worker.progress_updated.connect(self.update_progress)
        self.worker.finished.connect(self.complete)
        self.worker.error.connect(self.error)
        self.worker.start()

    def update_progress(self, value, text):
        self.progress_bar.setValue(value)
        self.label.setText(text)

    def complete(self):
        self.progress_bar.setValue(100)
        self.label.setText("Processing complete!")
        self.cancel_button.hide()
        self.close_button.show()

    def error(self, text):
        self.label.setText(f"<b>Error:</b> {text}")
        self.resume_button.show()

    def resume(self):
        self.resume_button.hide()
        self.worker.start()

    def cancel(self):
        if self.worker.isRunning():
            self.worker.cancel()  # Request graceful cancellation
        self.reject()  # Close the dialog

    def on_success(self):
        self.cancel()
        self.success_callback()
