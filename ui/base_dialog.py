from abc import ABCMeta, abstractmethod
from anki.notes import Note as AnkiNote
from aqt.qt import (
    QSettings,
    QWidget,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QVBoxLayout,
    Qt,
    QScrollArea,
)
from PyQt6 import QtCore
from ..core.settings import SettingsNames
from .dynamic_form import DynamicForm
from .preset_bar import PresetBar
from .styles import SPACING_SM, SPACING_MD, SPACING_LG, COLOR_TEXT_SECONDARY
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

    def show(self):
        if self.layout() is not None:
            QWidget().setLayout(self.layout())
        card_fields = sorted(
            {field for note in self.selected_notes for field in note.keys()}
        )

        self.resize(self._width * 2 + 20, 750)
        container_widget = QWidget()
        main_layout = QHBoxLayout(container_widget)
        main_layout.setSpacing(SPACING_LG)

        # -- LEFT COLUMN --
        left_container = QWidget()
        left_container.setMaximumWidth(self._width)
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(SPACING_SM)
        left_container.setLayout(left_layout)

        # Connection Settings group
        conn_group = QGroupBox("Connection Settings")
        conn_layout = QVBoxLayout()
        conn_layout.setSpacing(SPACING_MD)
        conn_group.setLayout(conn_layout)

        conn_layout.addWidget(self._field_label("Model"))
        conn_layout.addWidget(
            self.ui_tools.create_dropdown(
                SettingsNames.MODEL_SETTING_NAME, self.models, allow_custom=True
            )
        )

        conn_layout.addWidget(self._field_label(f"{self.service_name} API Key"))
        conn_layout.addWidget(
            self.ui_tools.create_text_entry(SettingsNames.API_KEY_SETTING_NAME)
        )

        conn_layout.addWidget(self._field_label("Base URL"))
        desc = QLabel("Override the default API endpoint (leave blank for default)")
        desc.setProperty("cssClass", "muted")
        desc.setWordWrap(True)
        conn_layout.addWidget(desc)
        conn_layout.addWidget(
            self.ui_tools.create_text_entry(
                SettingsNames.BASE_URL_SETTING_NAME,
                placeholder=self.base_url,
            )
        )

        conn_layout.addWidget(self._field_label("Max Concurrent Requests"))
        conn_layout.addWidget(
            self.ui_tools.create_text_entry(
                SettingsNames.MAX_CONCURRENT_REQUESTS_SETTING_NAME,
                placeholder="10",
                default_value="10",
            )
        )
        left_layout.addWidget(conn_group)

        # System Prompt group
        sys_group = QGroupBox("System Prompt")
        sys_layout = QVBoxLayout()
        sys_layout.setSpacing(SPACING_MD)
        sys_group.setLayout(sys_layout)

        sys_desc = QLabel(self.system_prompt_description)
        sys_desc.setProperty("cssClass", "description")
        sys_desc.setWordWrap(True)
        sys_layout.addWidget(sys_desc)

        sys_layout.addWidget(
            self.ui_tools.create_text_edit(
                SettingsNames.SYSTEM_PROMPT_SETTING_NAME,
                self.system_prompt_placeholder,
                min_height=180,
            )
        )
        left_layout.addWidget(sys_group)

        left_layout.addStretch()

        # -- RIGHT COLUMN --
        right_container = QWidget()
        right_container.setMaximumWidth(self._width)
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(SPACING_SM)
        right_container.setLayout(right_layout)
        right_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Presets group
        preset_group = QGroupBox("Presets")
        preset_layout = QVBoxLayout()
        preset_layout.setSpacing(SPACING_MD)
        preset_group.setLayout(preset_layout)

        preset_desc = QLabel("Save and load prompt configurations for reuse across providers.")
        preset_desc.setProperty("cssClass", "muted")
        preset_desc.setWordWrap(True)
        preset_layout.addWidget(preset_desc)

        self.preset_bar = PresetBar(app_settings=self.app_settings)
        self.preset_bar.get_current_values = self._get_preset_values
        self.preset_bar.preset_loaded.connect(
            lambda preset: self._apply_preset(preset, card_fields)
        )
        preset_layout.addWidget(self.preset_bar)
        right_layout.addWidget(preset_group)

        # User Prompt group
        user_group = QGroupBox("User Prompt")
        user_layout = QVBoxLayout()
        user_layout.setSpacing(SPACING_MD)
        user_group.setLayout(user_layout)

        user_desc = QLabel(self.user_prompt_description)
        user_desc.setProperty("cssClass", "description")
        user_desc.setWordWrap(True)
        user_layout.addWidget(user_desc)

        user_layout.addWidget(
            self.ui_tools.create_text_edit(
                SettingsNames.USER_PROMPT_SETTING_NAME,
                self.user_prompt_placeholder,
                min_height=100,
            )
        )

        fields_label = QLabel("Available fields: " + ", ".join(
            f"{{{f}}}" for f in card_fields
        ))
        fields_label.setProperty("cssClass", "muted")
        fields_label.setWordWrap(True)
        user_layout.addWidget(fields_label)

        right_layout.addWidget(user_group)

        # Output Mapping group
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

        right_layout.addWidget(mapping_group)

        # Status bar
        status = QLabel(f"{len(self.selected_notes)} card(s) selected")
        status.setProperty("cssClass", "status-info")
        right_layout.addWidget(status)

        main_layout.addWidget(left_container)
        main_layout.addWidget(right_container)

        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(container_widget)

        final_layout = QVBoxLayout(self)
        final_layout.setContentsMargins(0, 0, 0, 0)
        final_layout.addWidget(scroll_area)
        self.setLayout(final_layout)
        return self

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
            preset.get("destination_fields", []),
            card_fields,
        )
        self._two_col_form_layout.insertWidget(
            self._two_col_form_index, self.two_col_form
        )

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
