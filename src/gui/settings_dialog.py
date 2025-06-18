from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QCheckBox, QSpinBox, QComboBox,
                            QTabWidget, QWidget, QFormLayout, QLineEdit,
                            QGroupBox, QDialogButtonBox)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, QSettings

class SettingsDialog(QDialog):
    """Dialog for configuring application settings."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.resize(500, 400)
        
        # Initialize settings
        self.settings = QSettings("ClipboardViewer", "ClipboardViewer")
        
        self.setup_ui()
        self.load_settings()
        
    def setup_ui(self):
        """Set up the user interface components."""
        # Main layout
        self.layout = QVBoxLayout(self)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Create tabs
        self.general_tab = QWidget()
        self.history_tab = QWidget()
        self.appearance_tab = QWidget()
        self.hotkeys_tab = QWidget()
        
        # Set up each tab
        self.setup_general_tab()
        self.setup_history_tab()
        self.setup_appearance_tab()
        self.setup_hotkeys_tab()
        
        # Add tabs to tab widget
        self.tab_widget.addTab(self.general_tab, "General")
        self.tab_widget.addTab(self.history_tab, "History")
        self.tab_widget.addTab(self.appearance_tab, "Appearance")
        self.tab_widget.addTab(self.hotkeys_tab, "Hotkeys")
        
        # Dialog buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | 
                                         QDialogButtonBox.StandardButton.Cancel | 
                                         QDialogButtonBox.StandardButton.Apply)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.button_box.button(QDialogButtonBox.StandardButton.Apply).clicked.connect(self.apply_settings)
        
        # Add widgets to main layout
        self.layout.addWidget(self.tab_widget)
        self.layout.addWidget(self.button_box)
        
    def setup_general_tab(self):
        """Set up the general settings tab."""
        layout = QVBoxLayout(self.general_tab)
        
        # Startup options
        startup_group = QGroupBox("Startup Options")
        startup_layout = QVBoxLayout(startup_group)
        
        self.start_with_system = QCheckBox("Start with system")
        self.start_minimized = QCheckBox("Start minimized to system tray")
        
        startup_layout.addWidget(self.start_with_system)
        startup_layout.addWidget(self.start_minimized)
        
        # System tray options
        tray_group = QGroupBox("System Tray")
        tray_layout = QVBoxLayout(tray_group)
        
        self.minimize_to_tray = QCheckBox("Minimize to system tray when closed")
        self.show_notifications = QCheckBox("Show notifications for new clipboard items")
        
        tray_layout.addWidget(self.minimize_to_tray)
        tray_layout.addWidget(self.show_notifications)
        
        # Add groups to tab layout
        layout.addWidget(startup_group)
        layout.addWidget(tray_group)
        layout.addStretch()
        
    def setup_history_tab(self):
        """Set up the history settings tab."""
        layout = QVBoxLayout(self.history_tab)
        
        # History limits
        limits_group = QGroupBox("History Limits")
        limits_layout = QFormLayout(limits_group)
        
        self.max_history_items = QSpinBox()
        self.max_history_items.setRange(10, 10000)
        self.max_history_items.setSingleStep(10)
        
        self.auto_cleanup_days = QSpinBox()
        self.auto_cleanup_days.setRange(1, 365)
        self.auto_cleanup_days.setSingleStep(1)
        
        limits_layout.addRow("Maximum history items:", self.max_history_items)
        limits_layout.addRow("Auto-cleanup after (days):", self.auto_cleanup_days)
        
        # Content types
        types_group = QGroupBox("Content Types to Monitor")
        types_layout = QVBoxLayout(types_group)
        
        self.monitor_text = QCheckBox("Text")
        self.monitor_images = QCheckBox("Images")
        self.monitor_files = QCheckBox("Files")
        
        types_layout.addWidget(self.monitor_text)
        types_layout.addWidget(self.monitor_images)
        types_layout.addWidget(self.monitor_files)
        
        # Privacy
        privacy_group = QGroupBox("Privacy")
        privacy_layout = QVBoxLayout(privacy_group)
        
        self.exclude_sensitive = QCheckBox("Exclude sensitive applications (password managers, etc.)")
        self.encrypt_history = QCheckBox("Encrypt clipboard history")
        
        privacy_layout.addWidget(self.exclude_sensitive)
        privacy_layout.addWidget(self.encrypt_history)
        
        # Add groups to tab layout
        layout.addWidget(limits_group)
        layout.addWidget(types_group)
        layout.addWidget(privacy_group)
        layout.addStretch()
        
    def setup_appearance_tab(self):
        """Set up the appearance settings tab."""
        layout = QVBoxLayout(self.appearance_tab)
        
        # Theme settings
        theme_group = QGroupBox("Theme")
        theme_layout = QFormLayout(theme_group)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["System", "Light", "Dark"])
        
        theme_layout.addRow("Application theme:", self.theme_combo)
        
        # Font settings
        font_group = QGroupBox("Font")
        font_layout = QFormLayout(font_group)
        
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 24)
        self.font_size_spin.setSingleStep(1)
        
        font_layout.addRow("Font size:", self.font_size_spin)
        
        # Add groups to tab layout
        layout.addWidget(theme_group)
        layout.addWidget(font_group)
        layout.addStretch()
        
    def setup_hotkeys_tab(self):
        """Set up the hotkeys settings tab."""
        layout = QVBoxLayout(self.hotkeys_tab)
        
        # Hotkey settings
        hotkeys_group = QGroupBox("Keyboard Shortcuts")
        hotkeys_layout = QFormLayout(hotkeys_group)
        
        self.show_app_hotkey = QLineEdit()
        self.show_app_hotkey.setPlaceholderText("Click to set hotkey")
        self.show_app_hotkey.setText("Ctrl+Shift+V")
        
        self.copy_last_hotkey = QLineEdit()
        self.copy_last_hotkey.setPlaceholderText("Click to set hotkey")
        self.copy_last_hotkey.setText("Ctrl+Shift+C")
        
        hotkeys_layout.addRow("Show application:", self.show_app_hotkey)
        hotkeys_layout.addRow("Copy last item:", self.copy_last_hotkey)
        
        # Add groups to tab layout
        layout.addWidget(hotkeys_group)
        layout.addStretch()
        
    def load_settings(self):
        """Load settings from QSettings."""
        # General tab
        self.start_with_system.setChecked(self.settings.value("general/start_with_system", False, type=bool))
        self.start_minimized.setChecked(self.settings.value("general/start_minimized", False, type=bool))
        self.minimize_to_tray.setChecked(self.settings.value("general/minimize_to_tray", True, type=bool))
        self.show_notifications.setChecked(self.settings.value("general/show_notifications", True, type=bool))
        
        # History tab
        self.max_history_items.setValue(self.settings.value("history/max_items", 1000, type=int))
        self.auto_cleanup_days.setValue(self.settings.value("history/auto_cleanup_days", 30, type=int))
        self.monitor_text.setChecked(self.settings.value("history/monitor_text", True, type=bool))
        self.monitor_images.setChecked(self.settings.value("history/monitor_images", True, type=bool))
        self.monitor_files.setChecked(self.settings.value("history/monitor_files", True, type=bool))
        self.exclude_sensitive.setChecked(self.settings.value("history/exclude_sensitive", True, type=bool))
        self.encrypt_history.setChecked(self.settings.value("history/encrypt_history", False, type=bool))
        
        # Appearance tab
        self.theme_combo.setCurrentText(self.settings.value("appearance/theme", "System", type=str))
        self.font_size_spin.setValue(self.settings.value("appearance/font_size", 10, type=int))
        
        # Hotkeys tab
        self.show_app_hotkey.setText(self.settings.value("hotkeys/show_app", "Ctrl+Shift+V", type=str))
        self.copy_last_hotkey.setText(self.settings.value("hotkeys/copy_last", "Ctrl+Shift+C", type=str))
        
    def save_settings(self):
        """Save settings to QSettings."""
        # General tab
        self.settings.setValue("general/start_with_system", self.start_with_system.isChecked())
        self.settings.setValue("general/start_minimized", self.start_minimized.isChecked())
        self.settings.setValue("general/minimize_to_tray", self.minimize_to_tray.isChecked())
        self.settings.setValue("general/show_notifications", self.show_notifications.isChecked())
        
        # History tab
        self.settings.setValue("history/max_items", self.max_history_items.value())
        self.settings.setValue("history/auto_cleanup_days", self.auto_cleanup_days.value())
        self.settings.setValue("history/monitor_text", self.monitor_text.isChecked())
        self.settings.setValue("history/monitor_images", self.monitor_images.isChecked())
        self.settings.setValue("history/monitor_files", self.monitor_files.isChecked())
        self.settings.setValue("history/exclude_sensitive", self.exclude_sensitive.isChecked())
        self.settings.setValue("history/encrypt_history", self.encrypt_history.isChecked())
        
        # Appearance tab
        self.settings.setValue("appearance/theme", self.theme_combo.currentText())
        self.settings.setValue("appearance/font_size", self.font_size_spin.value())
        
        # Hotkeys tab
        self.settings.setValue("hotkeys/show_app", self.show_app_hotkey.text())
        self.settings.setValue("hotkeys/copy_last", self.copy_last_hotkey.text())
        
        self.settings.sync()
        
    def apply_settings(self):
        """Apply the current settings."""
        self.save_settings()
        
    def accept(self):
        """Handle dialog acceptance."""
        self.save_settings()
        super().accept()