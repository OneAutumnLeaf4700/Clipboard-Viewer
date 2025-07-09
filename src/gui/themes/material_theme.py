"""
Material Design Theme System for Clipboard Viewer
Provides modern styling and color schemes for the application.
"""

from PyQt6.QtGui import QColor, QPalette, QFont, QFontDatabase
from PyQt6.QtCore import Qt
import os
import sys

def detect_system_theme():
    """Detect if the system is using dark or light theme"""
    try:
        if sys.platform == "win32":
            import winreg
            registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
            key = winreg.OpenKey(registry, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize")
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            return "light" if value == 1 else "dark"
        else:
            # Default to light theme for non-Windows systems
            return "light"
    except Exception:
        # Default to light theme if detection fails
        return "light"

class MaterialTheme:
    """Material Design theme colors and styles"""
    
    # Primary Colors (Better light theme colors)
    PRIMARY = "#1976d2"
    PRIMARY_VARIANT = "#1565c0"
    SECONDARY = "#f57c00"
    SECONDARY_VARIANT = "#ef6c00"
    
    # Surface Colors
    SURFACE = "#ffffff"
    SURFACE_VARIANT = "#f5f5f5"
    BACKGROUND = "#fafafa"
    PREVIEW_SURFACE = "#f0f4f8"  # Slightly different color for preview area
    
    # Text Colors
    ON_PRIMARY = "#ffffff"
    ON_SECONDARY = "#ffffff"
    ON_SURFACE = "#212121"
    ON_BACKGROUND = "#212121"
    
    # State Colors
    ERROR = "#d32f2f"
    WARNING = "#f57c00"
    SUCCESS = "#388e3c"
    INFO = "#1976d2"
    
    # Elevation/Shadow Colors
    SHADOW_LIGHT = "rgba(0, 0, 0, 0.1)"
    SHADOW_MEDIUM = "rgba(0, 0, 0, 0.2)"
    SHADOW_STRONG = "rgba(0, 0, 0, 0.3)"

class MaterialDarkTheme(MaterialTheme):
    """Dark variant of Material Design theme"""
    
    # Primary Colors (slightly adjusted for dark theme)
    PRIMARY = "#90caf9"
    PRIMARY_VARIANT = "#42a5f5"
    SECONDARY = "#ffb74d"
    SECONDARY_VARIANT = "#ffa726"
    
    # Surface Colors
    SURFACE = "#1e1e1e"
    SURFACE_VARIANT = "#2d2d2d"
    BACKGROUND = "#121212"
    PREVIEW_SURFACE = "#252525"  # Slightly different color for preview area
    
    # Text Colors
    ON_PRIMARY = "#000000"
    ON_SECONDARY = "#000000"
    ON_SURFACE = "#ffffff"
    ON_BACKGROUND = "#ffffff"
    
    # State Colors
    ERROR = "#f48fb1"
    WARNING = "#ffb74d"
    SUCCESS = "#81c784"
    INFO = "#64b5f6"

def get_material_stylesheet(theme_type="light"):
    """Get the complete Material Design stylesheet"""
    
    theme = MaterialTheme() if theme_type == "light" else MaterialDarkTheme()
    
    return f"""
    /* Main Window */
    QMainWindow {{
        background-color: {theme.BACKGROUND};
        color: {theme.ON_BACKGROUND};
    }}
    
    /* Cards and Frames */
    QFrame {{
        background-color: {theme.SURFACE};
        border-radius: 12px;
        border: none;
    }}
    
    QFrame[card="true"] {{
        background-color: {theme.SURFACE};
        border-radius: 12px;
        border: none;
        padding: 16px;
        margin: 8px;
    }}
    
    /* Preview area with different background */
    QWidget[class="preview-area"] {{
        background-color: {theme.PREVIEW_SURFACE};
        border-radius: 16px;
        border: 2px solid {theme.SURFACE_VARIANT};
        padding: 20px;
        margin: 12px;
        box-shadow: 0 4px 12px {theme.SHADOW_MEDIUM};
    }}
    
    /* Preview content containers */
    QWidget[class="preview-content"] {{
        background-color: {theme.SURFACE};
        border-radius: 12px;
        border: 1px solid {theme.SURFACE_VARIANT};
        padding: 16px;
        margin: 8px 0;
    }}
    
    /* Preview header styling */
    QLabel[class="preview-header"] {{
        font-size: 18px;
        font-weight: 700;
        color: {theme.PRIMARY};
        margin-bottom: 16px;
        padding: 8px 0;
        border-bottom: 2px solid {theme.PRIMARY};
    }}
    
    /* Preview type labels */
    QLabel[class="preview-type"] {{
        font-size: 14px;
        font-weight: 600;
        color: {theme.SECONDARY};
        margin-bottom: 8px;
        padding: 4px 8px;
        background-color: rgba(245, 124, 0, 0.1);
        border-radius: 6px;
    }}
    
    /* Preview text content */
    QLabel[class="preview-text"] {{
        font-size: 14px;
        line-height: 1.5;
        color: {theme.ON_SURFACE};
        background-color: {theme.SURFACE};
        border: 1px solid {theme.SURFACE_VARIANT};
        border-radius: 8px;
        padding: 12px;
        margin: 8px 0;
    }}
    
    /* Preview button container */
    QWidget[class="preview-buttons"] {{
        background-color: transparent;
        border: none;
        padding: 16px 0 0 0;
        margin: 16px 0 0 0;
        border-top: 1px solid {theme.SURFACE_VARIANT};
    }}
    
    /* Preview image styling */
    QLabel[class="preview-image"] {{
        background-color: {theme.SURFACE};
        border: 2px solid {theme.SURFACE_VARIANT};
        border-radius: 8px;
        padding: 8px;
        margin: 8px 0;
    }}
    
    /* Preview file list styling */
    QListWidget[class="preview-files"] {{
        background-color: {theme.SURFACE};
        border: 1px solid {theme.SURFACE_VARIANT};
        border-radius: 8px;
        padding: 8px;
        margin: 8px 0;
    }}
    
    /* No preview message */
    QLabel[class="no-preview"] {{
        color: rgba(128, 128, 128, 0.8);
        font-style: italic;
        text-align: center;
        padding: 40px;
        background-color: {theme.SURFACE};
        border: 1px dashed {theme.SURFACE_VARIANT};
        border-radius: 8px;
        margin: 8px 0;
    }}
    
    /* Buttons */
    QPushButton {{
        background-color: {theme.PRIMARY};
        color: {theme.ON_PRIMARY};
        border: none;
        border-radius: 8px;
        padding: 8px 16px;
        font-weight: 600;
        font-size: 13px;
        font-family: 'Roboto', sans-serif;
        min-height: 20px;
    }}
    
    QPushButton:hover {{
        background-color: {theme.PRIMARY_VARIANT};
    }}
    
    QPushButton:pressed {{
        background-color: {theme.PRIMARY_VARIANT};
        padding: 9px 17px 7px 15px;
    }}
    
    QPushButton:disabled {{
        background-color: rgba(128, 128, 128, 0.3);
        color: rgba(128, 128, 128, 0.7);
    }}
    
    /* Small buttons (like Clear Filter) */
    QPushButton[type="small"] {{
        padding: 6px 12px;
        font-size: 12px;
        min-height: 16px;
    }}
    
    /* Secondary Buttons */
    QPushButton[type="secondary"] {{
        background-color: {theme.SECONDARY};
        color: {theme.ON_SECONDARY};
    }}
    
    QPushButton[type="secondary"]:hover {{
        background-color: {theme.SECONDARY_VARIANT};
    }}
    
    /* Outlined Buttons */
    QPushButton[type="outlined"] {{
        background-color: transparent;
        color: {theme.PRIMARY};
        border: 2px solid {theme.PRIMARY};
    }}
    
    QPushButton[type="outlined"]:hover {{
        background-color: rgba(98, 0, 238, 0.04);
    }}
    
    /* Text Buttons */
    QPushButton[type="text"] {{
        background-color: transparent;
        color: {theme.PRIMARY};
        border: none;
        padding: 8px 16px;
    }}
    
    QPushButton[type="text"]:hover {{
        background-color: rgba(98, 0, 238, 0.04);
    }}
    
    /* Input Fields */
    QLineEdit {{
        background-color: {theme.SURFACE};
        border: 2px solid transparent;
        border-radius: 8px;
        padding: 12px 16px;
        font-size: 14px;
        color: {theme.ON_SURFACE};
        selection-background-color: {theme.PRIMARY};
    }}
    
    QLineEdit:focus {{
        border-color: {theme.PRIMARY};
        outline: none;
    }}
    
    QLineEdit:hover {{
        border-color: rgba(98, 0, 238, 0.3);
    }}
    
    /* Combo Boxes */
    QComboBox {{
        background-color: {theme.SURFACE};
        border: 2px solid transparent;
        border-radius: 8px;
        padding: 12px 16px;
        font-size: 14px;
        color: {theme.ON_SURFACE};
        min-width: 120px;
    }}
    
    QComboBox:hover {{
        border-color: rgba(98, 0, 238, 0.3);
    }}
    
    QComboBox:focus {{
        border-color: {theme.PRIMARY};
    }}
    
    QComboBox::drop-down {{
        border: none;
        border-radius: 8px;
        width: 30px;
    }}
    
    QComboBox::down-arrow {{
        image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjQiIGhlaWdodD0iMjQiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTcgMTBMMTIgMTVMMTcgMTAiIHN0cm9rZT0iIzMzMzMzMyIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiLz4KPC9zdmc+);
        width: 16px;
        height: 16px;
    }}
    
    /* List Widget */
    QListWidget {{
        background-color: {theme.SURFACE};
        border: none;
        border-radius: 12px;
        padding: 8px;
        outline: none;
    }}
    
    QListWidget::item {{
        background-color: transparent;
        border: none;
        border-radius: 8px;
        padding: 12px 16px;
        margin: 2px 0;
        color: {theme.ON_SURFACE};
        min-height: 40px;
    }}
    
    QListWidget::item:selected {{
        background-color: {theme.PRIMARY};
        color: {theme.ON_PRIMARY};
    }}
    
    QListWidget::item:hover {{
        background-color: rgba(98, 0, 238, 0.08);
    }}
    
    QListWidget::item:selected:hover {{
        background-color: {theme.PRIMARY_VARIANT};
    }}
    
    /* Scroll Bars */
    QScrollBar:vertical {{
        background: {theme.SURFACE_VARIANT};
        width: 12px;
        border-radius: 6px;
        margin: 0;
    }}
    
    QScrollBar::handle:vertical {{
        background: rgba(98, 0, 238, 0.3);
        border-radius: 6px;
        min-height: 20px;
        margin: 2px;
    }}
    
    QScrollBar::handle:vertical:hover {{
        background: rgba(98, 0, 238, 0.5);
    }}
    
    QScrollBar::add-line:vertical,
    QScrollBar::sub-line:vertical {{
        border: none;
        background: none;
        height: 0;
    }}
    
    QScrollBar:horizontal {{
        background: {theme.SURFACE_VARIANT};
        height: 12px;
        border-radius: 6px;
        margin: 0;
    }}
    
    QScrollBar::handle:horizontal {{
        background: rgba(98, 0, 238, 0.3);
        border-radius: 6px;
        min-width: 20px;
        margin: 2px;
    }}
    
    QScrollBar::handle:horizontal:hover {{
        background: rgba(98, 0, 238, 0.5);
    }}
    
    QScrollBar::add-line:horizontal,
    QScrollBar::sub-line:horizontal {{
        border: none;
        background: none;
        width: 0;
    }}
    
    /* Labels */
    QLabel {{
        color: {theme.ON_BACKGROUND};
        font-family: 'Roboto', sans-serif;
    }}
    
    QLabel[type="heading"] {{
        font-size: 20px;
        font-weight: 600;
        color: {theme.ON_BACKGROUND};
        margin-bottom: 8px;
    }}
    
    QLabel[type="subheading"] {{
        font-size: 16px;
        font-weight: 500;
        color: {theme.ON_BACKGROUND};
        margin-bottom: 4px;
    }}
    
    QLabel[type="body"] {{
        font-size: 14px;
        color: {theme.ON_BACKGROUND};
    }}
    
    QLabel[type="caption"] {{
        font-size: 12px;
        color: rgba(0, 0, 0, 0.6);
    }}
    
    /* Toolbar */
    QToolBar {{
        background-color: {theme.SURFACE};
        border: none;
        border-radius: 12px;
        padding: 8px;
        margin: 4px;
        spacing: 8px;
    }}
    
    QToolBar::separator {{
        background-color: rgba(0, 0, 0, 0.12);
        width: 1px;
        margin: 8px 4px;
    }}
    
    /* Status Bar */
    QStatusBar {{
        background-color: {theme.SURFACE};
        border: none;
        border-radius: 8px;
        padding: 8px;
        margin: 4px;
        color: {theme.ON_SURFACE};
    }}
    
    /* Splitter */
    QSplitter::handle {{
        background-color: {theme.SURFACE_VARIANT};
        border-radius: 4px;
        margin: 4px;
    }}
    
    QSplitter::handle:horizontal {{
        width: 8px;
    }}
    
    QSplitter::handle:vertical {{
        height: 8px;
    }}
    
    QSplitter::handle:hover {{
        background-color: {theme.PRIMARY};
    }}
    
    /* Menu */
    QMenu {{
        background-color: {theme.SURFACE};
        border: none;
        border-radius: 8px;
        padding: 8px;
        color: {theme.ON_SURFACE};
    }}
    
    QMenu::item {{
        background-color: transparent;
        padding: 8px 16px;
        border-radius: 4px;
        margin: 2px;
    }}
    
    QMenu::item:selected {{
        background-color: {theme.PRIMARY};
        color: {theme.ON_PRIMARY};
    }}
    
    QMenu::separator {{
        height: 1px;
        background-color: rgba(0, 0, 0, 0.12);
        margin: 4px 8px;
    }}
    
    /* Checkboxes */
    QCheckBox {{
        color: {theme.ON_BACKGROUND};
        font-family: 'Roboto', sans-serif;
        spacing: 8px;
    }}
    
    QCheckBox::indicator {{
        width: 20px;
        height: 20px;
        border-radius: 4px;
        border: 2px solid rgba(0, 0, 0, 0.3);
        background-color: transparent;
    }}
    
    QCheckBox::indicator:hover {{
        border-color: {theme.PRIMARY};
    }}
    
    QCheckBox::indicator:checked {{
        background-color: {theme.PRIMARY};
        border-color: {theme.PRIMARY};
        image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEzLjUgNC41TDYgMTJMNC41IDEwLjUiIHN0cm9rZT0id2hpdGUiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIi8+Cjwvc3ZnPg==);
    }}
    
    /* Tab Widget */
    QTabWidget::pane {{
        border: none;
        background-color: {theme.SURFACE};
        border-radius: 12px;
        padding: 16px;
    }}
    
    QTabBar::tab {{
        background-color: transparent;
        color: {theme.ON_SURFACE};
        padding: 12px 24px;
        margin: 0 4px;
        border-radius: 8px;
        font-weight: 500;
    }}
    
    QTabBar::tab:selected {{
        background-color: {theme.PRIMARY};
        color: {theme.ON_PRIMARY};
    }}
    
    QTabBar::tab:hover {{
        background-color: rgba(98, 0, 238, 0.08);
    }}
    
    QTabBar::tab:selected:hover {{
        background-color: {theme.PRIMARY_VARIANT};
    }}
    
    /* Floating Action Button */
    QPushButton[type="fab"] {{
        background-color: {theme.PRIMARY};
        color: {theme.ON_PRIMARY};
        border: none;
        border-radius: 28px;
        padding: 0;
        width: 56px;
        height: 56px;
        font-size: 24px;
        font-weight: normal;
    }}
    
    QPushButton[type="fab"]:hover {{
        background-color: {theme.PRIMARY_VARIANT};
    }}
    
    QPushButton[type="fab"]:pressed {{
        background-color: {theme.PRIMARY_VARIANT};
        width: 54px;
        height: 54px;
    }}
    """

def setup_material_fonts():
    """Setup Material Design fonts"""
    
    # Try to add Roboto font files if available
    base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    fonts_path = os.path.join(base_path, "assets", "fonts")
    
    roboto_regular = os.path.join(fonts_path, "Roboto-Regular.ttf")
    roboto_bold = os.path.join(fonts_path, "Roboto-Bold.ttf")
    roboto_medium = os.path.join(fonts_path, "Roboto-Medium.ttf")
    
    if os.path.exists(roboto_regular):
        QFontDatabase.addApplicationFont(roboto_regular)
    if os.path.exists(roboto_bold):
        QFontDatabase.addApplicationFont(roboto_bold)
    if os.path.exists(roboto_medium):
        QFontDatabase.addApplicationFont(roboto_medium)
    
    # Set default application font
    default_font = QFont("Roboto", 10)
    available_families = QFontDatabase.families()
    if "Roboto" not in available_families:
        # Fallback to system fonts
        default_font = QFont("Segoe UI", 10)
    
    return default_font

def apply_material_theme(widget, theme_type="light"):
    """Apply Material Design theme to a widget"""
    
    # Apply stylesheet to the widget
    stylesheet = get_material_stylesheet(theme_type)
    widget.setStyleSheet(stylesheet)
    
    # Setup palette for better integration
    palette = QPalette()
    theme = MaterialTheme() if theme_type == "light" else MaterialDarkTheme()
    
    palette.setColor(QPalette.ColorRole.Window, QColor(theme.BACKGROUND))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(theme.ON_BACKGROUND))
    palette.setColor(QPalette.ColorRole.Base, QColor(theme.SURFACE))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(theme.SURFACE_VARIANT))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(theme.SURFACE))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor(theme.ON_SURFACE))
    palette.setColor(QPalette.ColorRole.Text, QColor(theme.ON_SURFACE))
    palette.setColor(QPalette.ColorRole.Button, QColor(theme.PRIMARY))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(theme.ON_PRIMARY))
    palette.setColor(QPalette.ColorRole.BrightText, QColor(theme.ON_PRIMARY))
    palette.setColor(QPalette.ColorRole.Link, QColor(theme.PRIMARY))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(theme.PRIMARY))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(theme.ON_PRIMARY))
    
    widget.setPalette(palette)

