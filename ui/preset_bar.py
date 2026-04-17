"""Preset toolbar widget for saving/loading/deleting prompt presets."""

from datetime import datetime

from PyQt6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QInputDialog,
    QMessageBox,
    QPushButton,
    QWidget,
)
from PyQt6.QtCore import pyqtSignal
from aqt.qt import QSettings

from ..core.preset_manager import PresetManager
from ..core.settings import SettingsNames
from .styles import SPACING_SM

_NO_PRESET = "(No preset)"


class PresetBar(QWidget):
    """A toolbar with a preset dropdown and Save/Delete/Export/Import buttons."""

    preset_loaded = pyqtSignal(dict)

    def __init__(self, app_settings: QSettings = None, parent=None):
        super().__init__(parent)
        self._app_settings = app_settings
        self._loaded_snapshot = None  # snapshot of preset values when loaded
        self._dirty = False
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_SM)

        self.combo = QComboBox()
        self.combo.setMinimumWidth(200)
        last_preset = ""
        if self._app_settings:
            last_preset = self._app_settings.value(
                SettingsNames.LAST_PRESET_NAME, defaultValue="", type=str
            )
        self._refresh_list(select_name=last_preset)
        self.combo.currentIndexChanged.connect(self._on_selection_changed)
        layout.addWidget(self.combo)

        save_btn = QPushButton("Save Preset")
        save_btn.clicked.connect(self._on_save)
        layout.addWidget(save_btn)

        delete_btn = QPushButton("Delete")
        delete_btn.setProperty("cssClass", "danger")
        delete_btn.clicked.connect(self._on_delete)
        layout.addWidget(delete_btn)

        export_btn = QPushButton("Export")
        export_btn.clicked.connect(self._on_export)
        layout.addWidget(export_btn)

        import_btn = QPushButton("Import")
        import_btn.clicked.connect(self._on_import)
        layout.addWidget(import_btn)

        layout.addStretch()

        # Callable set by the dialog to provide current form values
        self.get_current_values = None

    def _refresh_list(self, select_name: str = ""):
        """Reload the combo from stored presets."""
        self.combo.blockSignals(True)
        self.combo.clear()
        self.combo.addItem(_NO_PRESET)
        for name in PresetManager.list_presets():
            self.combo.addItem(name)
        if select_name:
            idx = self.combo.findText(select_name)
            if idx >= 0:
                self.combo.setCurrentIndex(idx)
        self.combo.blockSignals(False)

    def _on_selection_changed(self):
        name = self.combo.currentText()
        # Strip dirty marker for comparison
        clean_name = name.rstrip(" *")

        if clean_name == _NO_PRESET or name == _NO_PRESET:
            self._save_last_preset("")
            self._loaded_snapshot = None
            self._dirty = False
            return

        # Warn about unsaved changes before switching
        if self._dirty and self._loaded_snapshot:
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                "You have unsaved changes to the current preset. "
                "Switch anyway and discard changes?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply != QMessageBox.StandardButton.Yes:
                # Revert combo to previous preset (block signals to avoid recursion)
                self.combo.blockSignals(True)
                old_name = self._loaded_snapshot.get("_name", "")
                idx = self.combo.findText(old_name)
                if idx < 0:
                    idx = self.combo.findText(old_name + " *")
                if idx >= 0:
                    self.combo.setCurrentIndex(idx)
                self.combo.blockSignals(False)
                return

        self._save_last_preset(clean_name)
        preset = PresetManager.load_preset(clean_name)
        if preset:
            self._loaded_snapshot = dict(preset)
            self._loaded_snapshot["_name"] = clean_name
            self._dirty = False
            self._update_combo_label()
            self.preset_loaded.emit(preset)

    def mark_dirty(self):
        """Called by the dialog when any preset-tracked field changes."""
        if self._loaded_snapshot is None:
            return  # No preset active, nothing to track
        if not self._dirty:
            self._dirty = True
            self._update_combo_label()

    def is_dirty(self) -> bool:
        return self._dirty

    def active_preset_name(self) -> str | None:
        """Returns the clean name of the active preset, or None."""
        if self._loaded_snapshot is None:
            return None
        return self._loaded_snapshot.get("_name")

    def mark_clean(self):
        """Mark the current preset as saved/clean."""
        self._dirty = False
        self._update_combo_label()

    def save_active_preset(self, values: dict):
        """Silently save the active preset with updated values."""
        name = self.active_preset_name()
        if not name:
            return
        PresetManager.save_preset(
            name,
            system_prompt=values.get("system_prompt", ""),
            user_prompt=values.get("user_prompt", ""),
            response_keys=values.get("response_keys", []),
            destination_fields=values.get("destination_fields", []),
        )
        self._loaded_snapshot = {
            "system_prompt": values.get("system_prompt", ""),
            "user_prompt": values.get("user_prompt", ""),
            "response_keys": values.get("response_keys", []),
            "destination_field": values.get("destination_fields", []),
            "_name": name,
        }
        self._dirty = False
        self._update_combo_label()

    def _update_combo_label(self):
        """Add or remove the dirty '*' marker on the current combo item."""
        idx = self.combo.currentIndex()
        if idx <= 0:
            return
        name = self.combo.itemText(idx).rstrip(" *")
        display = f"{name} *" if self._dirty else name
        self.combo.blockSignals(True)
        self.combo.setItemText(idx, display)
        self.combo.blockSignals(False)

    def _save_last_preset(self, name: str):
        if self._app_settings:
            self._app_settings.setValue(SettingsNames.LAST_PRESET_NAME, name)

    def _on_save(self):
        if not self.get_current_values:
            return

        current_name = self.combo.currentText().rstrip(" *")
        default_name = "" if current_name == _NO_PRESET else current_name

        name, ok = QInputDialog.getText(
            self, "Save Preset", "Preset name:", text=default_name
        )
        if not ok or not name.strip():
            return
        name = name.strip()

        # Check overwrite
        if name in PresetManager.list_presets():
            reply = QMessageBox.question(
                self,
                "Overwrite Preset",
                f'Preset "{name}" already exists. Overwrite?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply != QMessageBox.StandardButton.Yes:
                return

        values = self.get_current_values()
        PresetManager.save_preset(
            name,
            system_prompt=values["system_prompt"],
            user_prompt=values["user_prompt"],
            response_keys=values["response_keys"],
            destination_fields=values["destination_fields"],
        )
        self._loaded_snapshot = dict(values)
        self._loaded_snapshot["_name"] = name
        self._dirty = False
        self._refresh_list(select_name=name)

    def _on_delete(self):
        name = self.combo.currentText()
        if name == _NO_PRESET:
            return
        reply = QMessageBox.question(
            self,
            "Delete Preset",
            f'Delete preset "{name}"?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            PresetManager.delete_preset(name)
            self._loaded_snapshot = None
            self._dirty = False
            self._refresh_list()

    def _on_export(self):
        current = self.combo.currentText().rstrip(" *")
        if current and current != _NO_PRESET:
            safe_name = current.replace(" ", "_")
        else:
            safe_name = "all_presets"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"{safe_name}_preset_{timestamp}.json"
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Presets", default_name,
            "JSON Files (*.json)"
        )
        if not file_path:
            return
        try:
            PresetManager.export_presets(file_path)
            QMessageBox.information(
                self, "Export Complete",
                f"Presets exported to {file_path}"
            )
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", str(e))

    def _on_import(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Presets", "",
            "JSON Files (*.json)"
        )
        if not file_path:
            return
        try:
            imported = PresetManager.import_presets(file_path)
            self._refresh_list()
            QMessageBox.information(
                self, "Import Complete",
                f"Imported {len(imported)} preset(s): {', '.join(imported)}"
            )
        except Exception as e:
            QMessageBox.critical(self, "Import Failed", str(e))
