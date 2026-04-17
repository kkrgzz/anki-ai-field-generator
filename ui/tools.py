from aqt.qt import (
    QComboBox,
    QFont,
    QGroupBox,
    QLabel,
    QLineEdit,
    QSettings,
    QTextEdit,
    QVBoxLayout,
)

from .styles import SPACING_SM, SPACING_MD


class UITools:
    def __init__(self, settings: QSettings, max_width):
        self.max_width = max_width
        self.settings = settings
        self.widgets = {}

    def create_label(self, label_text):
        label = QLabel(label_text)
        label.setProperty("cssClass", "section-title")
        return label

    def create_descriptive_text(self, text):
        label = QLabel(text)
        label.setProperty("cssClass", "description")
        if self.max_width:
            label.setMaximumWidth(self.max_width)
        label.setWordWrap(True)
        return label

    def create_group_box(self, title):
        """Creates a styled QGroupBox section card."""
        group = QGroupBox(title)
        layout = QVBoxLayout()
        layout.setSpacing(SPACING_MD)
        layout.setContentsMargins(SPACING_MD, SPACING_MD, SPACING_MD, SPACING_MD)
        group.setLayout(layout)
        return group, layout

    def create_dropdown(self, setting_name, items: list[str], allow_custom=False):
        combo_box = QComboBox()
        if self.max_width:
            combo_box.setMaximumWidth(self.max_width)
        combo_box.addItems(items)
        if allow_custom:
            combo_box.setEditable(True)
        if self.settings:
            setting_value = self.settings.value(setting_name)
            if setting_value:
                if setting_value not in items:
                    combo_box.addItem(setting_value)
                combo_box.setCurrentText(setting_value)
        self.widgets[setting_name] = combo_box
        return combo_box

    def create_text_entry(self, setting_name, placeholder="", default_value=None):
        setting_value = None
        if self.settings:
            setting_value = self.settings.value(setting_name)
        if setting_value in (None, ""):
            setting_value = "" if default_value is None else str(default_value)
        entry = QLineEdit(str(setting_value))
        entry.setPlaceholderText(placeholder)
        if self.max_width:
            entry.setMaximumWidth(self.max_width)
        self.widgets[setting_name] = entry
        return entry

    def create_text_edit(self, setting_name, placeholder="", min_height=120):
        text_edit = QTextEdit()
        text_edit.setMinimumHeight(min_height)
        text_edit.setAcceptRichText(False)
        if self.settings:
            setting_value = self.settings.value(setting_name)
            if setting_value:
                text_edit.setPlainText(setting_value)
        text_edit.setPlaceholderText(placeholder)
        self.widgets[setting_name] = text_edit
        return text_edit

    def save_settings(self):
        settings_values = self.get_settings()
        for setting_name, value in settings_values.items():
            self.settings.setValue(setting_name, value)

    def get_settings(self):
        settings = {}
        for setting_name, widget in self.widgets.items():
            if isinstance(widget, QTextEdit):
                settings[setting_name] = widget.toPlainText()
            elif isinstance(widget, QLineEdit):
                settings[setting_name] = widget.text()
            elif isinstance(widget, QComboBox):
                settings[setting_name] = widget.currentText()
        return settings
