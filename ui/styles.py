"""Centralized stylesheet and theme constants for the plugin UI."""

# Spacing & sizing constants (8px grid)
SPACING_XS = 2
SPACING_SM = 4
SPACING_MD = 8
SPACING_LG = 12
SPACING_XL = 16
SPACING_XXL = 24

SECTION_RADIUS = 6
INPUT_RADIUS = 4

# Colors
COLOR_PRIMARY = "#4a90d9"
COLOR_PRIMARY_HOVER = "#5ba0e9"
COLOR_PRIMARY_PRESSED = "#3a7ec7"
COLOR_DANGER = "#d94a4a"
COLOR_DANGER_HOVER = "#e95b5b"
COLOR_SUCCESS = "#4caf50"

COLOR_BG = "#2b2b2b"
COLOR_SURFACE = "#353535"
COLOR_SURFACE_HOVER = "#3e3e3e"
COLOR_BORDER = "#4a4a4a"
COLOR_BORDER_FOCUS = COLOR_PRIMARY
COLOR_INPUT_BG = "#2f2f2f"

COLOR_TEXT = "#e0e0e0"
COLOR_TEXT_SECONDARY = "#a0a0a0"
COLOR_TEXT_MUTED = "#808080"
COLOR_TEXT_ON_PRIMARY = "#ffffff"

# Font sizes
FONT_SIZE_SM = 11
FONT_SIZE_MD = 12
FONT_SIZE_LG = 13
FONT_SIZE_SECTION_TITLE = 13


