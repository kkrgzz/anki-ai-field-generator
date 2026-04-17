from collections.abc import Callable
from PyQt6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
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
        self.resize(700, 500)

        apply_stylesheet(self)

        main_layout = QVBoxLayout()
        main_layout.setSpacing(SPACING_LG)

        # ── Tab widget ──
        self.tabs = QTabWidget()

        # --- Progress tab ---
        progress_tab = QWidget()
        progress_layout = QVBoxLayout()
        progress_layout.setSpacing(SPACING_LG)

        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(100)
        progress_layout.addWidget(self.progress_bar)

        self.label = QLabel("Starting processing...")
        self.label.setWordWrap(True)
        progress_layout.addWidget(self.label)

        progress_layout.addStretch()
        progress_tab.setLayout(progress_layout)
        self.tabs.addTab(progress_tab, "Progress")

        # --- Log tab ---
        log_tab = QWidget()
        log_layout = QVBoxLayout()
        log_layout.setSpacing(SPACING_MD)

        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        log_layout.addWidget(self.log_view)

        log_tab.setLayout(log_layout)
        self.tabs.addTab(log_tab, "Log (0)")

        self._log_count = 0

        main_layout.addWidget(self.tabs)

        # ── Button bar ──
        button_layout = QHBoxLayout()
        button_layout.setSpacing(SPACING_MD)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.cancel)
        button_layout.addWidget(self.cancel_button)

        self.resume_button = QPushButton("Continue")
        self.resume_button.clicked.connect(self.resume)
        self.resume_button.hide()
        button_layout.addWidget(self.resume_button)

        button_layout.addStretch()

        self.close_button = QPushButton("Close")
        self.close_button.setProperty("cssClass", "primary")
        self.close_button.clicked.connect(self.on_success)
        self.close_button.hide()
        button_layout.addWidget(self.close_button)

        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

        self.worker = worker
        self.worker.progress_updated.connect(self.update_progress)
        self.worker.finished.connect(self.complete)
        self.worker.error.connect(self.error)
        if hasattr(self.worker, "card_logged"):
            self.worker.card_logged.connect(self.add_log_entry)
        self.worker.start()

    def add_log_entry(self, card_index: int, prompt: str, response: dict):
        self._log_count += 1
        self.tabs.setTabText(1, f"Log ({self._log_count})")

        separator = "\u2500" * 60
        response_lines = "\n".join(f"  {k}: {v}" for k, v in response.items())

        entry = (
            f"{separator}\n"
            f"Card #{card_index + 1}\n"
            f"{separator}\n"
            f"\u25B6 Request:\n{prompt}\n\n"
            f"\u25C0 Response:\n{response_lines}\n\n"
        )
        self.log_view.append(entry)

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
