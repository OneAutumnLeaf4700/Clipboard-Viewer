from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTabWidget,
                            QLabel, QPushButton, QSpinBox, QCheckBox, QComboBox,
                            QGroupBox, QFormLayout, QLineEdit, QWidget)
from PyQt6.QtCore import Qt, QSettings
from PyQt6.QtGui import QKeyEvent

class HotkeyLineEdit(QLineEdit):
    """Custom QLineEdit for capturing hotkey combinations."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setPlaceholderText("Press keys to set hotkey")
        self.current_hotkey = ""
    
    def keyPressEvent(self, event: QKeyEvent):
        """Handle key press events to capture hotkey combinations."""
        modifiers = []
        
        # Check for modifier keys
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            modifiers.append("Ctrl")
        if event.modifiers() & Qt.KeyboardModifier.AltModifier:
            modifiers.append("Alt")
        if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
            modifiers.append("Shift")
        if event.modifiers() & Qt.KeyboardModifier.MetaModifier:
            modifiers.append("Win")
        
        qt_key = event.key()
        key_name = None
        # Handle function keys
        if Qt.Key.Key_F1 <= qt_key <= Qt.Key.Key_F35:
            key_name = f"F{qt_key - Qt.Key.Key_F1 + 1}"
        # Handle arrows and other special keys
        elif qt_key == Qt.Key.Key_Left:
            key_name = "Left"
        elif qt_key == Qt.Key.Key_Right:
            key_name = "Right"
        elif qt_key == Qt.Key.Key_Up:
            key_name = "Up"
        elif qt_key == Qt.Key.Key_Down:
            key_name = "Down"
        elif qt_key == Qt.Key.Key_Delete:
            key_name = "Delete"
        elif qt_key == Qt.Key.Key_Insert:
            key_name = "Insert"
        elif qt_key == Qt.Key.Key_Home:
            key_name = "Home"
        elif qt_key == Qt.Key.Key_End:
            key_name = "End"
        elif qt_key == Qt.Key.Key_PageUp:
            key_name = "PageUp"
        elif qt_key == Qt.Key.Key_PageDown:
            key_name = "PageDown"
        else:
            # Printable keys
            try:
                if 0x20 <= qt_key <= 0x7E:
                    key_name = chr(qt_key).upper()
                else:
                    key_name = event.text().upper()
            except Exception:
                key_name = event.text().upper()
        
        # Combine modifiers and key
        if key_name and key_name not in ["Ctrl", "Alt", "Shift", "Win", ""]:
            modifiers.append(key_name)
            self.current_hotkey = "+".join(modifiers)
            self.setText(self.current_hotkey)
        
        event.accept()

class SettingsDialog(QDialog):
    """Dialog for managing application settings."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Window setup
        self.setWindowTitle("Settings")
        self.setMinimumSize(600, 400)
        
        # Initialize settings
        self.settings = QSettings()
        
        # Create main layout
        layout = QVBoxLayout(self)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Add tabs
        self.add_general_tab()
        self.add_appearance_tab()
        
        layout.addWidget(self.tab_widget)
        
        # Add buttons
        button_layout = QHBoxLayout()
        
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_settings)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        self.apply_button = QPushButton("Apply")
        self.apply_button.clicked.connect(self.apply_settings)
        
        button_layout.addStretch()
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.apply_button)
        
        layout.addLayout(button_layout)
        
        # Load current settings
        self.load_settings()
    
    def add_general_tab(self):
        """Add the general settings tab with a 'Start with Windows' option."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        # Startup section
        self.auto_start = QCheckBox("Start with Windows")
        layout.addWidget(self.auto_start)
        layout.addStretch()
        self.tab_widget.addTab(tab, "General")
    
    def add_appearance_tab(self):
        """Add the appearance settings tab (now blank for redesign)."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        # All widgets removed; blank tab for redesign
        layout.addStretch()
        self.tab_widget.addTab(tab, "Appearance")
    
    def load_settings(self):
        """Load settings from QSettings. (No settings to load; tabs are blank)"""
        pass
    
    def save_settings(self):
        """Save settings and close dialog."""
        self.apply_settings()
        self.accept()
    
    def apply_settings(self):
        """Apply settings without closing dialog. (No settings to apply; tabs are blank)"""
        # Emit signal to notify main window of settings changes
        if self.parent():
            self.parent().settings_changed.emit()