def apply_material_theme_to_app(app, theme_type="light"):
    """Apply Material Design theme to the entire application"""
    
    # Setup fonts
    default_font = setup_material_fonts()
    app.setFont(default_font)
    
    # Apply stylesheet
    stylesheet = get_material_stylesheet(theme_type)
    app.setStyleSheet(stylesheet)
    
    # Setup palette for better integration
    palette = QPalette()
    theme = MaterialTheme() if theme_type == "light" else MaterialDarkTheme()
    
    palette.setColor(QPalette.ColorRole.Window, QColor(theme.BACKGROUND))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(theme.ON_BACKGROUND))
    palette.setColor(QPalette.ColorRole.Base, QColor(theme.SURFACE))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(theme.SURFACE_VARIANT))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(theme.SURFACE))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor(theme.ON_SURFACE))
    palette.setColor(QPalette.ColorRole.Text, QColor(theme.ON_SURFACE))
    palette.setColor(QPalette.ColorRole.Button, QColor(theme.PRIMARY))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(theme.ON_PRIMARY))
    palette.setColor(QPalette.ColorRole.BrightText, QColor(theme.ON_PRIMARY))
    palette.setColor(QPalette.ColorRole.Link, QColor(theme.PRIMARY))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(theme.PRIMARY))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(theme.ON_PRIMARY))
    
    app.setPalette(palette)
