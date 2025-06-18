from PyQt6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import Qt, pyqtSignal, QObject

class SystemTrayManager(QObject):
    """Class to manage system tray icon and menu."""
    
    # Signals
    show_app_requested = pyqtSignal()  # Signal to show the main application window
    hide_app_requested = pyqtSignal()  # Signal to hide the main application window
    exit_app_requested = pyqtSignal()  # Signal to exit the application
    settings_requested = pyqtSignal()  # Signal to show settings dialog
    clear_history_requested = pyqtSignal()  # Signal to clear clipboard history
    
    def __init__(self, parent=None, icon_path=None):
        super().__init__(parent)
        
        # Create system tray icon
        self.tray_icon = QSystemTrayIcon(parent)
        
        # Set icon if provided
        if icon_path:
            self.set_icon(icon_path)
        
        # Create tray menu
        self.setup_tray_menu()
        
        # Connect signals
        self.tray_icon.activated.connect(self.on_tray_icon_activated)
    
    def setup_tray_menu(self):
        """Set up the system tray context menu."""
        tray_menu = QMenu()
        
        # Show action
        self.show_action = QAction("Show", self)
        self.show_action.triggered.connect(self.show_app_requested)
        tray_menu.addAction(self.show_action)
        
        # Hide action
        self.hide_action = QAction("Hide", self)
        self.hide_action.triggered.connect(self.hide_app_requested)
        tray_menu.addAction(self.hide_action)
        
        tray_menu.addSeparator()
        
        # Clear history action
        self.clear_history_action = QAction("Clear History", self)
        self.clear_history_action.triggered.connect(self.clear_history_requested)
        tray_menu.addAction(self.clear_history_action)
        
        # Settings action
        self.settings_action = QAction("Settings", self)
        self.settings_action.triggered.connect(self.settings_requested)
        tray_menu.addAction(self.settings_action)
        
        tray_menu.addSeparator()
        
        # Exit action
        self.exit_action = QAction("Exit", self)
        self.exit_action.triggered.connect(self.exit_app_requested)
        tray_menu.addAction(self.exit_action)
        
        # Set the menu
        self.tray_icon.setContextMenu(tray_menu)
    
    def set_icon(self, icon_path):
        """Set the system tray icon."""
        self.tray_icon.setIcon(QIcon(icon_path))
    
    def show(self):
        """Show the system tray icon."""
        self.tray_icon.show()
    
    def hide(self):
        """Hide the system tray icon."""
        self.tray_icon.hide()
    
    def show_message(self, title, message, icon=QSystemTrayIcon.MessageIcon.Information, duration=5000):
        """Show a notification message from the system tray."""
        self.tray_icon.showMessage(title, message, icon, duration)
    
    def on_tray_icon_activated(self, reason):
        """Handle tray icon activation."""
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            # Single click - toggle visibility
            if self.parent() and self.parent().isVisible():
                self.hide_app_requested.emit()
            else:
                self.show_app_requested.emit()
        elif reason == QSystemTrayIcon.ActivationReason.MiddleClick:
            # Middle click - show settings
            self.settings_requested.emit()
    
    def update_menu_state(self, app_visible):
        """Update menu actions based on application visibility."""
        self.show_action.setEnabled(not app_visible)
        self.hide_action.setEnabled(app_visible)