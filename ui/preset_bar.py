"""Preset toolbar widget for saving/loading/deleting prompt presets."""

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

from ..core.preset_manager import PresetManager
from .styles import SPACING_SM

_NO_PRESET = "(No preset)"


class PresetBar(QWidget):
    """A toolbar with a preset dropdown and Save/Delete/Export/Import buttons."""

    preset_loaded = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_SM)

        self.combo = QComboBox()
        self.combo.setMinimumWidth(200)
        self._refresh_list()
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
        if name == _NO_PRESET:
            return
        preset = PresetManager.load_preset(name)
        if preset:
            self.preset_loaded.emit(preset)

    def _on_save(self):
        if not self.get_current_values:
            return

        current_name = self.combo.currentText()
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
            self._refresh_list()

    def _on_export(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Presets", "anki_ai_presets.json",
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
