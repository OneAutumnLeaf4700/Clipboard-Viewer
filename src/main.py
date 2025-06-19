import sys
import os
import logging
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QSettings

# Import our modules
from gui.main_window import MainWindow
from clipboard_monitor import ClipboardMonitor, ClipboardItem
from history_manager import HistoryManager
from utils.system_tray import SystemTrayManager
from utils.hotkeys import HotkeyManager
from utils.clipboard_utils import get_clipboard_data

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join('data', 'clipboard_viewer.log')),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('ClipboardViewer')

# get_clipboard_data function moved to utils.clipboard_utils

def main():
    logger.info("Clipboard Viewer started.")
    
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    # Initialize QApplication
    app = QApplication(sys.argv)
    app.setApplicationName("Clipboard Viewer")
    app.setOrganizationName("ClipboardViewer")
    app.setOrganizationDomain("clipboardviewer.app")
    
    # Initialize settings
    settings = QSettings()
    
    # Initialize history manager
    history_manager = HistoryManager()
    
    # Initialize clipboard monitor
    clipboard_monitor = ClipboardMonitor()
    
    # Initialize main window
    main_window = MainWindow(history_manager, clipboard_monitor)
    
    # Initialize system tray
    system_tray = SystemTrayManager()
    
    # Initialize hotkey manager
    hotkey_manager = HotkeyManager()
    
    # Connect signals and slots
    clipboard_monitor.new_content.connect(history_manager.add_item)
    
    # Connect system tray signals
    system_tray.show_app_requested.connect(main_window.show)
    system_tray.hide_app_requested.connect(main_window.hide)
    system_tray.settings_requested.connect(main_window.show_settings)
    system_tray.clear_history_requested.connect(main_window.clear_history)
    system_tray.exit_app_requested.connect(app.quit)
    
    # Start monitoring clipboard
    clipboard_monitor.start_monitoring()
    
    # Show main window unless start minimized is enabled
    if not settings.value("general/start_minimized", False, type=bool):
        main_window.show()
    
    main_window.show()

    # Execute application
    sys.exit(app.exec())

if __name__ == "__main__":
    main()