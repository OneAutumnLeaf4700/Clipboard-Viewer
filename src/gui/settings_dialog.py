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
        self.add_hotkeys_tab()
        self.add_storage_tab()
        
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
        """Add the general settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Startup settings
        startup_group = QGroupBox("Startup")
        startup_layout = QFormLayout()
        
        self.start_minimized = QCheckBox("Start minimized to system tray")
        startup_layout.addRow(self.start_minimized)
        
        self.auto_start = QCheckBox("Start with Windows")
        startup_layout.addRow(self.auto_start)
        
        startup_group.setLayout(startup_layout)
        layout.addWidget(startup_group)
        
        # Clipboard monitoring settings
        monitoring_group = QGroupBox("Clipboard Monitoring")
        monitoring_layout = QFormLayout()
        
        self.monitor_text = QCheckBox("Monitor text")
        self.monitor_text.setChecked(True)
        monitoring_layout.addRow(self.monitor_text)
        
        self.monitor_images = QCheckBox("Monitor images")
        self.monitor_images.setChecked(True)
        monitoring_layout.addRow(self.monitor_images)
        
        self.monitor_files = QCheckBox("Monitor files")
        self.monitor_files.setChecked(True)
        monitoring_layout.addRow(self.monitor_files)
        
        monitoring_group.setLayout(monitoring_layout)
        layout.addWidget(monitoring_group)
        
        layout.addStretch()
        self.tab_widget.addTab(tab, "General")
    
    def add_appearance_tab(self):
        """Add the appearance settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Theme settings
        theme_group = QGroupBox("Theme")
        theme_layout = QFormLayout()
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["System", "Light", "Dark"])
        theme_layout.addRow("Theme:", self.theme_combo)
        
        theme_group.setLayout(theme_layout)
        layout.addWidget(theme_group)
        
        # Window settings
        window_group = QGroupBox("Window")
        window_layout = QFormLayout()
        
        self.always_on_top = QCheckBox("Always on top")
        window_layout.addRow(self.always_on_top)
        
        self.maximize_on_show = QCheckBox("Maximize window when shown")
        window_layout.addRow(self.maximize_on_show)
        
        window_group.setLayout(window_layout)
        layout.addWidget(window_group)
        
        layout.addStretch()
        self.tab_widget.addTab(tab, "Appearance")
    
    def add_hotkeys_tab(self):
        """Add the hotkeys settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Hotkey settings
        hotkey_group = QGroupBox("Global Hotkeys")
        hotkey_layout = QFormLayout()
        
        self.toggle_hotkey = HotkeyLineEdit()
        hotkey_layout.addRow("Toggle Window:", self.toggle_hotkey)
        
        self.copy_last_hotkey = HotkeyLineEdit()
        hotkey_layout.addRow("Copy Last Item:", self.copy_last_hotkey)
        
        hotkey_group.setLayout(hotkey_layout)
        layout.addWidget(hotkey_group)
        
        layout.addStretch()
        self.tab_widget.addTab(tab, "Hotkeys")
    
    def add_storage_tab(self):
        """Add the storage settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # History settings
        history_group = QGroupBox("History")
        history_layout = QFormLayout()
        
        self.max_history = QSpinBox()
        self.max_history.setRange(100, 10000)
        self.max_history.setSingleStep(100)
        self.max_history.setValue(1000)
        history_layout.addRow("Maximum History Items:", self.max_history)
        
        self.auto_cleanup = QSpinBox()
        self.auto_cleanup.setRange(1, 365)
        self.auto_cleanup.setValue(30)
        history_layout.addRow("Auto-cleanup Days:", self.auto_cleanup)
        
        history_group.setLayout(history_layout)
        layout.addWidget(history_group)
        
        # Storage location
        storage_group = QGroupBox("Storage Location")
        storage_layout = QFormLayout()
        
        self.storage_path = QLineEdit()
        self.storage_path.setReadOnly(True)
        storage_layout.addRow("Database Path:", self.storage_path)
        
        storage_group.setLayout(storage_layout)
        layout.addWidget(storage_group)
        
        layout.addStretch()
        self.tab_widget.addTab(tab, "Storage")
    
    def load_settings(self):
        """Load settings from QSettings."""
        # General settings
        self.start_minimized.setChecked(self.settings.value("general/start_minimized", False, type=bool))
        self.auto_start.setChecked(self.settings.value("general/auto_start", False, type=bool))
        self.monitor_text.setChecked(self.settings.value("general/monitor_text", True, type=bool))
        self.monitor_images.setChecked(self.settings.value("general/monitor_images", True, type=bool))
        self.monitor_files.setChecked(self.settings.value("general/monitor_files", True, type=bool))
        
        # Appearance settings
        theme = self.settings.value("appearance/theme", "System")
        self.theme_combo.setCurrentText(theme)
        self.always_on_top.setChecked(self.settings.value("appearance/always_on_top", False, type=bool))
        self.maximize_on_show.setChecked(self.settings.value("appearance/maximize_on_show", False, type=bool))
        
        # Hotkey settings
        self.toggle_hotkey.setText(self.settings.value("hotkeys/toggle_window", "Ctrl+Shift+V"))
        self.copy_last_hotkey.setText(self.settings.value("hotkeys/copy_last", "Ctrl+Shift+C"))
        
        # Storage settings
        self.max_history.setValue(self.settings.value("storage/max_history", 1000, type=int))
        self.auto_cleanup.setValue(self.settings.value("storage/auto_cleanup_days", 30, type=int))
        self.storage_path.setText(self.settings.value("storage/db_path", "data/clipboard_history.db"))
    
    def save_settings(self):
        """Save settings and close dialog."""
        self.apply_settings()
        self.accept()
    
    def apply_settings(self):
        """Apply settings without closing dialog."""
        # General settings
        self.settings.setValue("general/start_minimized", self.start_minimized.isChecked())
        self.settings.setValue("general/auto_start", self.auto_start.isChecked())
        self.settings.setValue("general/monitor_text", self.monitor_text.isChecked())
        self.settings.setValue("general/monitor_images", self.monitor_images.isChecked())
        self.settings.setValue("general/monitor_files", self.monitor_files.isChecked())
        
        # Appearance settings
        self.settings.setValue("appearance/theme", self.theme_combo.currentText())
        self.settings.setValue("appearance/always_on_top", self.always_on_top.isChecked())
        self.settings.setValue("appearance/maximize_on_show", self.maximize_on_show.isChecked())
        
        # Hotkey settings
        self.settings.setValue("hotkeys/toggle_window", self.toggle_hotkey.text())
        self.settings.setValue("hotkeys/copy_last", self.copy_last_hotkey.text())
        
        # Storage settings
        self.settings.setValue("storage/max_history", self.max_history.value())
        self.settings.setValue("storage/auto_cleanup_days", self.auto_cleanup.value())
        self.settings.setValue("storage/db_path", self.storage_path.text())
        
        # Emit signal to notify main window of settings changes
        if self.parent():
            self.parent().settings_changed.emit()