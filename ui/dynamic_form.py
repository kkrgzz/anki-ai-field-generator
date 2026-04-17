from functools import partial

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QComboBox,
    QPushButton,
)

from .styles import SPACING_SM, SPACING_MD


class DynamicForm(QWidget):
    def __init__(self, keys: list[str], fields: list[str], card_fields: list[str]):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(SPACING_SM)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self._card_fields = [""] + card_fields if card_fields[0] != "" else card_fields

        self.add_button = QPushButton("+ Add Mapping")
        self.add_button.clicked.connect(partial(self.add_row, key="", field=""))
        self._fill_initial_data(keys, fields, card_fields)
        self.layout.addWidget(self.add_button)
        self.setLayout(self.layout)

    def _fill_initial_data(
        self, keys: list[str], fields: list[str], card_fields: list[str]
    ):
        all_fields_valid = (
            all(field in card_fields for field in fields) and len(fields) > 0
        )
        if all_fields_valid:
            for key, field in zip(keys, fields):
                self.add_row(key, field)
        else:
            self.add_row()

    def add_row(self, key="", field=""):
        row_layout = QHBoxLayout()
        row_layout.setSpacing(SPACING_MD)

        text_box = QLineEdit()
        text_box.setPlaceholderText("AI response key")
        row_layout.addWidget(text_box)
        text_box.setText(key)

        arrow = QLabel("\u2192")
        arrow.setProperty("cssClass", "arrow")
        arrow.setFixedWidth(20)
        row_layout.addWidget(arrow)

        combo_box = QComboBox()
        combo_box.addItems(self._card_fields)
        row_layout.addWidget(combo_box)
        combo_box.setCurrentText(field)

        remove_btn = QPushButton("\u2212")
        remove_btn.setFixedWidth(28)
        remove_btn.setToolTip("Remove mapping")
        remove_btn.setProperty("cssClass", "danger")
        remove_btn.clicked.connect(partial(self._remove_row, row_layout))
        row_layout.addWidget(remove_btn)

        self.layout.insertLayout(self.layout.count() - 1, row_layout)

    def _remove_row(self, row_layout: QHBoxLayout):
        # Remove all widgets in the row
        while row_layout.count():
            item = row_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        self.layout.removeItem(row_layout)
        row_layout.deleteLater()

    def get_inputs(self):
        """
        Returns two lists: the fields and the values
        """
        # Iterate through all rows and gather inputs
        keys = []
        fields = []
        for i in range(self.layout.count()):
            item = self.layout.itemAt(i)
            key = ""
            field = ""
            if isinstance(item, QHBoxLayout):
                for j in range(item.count()):
                    widget = item.itemAt(j).widget()
                    if isinstance(widget, QLineEdit):
                        key = widget.text()
                    elif isinstance(widget, QComboBox):
                        field = widget.currentText()
                    if key and field:
                        keys.append(key)
                        fields.append(field)

        return keys, fields
