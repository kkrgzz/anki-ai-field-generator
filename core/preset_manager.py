"""Manages saving and loading named prompt presets via QSettings."""

import json

from aqt.qt import QSettings

from .settings import SETTINGS_ORGANIZATION, SETTINGS_APPLICATION

PRESETS_GROUP = "presets"


class PresetManager:
    """Handles CRUD operations for named presets stored in QSettings."""

    # Keys stored in each preset
    SYSTEM_PROMPT = "system_prompt"
    USER_PROMPT = "user_prompt"
    RESPONSE_KEYS = "response_keys"
    DESTINATION_FIELDS = "destination_field"

    @staticmethod
    def _get_settings() -> QSettings:
        return QSettings(SETTINGS_ORGANIZATION, SETTINGS_APPLICATION)

    @classmethod
    def list_presets(cls) -> list[str]:
        """Returns sorted list of preset names."""
        settings = cls._get_settings()
        settings.beginGroup(PRESETS_GROUP)
        names = settings.childGroups()
        settings.endGroup()
        return sorted(names)

    @classmethod
    def save_preset(cls, name: str, system_prompt: str, user_prompt: str,
                    response_keys: list[str], destination_fields: list[str]):
        """Saves a preset with the given name. Overwrites if it already exists."""
        settings = cls._get_settings()
        settings.beginGroup(PRESETS_GROUP)
        settings.beginGroup(name)
        settings.setValue(cls.SYSTEM_PROMPT, system_prompt)
        settings.setValue(cls.USER_PROMPT, user_prompt)
        settings.setValue(cls.RESPONSE_KEYS, response_keys)
        settings.setValue(cls.DESTINATION_FIELDS, destination_fields)
        settings.endGroup()
        settings.endGroup()

    @classmethod
    def load_preset(cls, name: str) -> dict | None:
        """Loads a preset by name. Returns None if not found."""
        settings = cls._get_settings()
        settings.beginGroup(PRESETS_GROUP)
        if name not in settings.childGroups():
            settings.endGroup()
            return None
        settings.beginGroup(name)
        preset = {
            cls.SYSTEM_PROMPT: settings.value(cls.SYSTEM_PROMPT, defaultValue="", type=str),
            cls.USER_PROMPT: settings.value(cls.USER_PROMPT, defaultValue="", type=str),
            cls.RESPONSE_KEYS: settings.value(cls.RESPONSE_KEYS, defaultValue=[], type="QStringList"),
            cls.DESTINATION_FIELDS: settings.value(cls.DESTINATION_FIELDS, defaultValue=[], type="QStringList"),
        }
        settings.endGroup()
        settings.endGroup()
        return preset

    @classmethod
    def delete_preset(cls, name: str):
        """Deletes a preset by name."""
        settings = cls._get_settings()
        settings.beginGroup(PRESETS_GROUP)
        settings.remove(name)
        settings.endGroup()

    @classmethod
    def export_presets(cls, file_path: str, preset_names: list[str] | None = None):
        """Exports presets to a JSON file.

        Args:
            file_path: Destination file path.
            preset_names: Names to export. If None, exports all presets.
        """
        if preset_names is None:
            preset_names = cls.list_presets()

        data = {}
        for name in preset_names:
            preset = cls.load_preset(name)
            if preset:
                data[name] = preset

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    @classmethod
    def import_presets(cls, file_path: str) -> list[str]:
        """Imports presets from a JSON file.

        Returns:
            List of imported preset names.
        """
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, dict):
            raise ValueError("Invalid preset file format.")

        imported = []
        for name, preset in data.items():
            if not isinstance(preset, dict):
                continue
            cls.save_preset(
                name=str(name),
                system_prompt=preset.get(cls.SYSTEM_PROMPT, ""),
                user_prompt=preset.get(cls.USER_PROMPT, ""),
                response_keys=preset.get(cls.RESPONSE_KEYS, []),
                destination_fields=preset.get(cls.DESTINATION_FIELDS, []),
            )
            imported.append(str(name))
        return imported
