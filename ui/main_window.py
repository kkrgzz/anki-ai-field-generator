from collections.abc import Callable
from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QWidget,
    QVBoxLayout,
    QComboBox,
)

from .styles import apply_stylesheet, SPACING_MD, SPACING_LG, SPACING_XL, COLOR_TEXT_SECONDARY
from .tools import UITools


class MainWindow(QMainWindow):
    def __init__(self, client_factory, on_submit: Callable, on_preview: Callable):
        super().__init__()
        self.client_factory = client_factory
        self.on_preview = on_preview
        self.ui_tools = UITools(None, None)

        self.setWindowTitle("Anki AI - Update Your Flashcards with AI")
        screen = QApplication.primaryScreen().geometry()
        width = 1100
        height = 900
        x = (screen.width() - width) // 2
        y = (screen.height() - height) // 2
        self.setGeometry(x, y, width, height)

        apply_stylesheet(self)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        self.layout = QVBoxLayout()
        self.layout.setSpacing(SPACING_MD)
        self.layout.setContentsMargins(SPACING_XL, SPACING_XL, SPACING_XL, SPACING_XL)

        # -- Header bar --
        header = QHBoxLayout()
        header.setSpacing(SPACING_LG)

        title_label = QLabel("Anki AI")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        header.addWidget(title_label)

        subtitle = QLabel("Update your flashcards with AI")
        subtitle.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; font-size: 12px;")
        header.addWidget(subtitle)

        header.addStretch()

        llm_label = QLabel("Provider:")
        llm_label.setStyleSheet("font-weight: bold;")
        header.addWidget(llm_label)
        self.client_selector = QComboBox()
        self.client_selector.addItems(client_factory.valid_clients)
        self.client_selector.setFixedWidth(160)
        self.client_selector.currentIndexChanged.connect(self.switch_client)
        header.addWidget(self.client_selector)

        self.layout.addLayout(header)

        # -- Client UI container --
        client_ui_container = QWidget()
        self.client_ui_layout = QVBoxLayout()
        self.client_ui_layout.setContentsMargins(0, 0, 0, 0)
        client_ui_container.setLayout(self.client_ui_layout)
        self.layout.addWidget(client_ui_container)
        self.current_client_widget = None

        central_widget.setLayout(self.layout)

        # Initialize default client
        self.client_selector.setCurrentIndex(
            client_factory.valid_clients.index(client_factory.client_name)
        )
        self.switch_client()

        # -- Bottom button bar --
        button_bar = QHBoxLayout()
        button_bar.setSpacing(SPACING_MD)

        test_button = QPushButton("Test on 1 Card")
        test_button.clicked.connect(lambda: self.run_preview())
        button_bar.addWidget(test_button)

        button_bar.addStretch()

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.close)
        button_bar.addWidget(cancel_button)

        ok_button = QPushButton("Process All Cards")
        ok_button.setProperty("cssClass", "primary")
        ok_button.clicked.connect(lambda: self.accept(on_submit))
        button_bar.addWidget(ok_button)

        self.layout.addLayout(button_bar)

    def switch_client(self):
        client_name = self.client_selector.currentText()
        if self.current_client_widget:
            self.client_ui_layout.removeWidget(self.current_client_widget)
            self.current_client_widget.deleteLater()

        self.client_factory.update_client(client_name)
        self.current_client_widget = self.client_factory.get_dialog()
        self.client_ui_layout.addWidget(self.current_client_widget)
        self.current_client_widget.show()
        self.layout.update()

    def accept(self, on_submit: Callable):
        if self.current_client_widget.accept():
            on_submit()

    def run_preview(self):
        if self.current_client_widget.accept():
            self.on_preview()
