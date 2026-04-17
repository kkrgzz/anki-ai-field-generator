from abc import ABCMeta, abstractmethod
from anki.notes import Note as AnkiNote
from aqt.qt import (
    QSettings,
    QWidget,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    Qt,
    QScrollArea,
)
from PyQt6 import QtCore
from ..core.settings import SettingsNames
from .dynamic_form import DynamicForm
from .preset_bar import PresetBar
from .styles import SPACING_SM, SPACING_MD, SPACING_LG, COLOR_TEXT_SECONDARY, COLOR_BORDER
from .tools import UITools


class MyMeta(ABCMeta, type(QtCore.QObject)):
    pass


class UserBaseDialog(QWidget, metaclass=MyMeta):
    def __init__(self, app_settings: QSettings, selected_notes: list[AnkiNote]):
        super().__init__()
        self._width = 500
        self.app_settings: QSettings = app_settings
        self.selected_notes = selected_notes
        self.ui_tools: UITools = UITools(app_settings, self._width)
        self._applying_preset = False

    def show(self):
        if self.layout() is not None:
            QWidget().setLayout(self.layout())
        card_fields = sorted(
            {field for note in self.selected_notes for field in note.keys()}
        )

        self.resize(self._width * 2 + 20, 750)
        container_widget = QWidget()
        outer_layout = QVBoxLayout(container_widget)
        outer_layout.setSpacing(SPACING_MD)

        # ── Connection Settings (collapsible, compact grid) ──
        conn_header = QHBoxLayout()
        self._conn_toggle = QPushButton("\u25BC Connection Settings")
        self._conn_toggle.setFlat(True)
        self._conn_toggle.setStyleSheet(
            f"text-align: left; font-weight: bold; font-size: 13px; "
            f"border: none; padding: 4px 0;"
        )
        self._conn_toggle.setCursor(Qt.CursorShape.PointingHandCursor)
        self._conn_toggle.clicked.connect(self._toggle_connection)
        conn_header.addWidget(self._conn_toggle)
        conn_header.addStretch()
        outer_layout.addLayout(conn_header)

        self._conn_frame = QFrame()
        self._conn_frame.setStyleSheet(
            f"QFrame {{ border: 1px solid {COLOR_BORDER}; border-radius: 6px; "
            f"padding: 8px; }}"
        )
        conn_grid = QGridLayout()
        conn_grid.setSpacing(SPACING_MD)
        conn_grid.setColumnStretch(1, 1)
        conn_grid.setColumnStretch(3, 1)

        conn_grid.addWidget(self._field_label("Model"), 0, 0)
        conn_grid.addWidget(
            self.ui_tools.create_dropdown(
                SettingsNames.MODEL_SETTING_NAME, self.models, allow_custom=True
            ), 0, 1
        )

        conn_grid.addWidget(self._field_label(f"{self.service_name} API Key"), 0, 2)
        conn_grid.addWidget(
            self.ui_tools.create_text_entry(SettingsNames.API_KEY_SETTING_NAME), 0, 3
        )

        conn_grid.addWidget(self._field_label("Base URL"), 1, 0)
        conn_grid.addWidget(
            self.ui_tools.create_text_entry(
                SettingsNames.BASE_URL_SETTING_NAME,
                placeholder=self.base_url,
            ), 1, 1
        )

        conn_grid.addWidget(self._field_label("Max Requests"), 1, 2)
        conn_grid.addWidget(
            self.ui_tools.create_text_entry(
                SettingsNames.MAX_CONCURRENT_REQUESTS_SETTING_NAME,
                placeholder="10",
                default_value="10",
            ), 1, 3
        )

        self._conn_frame.setLayout(conn_grid)
        outer_layout.addWidget(self._conn_frame)

        # Auto-collapse if API key is already set
        api_key = self.app_settings.value(SettingsNames.API_KEY_SETTING_NAME, "")
        if api_key:
            self._conn_frame.hide()
            self._conn_toggle.setText("\u25B6 Connection Settings")

        # ── Presets bar (full width, compact) ──
        preset_row = QHBoxLayout()
        preset_row.setSpacing(SPACING_MD)
        preset_label = QLabel("Preset:")
        preset_label.setStyleSheet("font-weight: bold;")
        preset_row.addWidget(preset_label)

        self.preset_bar = PresetBar(app_settings=self.app_settings)
        self.preset_bar.get_current_values = self._get_preset_values
        self.preset_bar.preset_loaded.connect(
            lambda preset: self._apply_preset(preset, card_fields)
        )
        preset_row.addWidget(self.preset_bar)
        outer_layout.addLayout(preset_row)

        # ── Two-column prompts ──
        prompt_columns = QHBoxLayout()
        prompt_columns.setSpacing(SPACING_LG)

        # Left: System Prompt
        sys_group = QGroupBox("System Prompt")
        sys_layout = QVBoxLayout()
        sys_layout.setSpacing(SPACING_MD)
        sys_group.setLayout(sys_layout)

        sys_desc = QLabel(self.system_prompt_description)
        sys_desc.setProperty("cssClass", "description")
        sys_desc.setWordWrap(True)
        sys_layout.addWidget(sys_desc)

        sys_edit = self.ui_tools.create_text_edit(
            SettingsNames.SYSTEM_PROMPT_SETTING_NAME,
            self.system_prompt_placeholder,
            min_height=200,
        )
        sys_edit.textChanged.connect(self._on_preset_field_changed)
        sys_layout.addWidget(sys_edit)
        prompt_columns.addWidget(sys_group)

        # Right: User Prompt
        user_group = QGroupBox("User Prompt")
        user_layout = QVBoxLayout()
        user_layout.setSpacing(SPACING_MD)
        user_group.setLayout(user_layout)

        user_desc = QLabel(self.user_prompt_description)
        user_desc.setProperty("cssClass", "description")
        user_desc.setWordWrap(True)
        user_layout.addWidget(user_desc)

        user_edit = self.ui_tools.create_text_edit(
            SettingsNames.USER_PROMPT_SETTING_NAME,
            self.user_prompt_placeholder,
            min_height=120,
        )
        user_edit.textChanged.connect(self._on_preset_field_changed)
        user_layout.addWidget(user_edit)

        fields_label = QLabel("Available fields: " + ", ".join(
            f"{{{f}}}" for f in card_fields
        ))
        fields_label.setProperty("cssClass", "muted")
        fields_label.setWordWrap(True)
        user_layout.addWidget(fields_label)

        user_layout.addStretch()
        prompt_columns.addWidget(user_group)

        outer_layout.addLayout(prompt_columns)

        # ── Field Mapping (full width) ──
        mapping_group = QGroupBox("Output \u2192 Field Mapping")
        mapping_layout = QVBoxLayout()
        mapping_layout.setSpacing(SPACING_MD)
        mapping_group.setLayout(mapping_layout)

        mapping_desc = QLabel(
            "Map each AI response key to the Anki field where it should be saved."
        )
        mapping_desc.setProperty("cssClass", "description")
        mapping_desc.setWordWrap(True)
        mapping_layout.addWidget(mapping_desc)

        self._card_fields = card_fields
        self.two_col_form = DynamicForm(
            self.app_settings.value(
                SettingsNames.RESPONSE_KEYS_SETTING_NAME, type="QStringList"
            ),
            self.app_settings.value(
                SettingsNames.DESTINATION_FIELD_SETTING_NAME, type="QStringList"
            ),
            card_fields,
        )
        self._two_col_form_layout = mapping_layout
        self._two_col_form_index = mapping_layout.count()
        mapping_layout.addWidget(self.two_col_form)

        outer_layout.addWidget(mapping_group)

        # Status bar
        status = QLabel(f"{len(self.selected_notes)} card(s) selected")
        status.setProperty("cssClass", "status-info")
        outer_layout.addWidget(status)

        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(container_widget)

        final_layout = QVBoxLayout(self)
        final_layout.setContentsMargins(0, 0, 0, 0)
        final_layout.addWidget(scroll_area)
        self.setLayout(final_layout)
        return self

    def _on_preset_field_changed(self):
        """Called when a preset-tracked field changes."""
        if not self._applying_preset:
            self.preset_bar.mark_dirty()

    def _toggle_connection(self):
        """Toggle the connection settings panel visibility."""
        if self._conn_frame.isVisible():
            self._conn_frame.hide()
            self._conn_toggle.setText("\u25B6 Connection Settings")
        else:
            self._conn_frame.show()
            self._conn_toggle.setText("\u25BC Connection Settings")

    def _field_label(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setStyleSheet("font-weight: bold; font-size: 12px;")
        return label

    @property
    @abstractmethod
    def service_name(self):
        pass

    @property
    @abstractmethod
    def models(self) -> list[str]:
        pass

    @property
    @abstractmethod
    def base_url(self):
        pass

    @property
    @abstractmethod
    def system_prompt_description(self):
        pass

    @property
    @abstractmethod
    def system_prompt_placeholder(self):
        pass

    @property
    @abstractmethod
    def user_prompt_description(self):
        pass

    @property
    @abstractmethod
    def user_prompt_placeholder(self):
        pass

    def accept(self) -> bool:
        if not self.are_settings_valid():
            return False
        self.ui_tools.save_settings()
        keys, fields = self.two_col_form.get_inputs()
        self.app_settings.setValue(SettingsNames.RESPONSE_KEYS_SETTING_NAME, keys)
        self.app_settings.setValue(
            SettingsNames.DESTINATION_FIELD_SETTING_NAME,
            fields,
        )
        # Auto-save the active preset if it was modified
        if self.preset_bar.is_dirty() and self.preset_bar.active_preset_name():
            self.preset_bar.save_active_preset(self._get_preset_values())
        return True

    def _get_preset_values(self) -> dict:
        settings = self.ui_tools.get_settings()
        keys, fields = self.two_col_form.get_inputs()
        return {
            "system_prompt": settings.get(SettingsNames.SYSTEM_PROMPT_SETTING_NAME, ""),
            "user_prompt": settings.get(SettingsNames.USER_PROMPT_SETTING_NAME, ""),
            "response_keys": keys,
            "destination_fields": fields,
        }

    def _apply_preset(self, preset: dict, card_fields: list[str]):
        # Temporarily disable dirty tracking while applying preset values
        self._applying_preset = True

        system_widget = self.ui_tools.widgets.get(SettingsNames.SYSTEM_PROMPT_SETTING_NAME)
        if system_widget:
            system_widget.setPlainText(preset.get("system_prompt", ""))

        user_widget = self.ui_tools.widgets.get(SettingsNames.USER_PROMPT_SETTING_NAME)
        if user_widget:
            user_widget.setPlainText(preset.get("user_prompt", ""))

        old_form = self.two_col_form
        self._two_col_form_layout.removeWidget(old_form)
        old_form.deleteLater()

        self.two_col_form = DynamicForm(
            preset.get("response_keys", []),
            preset.get("destination_field", []),
            card_fields,
        )
        self._two_col_form_layout.insertWidget(
            self._two_col_form_index, self.two_col_form
        )

        self._applying_preset = False

    def are_settings_valid(self) -> bool:
        settings = self.ui_tools.get_settings()
        if (
            SettingsNames.API_KEY_SETTING_NAME not in settings
            or not settings[SettingsNames.API_KEY_SETTING_NAME]
        ):
            _show_error("Please enter an API key.")
            return False
        if (
            SettingsNames.USER_PROMPT_SETTING_NAME not in settings
            or not settings[SettingsNames.USER_PROMPT_SETTING_NAME]
        ):
            _show_error("Please enter a prompt.")
            return False

        keys, fields = self.two_col_form.get_inputs()
        if len(keys) == 0 or len(fields) == 0:
            _show_error("You must map at least one AI output to an Anki field.")
            return False

        return True


def _show_error(message: str):
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Icon.Critical)
    msg_box.setWindowTitle("Validation Error")
    msg_box.setText(message)
    msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
    msg_box.exec()
