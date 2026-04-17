"""Dialog that tests the current configuration on a single card and shows results."""

from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ..clients.base import LLMClient
from ..core.exceptions import ExternalException


class PreviewWorker(QThread):
    """Runs a single LLM call in a background thread."""

    success = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, client, prompt):
        super().__init__()
        self.client = client
        self.prompt = prompt

    def run(self):
        try:
            result = self.client.call([self.prompt])
            self.success.emit(result)
        except ExternalException as e:
            self.error.emit(str(e))
        except Exception as e:
            self.error.emit(f"Unexpected error: {e}")


class PreviewDialog(QDialog):
    """Shows the prompt that will be sent and the AI response for one card."""

    def __init__(self, client: LLMClient, note, response_keys, note_fields, parent=None):
        super().__init__(parent)
        self.client = client
        self.note = note
        self.response_keys = response_keys
        self.note_fields = note_fields
        self.worker = None

        self.setWindowTitle("Preview - Test on 1 Card")
        self.setMinimumSize(700, 500)
        self.setModal(True)

        layout = QVBoxLayout(self)

        # --- Prompt section ---
        layout.addWidget(self._bold_label("System Prompt:"))
        self.system_prompt_view = QTextEdit()
        self.system_prompt_view.setReadOnly(True)
        self.system_prompt_view.setMaximumHeight(120)
        self.system_prompt_view.setPlainText(client.prompt_config.system_prompt)
        layout.addWidget(self.system_prompt_view)

        layout.addWidget(self._bold_label("User Prompt (filled with card data):"))
        self.user_prompt_view = QTextEdit()
        self.user_prompt_view.setReadOnly(True)
        self.user_prompt_view.setMaximumHeight(100)
        try:
            filled_prompt = client.get_user_prompt(note)
        except Exception as e:
            filled_prompt = f"[Error filling prompt: {e}]"
        self.user_prompt_view.setPlainText(filled_prompt)
        layout.addWidget(self.user_prompt_view)

        # --- Response section ---
        layout.addWidget(self._bold_label("AI Response:"))
        self.response_view = QTextEdit()
        self.response_view.setReadOnly(True)
        layout.addWidget(self.response_view)

        # --- Field mapping preview ---
        layout.addWidget(self._bold_label("Field Mapping Preview:"))
        self.mapping_view = QTextEdit()
        self.mapping_view.setReadOnly(True)
        self.mapping_view.setMaximumHeight(120)
        layout.addWidget(self.mapping_view)

        # --- Status ---
        self.status_label = QLabel("")
        layout.addWidget(self.status_label)

        # --- Buttons ---
        button_layout = QHBoxLayout()
        self.run_button = QPushButton("Send to AI")
        self.run_button.clicked.connect(self.run_preview)
        button_layout.addWidget(self.run_button)

        button_layout.addStretch()

        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)
        button_layout.addWidget(close_button)

        layout.addLayout(button_layout)

        # Auto-run on open
        self.run_preview()

    def run_preview(self):
        self.run_button.setEnabled(False)
        self.status_label.setText("Sending to AI...")
        self.response_view.setPlainText("")
        self.mapping_view.setPlainText("")

        try:
            prompt = self.client.get_user_prompt(self.note)
        except Exception as e:
            self.status_label.setText(f"Error: {e}")
            self.run_button.setEnabled(True)
            return

        self.worker = PreviewWorker(self.client, prompt)
        self.worker.success.connect(self._on_success)
        self.worker.error.connect(self._on_error)
        self.worker.finished.connect(lambda: self.run_button.setEnabled(True))
        self.worker.start()

    def _on_success(self, response: dict):
        # Show raw response
        lines = []
        for key, value in response.items():
            lines.append(f"{key}: {value}")
        self.response_view.setPlainText("\n".join(lines))

        # Show how it maps to fields
        mapping_lines = []
        for response_key, note_field in zip(self.response_keys, self.note_fields):
            value = response.get(response_key, "<missing from response>")
            mapping_lines.append(f"{note_field}  ←  {value}")
        self.mapping_view.setPlainText("\n".join(mapping_lines))
        self.status_label.setText("Preview complete. No changes were saved to the card.")

    def _on_error(self, error_msg: str):
        self.response_view.setPlainText(f"Error:\n{error_msg}")
        self.status_label.setText("Request failed.")

    def _bold_label(self, text: str) -> QLabel:
        label = QLabel(text)
        font = label.font()
        font.setBold(True)
        font.setPointSize(11)
        label.setFont(font)
        return label

    def closeEvent(self, event):
        if self.worker and self.worker.isRunning():
            self.worker.quit()
            self.worker.wait(2000)
        super().closeEvent(event)