APP_STYLESHEET = f"""
/* ── Global ───────────────────────────────────────── */
QMainWindow, QDialog {{
    background-color: {COLOR_BG};
    color: {COLOR_TEXT};
}}

QWidget {{
    color: {COLOR_TEXT};
    font-size: {FONT_SIZE_MD}px;
}}

/* ── Scroll area ──────────────────────────────────── */
QScrollArea {{
    border: none;
    background: transparent;
}}
QScrollArea > QWidget > QWidget {{
    background: transparent;
}}
QScrollBar:vertical {{
    background: {COLOR_SURFACE};
    width: 8px;
    border-radius: 4px;
}}
QScrollBar::handle:vertical {{
    background: {COLOR_BORDER};
    border-radius: 4px;
    min-height: 30px;
}}
QScrollBar::handle:vertical:hover {{
    background: {COLOR_TEXT_MUTED};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}

/* ── Group boxes (section cards) ──────────────────── */
QGroupBox {{
    background-color: {COLOR_SURFACE};
    border: 1px solid {COLOR_BORDER};
    border-radius: {SECTION_RADIUS}px;
    margin-top: {SPACING_LG}px;
    padding: {SPACING_LG}px;
    padding-top: {SPACING_XXL}px;
    font-weight: bold;
    font-size: {FONT_SIZE_SECTION_TITLE}px;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: {SPACING_XS}px {SPACING_MD}px;
    color: {COLOR_TEXT};
}}

/* ── Inputs ───────────────────────────────────────── */
QLineEdit, QTextEdit {{
    background-color: {COLOR_INPUT_BG};
    border: 1px solid {COLOR_BORDER};
    border-radius: {INPUT_RADIUS}px;
    padding: {SPACING_SM}px {SPACING_MD}px;
    color: {COLOR_TEXT};
    font-size: {FONT_SIZE_MD}px;
    selection-background-color: {COLOR_PRIMARY};
}}
QLineEdit:focus, QTextEdit:focus {{
    border-color: {COLOR_BORDER_FOCUS};
}}
QLineEdit:hover, QTextEdit:hover {{
    border-color: {COLOR_TEXT_MUTED};
}}

/* ── Dropdowns ────────────────────────────────────── */
QComboBox {{
    background-color: {COLOR_INPUT_BG};
    border: 1px solid {COLOR_BORDER};
    border-radius: {INPUT_RADIUS}px;
    padding: {SPACING_SM}px {SPACING_MD}px;
    color: {COLOR_TEXT};
    font-size: {FONT_SIZE_MD}px;
    min-height: 22px;
}}
QComboBox:hover {{
    border-color: {COLOR_TEXT_MUTED};
}}
QComboBox:focus {{
    border-color: {COLOR_BORDER_FOCUS};
}}
QComboBox::drop-down {{
    border: none;
    width: 24px;
}}
QComboBox QAbstractItemView {{
    background-color: {COLOR_SURFACE};
    border: 1px solid {COLOR_BORDER};
    color: {COLOR_TEXT};
    selection-background-color: {COLOR_PRIMARY};
}}

/* ── Buttons ──────────────────────────────────────── */
QPushButton {{
    background-color: {COLOR_SURFACE};
    border: 1px solid {COLOR_BORDER};
    border-radius: {INPUT_RADIUS}px;
    padding: {SPACING_SM}px {SPACING_LG}px;
    color: {COLOR_TEXT};
    font-size: {FONT_SIZE_MD}px;
    min-height: 24px;
}}
QPushButton:hover {{
    background-color: {COLOR_SURFACE_HOVER};
    border-color: {COLOR_TEXT_MUTED};
}}
QPushButton:pressed {{
    background-color: {COLOR_BORDER};
}}
QPushButton:disabled {{
    color: {COLOR_TEXT_MUTED};
    background-color: {COLOR_SURFACE};
    border-color: {COLOR_BORDER};
}}

/* Primary action buttons */
QPushButton[cssClass="primary"] {{
    background-color: {COLOR_PRIMARY};
    border-color: {COLOR_PRIMARY};
    color: {COLOR_TEXT_ON_PRIMARY};
    font-weight: bold;
}}
QPushButton[cssClass="primary"]:hover {{
    background-color: {COLOR_PRIMARY_HOVER};
    border-color: {COLOR_PRIMARY_HOVER};
}}
QPushButton[cssClass="primary"]:pressed {{
    background-color: {COLOR_PRIMARY_PRESSED};
}}

/* Danger buttons */
QPushButton[cssClass="danger"] {{
    border-color: {COLOR_DANGER};
    color: {COLOR_DANGER};
}}
QPushButton[cssClass="danger"]:hover {{
    background-color: {COLOR_DANGER};
    color: {COLOR_TEXT_ON_PRIMARY};
}}

/* ── Progress bar ─────────────────────────────────── */
QProgressBar {{
    background-color: {COLOR_INPUT_BG};
    border: 1px solid {COLOR_BORDER};
    border-radius: {INPUT_RADIUS}px;
    text-align: center;
    color: {COLOR_TEXT};
    min-height: 20px;
}}
QProgressBar::chunk {{
    background-color: {COLOR_PRIMARY};
    border-radius: {INPUT_RADIUS}px;
}}

/* ── Labels ───────────────────────────────────────── */
QLabel {{
    color: {COLOR_TEXT};
    background: transparent;
}}
QLabel[cssClass="section-title"] {{
    font-size: {FONT_SIZE_LG}px;
    font-weight: bold;
    color: {COLOR_TEXT};
    padding: 0px;
    margin: 0px;
}}
QLabel[cssClass="description"] {{
    color: {COLOR_TEXT_SECONDARY};
    font-size: {FONT_SIZE_SM}px;
}}
QLabel[cssClass="field-tag"] {{
    background-color: {COLOR_PRIMARY};
    color: {COLOR_TEXT_ON_PRIMARY};
    border-radius: 3px;
    padding: 2px 6px;
    font-size: {FONT_SIZE_SM}px;
}}
QLabel[cssClass="muted"] {{
    color: {COLOR_TEXT_MUTED};
    font-size: {FONT_SIZE_SM}px;
}}
QLabel[cssClass="status-info"] {{
    color: {COLOR_TEXT_SECONDARY};
    font-size: {FONT_SIZE_SM}px;
    font-style: italic;
}}
QLabel[cssClass="arrow"] {{
    color: {COLOR_TEXT_MUTED};
    font-size: 16px;
}}

/* ── Tab widget ───────────────────────────────────── */
QTabWidget::pane {{
    border: 1px solid {COLOR_BORDER};
    border-radius: {SECTION_RADIUS}px;
    background-color: {COLOR_SURFACE};
    top: -1px;
}}
QTabBar::tab {{
    background-color: {COLOR_BG};
    border: 1px solid {COLOR_BORDER};
    border-bottom: none;
    border-top-left-radius: {INPUT_RADIUS}px;
    border-top-right-radius: {INPUT_RADIUS}px;
    padding: {SPACING_SM}px {SPACING_LG}px;
    color: {COLOR_TEXT_SECONDARY};
    font-size: {FONT_SIZE_MD}px;
    min-width: 80px;
}}
QTabBar::tab:selected {{
    background-color: {COLOR_SURFACE};
    color: {COLOR_TEXT};
    font-weight: bold;
}}
QTabBar::tab:hover:!selected {{
    background-color: {COLOR_SURFACE_HOVER};
    color: {COLOR_TEXT};
}}

/* ── Dialog button box ────────────────────────────── */
QDialogButtonBox {{
    padding-top: {SPACING_MD}px;
}}
"""


def apply_stylesheet(widget):
    """Apply the global stylesheet to a top-level widget."""
    widget.setStyleSheet(APP_STYLESHEET)
