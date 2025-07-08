import sys
import os
from datetime import datetime
from PyQt6.QtWidgets import (QMainWindow, QApplication, QSplitter, QListWidget, 
                            QListWidgetItem, QVBoxLayout, QHBoxLayout, QWidget, 
                            QLabel, QPushButton, QMenu, QSystemTrayIcon, 
                            QMessageBox, QFrame, QToolBar, QStatusBar, QFileDialog, QDialog)
from PyQt6.QtGui import QIcon, QAction, QPixmap, QFont, QCursor
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QTimer, QSettings

# Import the clipboard data retrieval function
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.clipboard_utils import get_clipboard_data
from gui.preview_widget import PreviewWidget
from utils.hotkeys import HotkeyManager

class ClipboardListItem(QListWidgetItem):
    """Custom list widget item to store clipboard data and its type."""
    
    def __init__(self, data_type, content, timestamp=None):
        super().__init__()
        self.data_type = data_type
        self.content = content
        self.timestamp = timestamp or datetime.now()
        
        # Set display text based on data type
        if data_type == "text":
            display_text = content[:50] + "..." if len(content) > 50 else content
            self.setText(f"{self.timestamp.strftime('%H:%M:%S')} - {display_text}")
            self.setIcon(QIcon("assets/icons/text_icon.svg"))  # Placeholder for actual icon path
        elif data_type == "image":
            self.setText(f"{self.timestamp.strftime('%H:%M:%S')} - [Image]")
            self.setIcon(QIcon("assets/icons/image_icon.svg"))  # Placeholder for actual icon path
        elif data_type == "files":
            file_count = len(content)
            file_text = f"{file_count} file{'s' if file_count > 1 else ''}"
            self.setText(f"{self.timestamp.strftime('%H:%M:%S')} - {file_text}")
            self.setIcon(QIcon("assets/icons/file_icon.svg"))  # Placeholder for actual icon path
        else:
            self.setText(f"{self.timestamp.strftime('%H:%M:%S')} - [Unknown format]")
            self.setIcon(QIcon("assets/icons/unknown_icon.svg"))  # Placeholder for actual icon path


class MainWindow(QMainWindow):
    """Main window for the Clipboard Viewer application."""
    
    # Signal emitted when settings are changed
    settings_changed = pyqtSignal()
    
    def __init__(self, history_manager, clipboard_monitor):
        super().__init__()
        
        # Window setup
        self.setWindowTitle("Clipboard Viewer")
        self.setMinimumSize(800, 600)
        
        # Store references to managers
        self.history_manager = history_manager
        self.clipboard_monitor = clipboard_monitor
        
        # Initialize clipboard history
        self.clipboard_history = []
        self.original_clipboard_history = []
        self.last_clipboard_content = None
        self.current_search_text = ""
        self.current_search_type = "All Types"
        
        # Initialize hotkey manager
        self.hotkey_manager = HotkeyManager()
        
        # Connect settings changed signal
        self.settings_changed.connect(self.update_hotkeys)
        self.settings_changed.connect(self.apply_theme_from_settings)
        
        # Create central widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # Create splitter for history and preview
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Create history list
        self.history_widget = QWidget()
        self.history_layout = QVBoxLayout(self.history_widget)
        
        self.history_header = QLabel("Clipboard History")
        self.history_header.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        
        # Add enhanced search bar
        self.search_layout = QHBoxLayout()
        from PyQt6.QtWidgets import QLineEdit, QComboBox, QDateEdit
        from PyQt6.QtCore import QDate
        
        # Search input with improved styling
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search clipboard history...")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.textChanged.connect(self.on_search_text_changed)
        
        # Search type filter
        self.search_type_filter = QComboBox()
        self.search_type_filter.addItems(["All Types", "Text", "Images", "Files"])
        self.search_type_filter.currentTextChanged.connect(self.on_search_filter_changed)
        self.search_type_filter.setToolTip("Filter by content type")
        
        # Search debounce timer
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.perform_search)
        
        self.search_layout.addWidget(self.search_input)
        self.search_layout.addWidget(self.search_type_filter)
        
        self.history_list = QListWidget()
        self.history_list.setAlternatingRowColors(True)
        self.history_list.currentItemChanged.connect(self.on_item_selected)
        self.history_list.itemDoubleClicked.connect(self.copy_selected_to_clipboard)
        
        self.history_layout.addWidget(self.history_header)
        self.history_layout.addLayout(self.search_layout)
        self.history_layout.addWidget(self.history_list)
        
        # Create preview widget
        self.preview_widget = PreviewWidget()
        self.preview_widget.copy_button.clicked.connect(self.copy_selected_to_clipboard)
        self.preview_widget.save_button.clicked.connect(self.save_selected_item)
        
        # Add widgets to splitter
        self.splitter.addWidget(self.history_widget)
        self.splitter.addWidget(self.preview_widget)
        self.splitter.setSizes([300, 500])  # Initial sizes
        
        # Add splitter to main layout
        self.main_layout.addWidget(self.splitter)
        
        # Create toolbar
        self.create_toolbar()
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
        # Setup system tray
        self.setup_system_tray()
        
        # Connect clipboard monitor signals
        self.clipboard_monitor.new_content.connect(self.on_new_clipboard_content)
        
        # Load initial history
        self.load_history()
    
    def create_toolbar(self):
        """Create the application toolbar."""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setIconSize(QSize(16, 16))
        self.addToolBar(toolbar)
        
        # Clear history action
        clear_action = QAction("Clear History", self)
        clear_action.triggered.connect(self.clear_history)
        toolbar.addAction(clear_action)
        
        toolbar.addSeparator()
        
        # Settings action (placeholder)
        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self.show_settings)
        toolbar.addAction(settings_action)
    
    def setup_system_tray(self):
        """Setup the system tray icon and menu."""
        # This is a placeholder - actual implementation would need proper icons
        self.tray_icon = QSystemTrayIcon(self)
        tray_menu = QMenu()
        
        show_action = QAction("Show", self)
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)
        
        hide_action = QAction("Hide", self)
        hide_action.triggered.connect(self.hide)
        tray_menu.addAction(hide_action)
        
        tray_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(QApplication.quit)
        tray_menu.addAction(exit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.tray_icon_activated)
        
        # Placeholder icon - replace with actual icon
        # self.tray_icon.setIcon(QIcon("assets/icons/app_icon.svg"))
        # self.tray_icon.show()
    
    def tray_icon_activated(self, reason):
        """Handle tray icon activation."""
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            if self.isVisible():
                self.hide()
            else:
                self.show()
                self.activateWindow()
    
    def check_clipboard(self):
        """Check for clipboard changes and update history."""
        # This method is now handled by the clipboard_monitor and history_manager
        # We'll keep it for compatibility but it's essentially a no-op
        pass
        
    def load_history(self):
        """Load clipboard history from the history manager."""
        # Clear current history list
        self.history_list.clear()
        self.clipboard_history.clear()
        
        # Get history items from history manager
        items = self.history_manager.get_all_items(limit=100)  # Get last 100 items
        
        # Add items to history list
        for item in items:
            # Create list item
            list_item = ClipboardListItem(item.data_type, item.content, item.timestamp)
            
            # Add to history list
            self.history_list.addItem(list_item)
            self.clipboard_history.append(list_item)
        
        # Store original items for search filtering
        self.original_clipboard_history = self.clipboard_history.copy()
        
        # Update status
        self.status_bar.showMessage(f"Loaded {len(items)} history items")
    
    def on_new_clipboard_content(self, item):
        """Handle new clipboard content from the clipboard monitor."""
        # Create new history item
        new_item = ClipboardListItem(item.data_type, item.content, item.timestamp)
        
        # Check if search is active
        search_text = self.search_input.text()
        if search_text and item.data_type == "text" and search_text.lower() in str(item.content).lower():
            # If search is active and the new item matches the search, add it to the filtered list
            self.history_list.insertItem(0, new_item)  # Add at the top
            self.clipboard_history.insert(0, new_item)
        elif not search_text:
            # If no search is active, add to the visible list
            self.history_list.insertItem(0, new_item)  # Add at the top
            self.clipboard_history.insert(0, new_item)
        
        # Always add to the original list
        self.original_clipboard_history.insert(0, new_item)
        
        # Update status
        self.status_bar.showMessage(f"New clipboard content: {item.data_type}")
    
    def on_item_selected(self, current, previous):
        """Handle selection of an item in the history list."""
        if current:
            self.preview_widget.show_preview(current)
    
    def copy_selected_to_clipboard(self):
        """Copy the selected item back to the clipboard."""
        current_item = self.history_list.currentItem()
        if not current_item:
            return
            
        # Copy the item back to clipboard based on its type
        if current_item.data_type == "text":
            clipboard = QApplication.clipboard()
            clipboard.setText(current_item.content)
        elif current_item.data_type == "image" and current_item.content:
            # For images, we'd need to convert PIL Image to QImage
            # This is a simplified version
            clipboard = QApplication.clipboard()
            temp_path = "temp_clipboard.png"
            current_item.content.save(temp_path)
            clipboard.setImage(QPixmap(temp_path).toImage())
            if os.path.exists(temp_path):
                os.remove(temp_path)
        elif current_item.data_type == "files":
            # For files, we'd need to use win32clipboard directly
            # This is a placeholder
            pass
        
        self.status_bar.showMessage(f"Copied item back to clipboard")
        # QMessageBox.information(self, "Clipboard", "Item copied to clipboard")
    
    def save_selected_item(self):
        """Save the selected clipboard item to a file."""
        current_item = self.history_list.currentItem()
        if not current_item:
            return
            
        if current_item.data_type == "text":
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save Text", "", "Text Files (*.txt);;All Files (*)"
            )
            if file_path:
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(current_item.content)
                    self.status_bar.showMessage(f"Saved to {file_path}")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to save file: {e}")
                    
        elif current_item.data_type == "image" and current_item.content:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save Image", "", "PNG Files (*.png);;JPEG Files (*.jpg);;All Files (*)"
            )
            if file_path:
                try:
                    current_item.content.save(file_path)
                    self.status_bar.showMessage(f"Saved to {file_path}")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to save file: {e}")
    
    def clear_history(self):
        """Clear the clipboard history."""
        reply = QMessageBox.question(
            self, "Clear History", 
            "Are you sure you want to clear the clipboard history?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Clear history in the database
            keep_favorites = True  # Option to keep favorites
            self.history_manager.clear_history(keep_favorites)
            
            # Clear UI
            self.history_list.clear()
            self.clipboard_history.clear()
            self.original_clipboard_history.clear()
            self.preview_widget.clear_preview()
            
            # Reload history (to show favorites if kept)
            self.load_history()
            
            self.status_bar.showMessage("Clipboard history cleared")
    
    def show_settings(self):
        """Show the settings dialog and re-apply theme if changed."""
        from gui.settings_dialog import SettingsDialog
        dialog = SettingsDialog(self)
        dialog.exec()
        self.apply_theme_from_settings()
    
    def apply_theme_from_settings(self):
        """Apply the selected theme from QSettings to the QApplication."""
        settings = QSettings()
        theme = settings.value("appearance/theme", "System")
        app = QApplication.instance()
        if theme == "Dark":
            app.setStyleSheet("""
                QWidget { background-color: #232629; color: #f0f0f0; }
                QLineEdit, QTextEdit, QPlainTextEdit, QComboBox, QListWidget, QSpinBox, QCheckBox, QPushButton {
                    background-color: #2c2f34; color: #f0f0f0; border: 1px solid #444; }
                QMenuBar, QMenu { background-color: #232629; color: #f0f0f0; }
                QToolBar, QStatusBar { background-color: #232629; color: #f0f0f0; }
                QTabWidget::pane { background: #232629; }
            """)
        elif theme == "Light":
            app.setStyleSheet("""
                QWidget { background-color: #f6f6f6; color: #232629; }
                QLineEdit, QTextEdit, QPlainTextEdit, QComboBox, QListWidget, QSpinBox, QCheckBox, QPushButton {
                    background-color: #ffffff; color: #232629; border: 1px solid #ccc; }
                QMenuBar, QMenu { background-color: #f6f6f6; color: #232629; }
                QToolBar, QStatusBar { background-color: #f6f6f6; color: #232629; }
                QTabWidget::pane { background: #f6f6f6; }
            """)
        else:
            app.setStyleSheet("")
    
    def on_search_text_changed(self, text):
        """Handle search text changes with debounced search."""
        self.current_search_text = text
        self.search_timer.stop()
        
        if text.strip():
            # Debounce search - wait 300ms after user stops typing
            self.search_timer.start(300)
        else:
            self.load_history()  # Reload all history items immediately if search is cleared
    
    def on_search_filter_changed(self, filter_type):
        """Handle search filter changes."""
        self.current_search_type = filter_type
        self.perform_search()
    
    def perform_search(self):
        """Perform the actual search with current parameters."""
        if self.current_search_text.strip():
            self.filter_history_list(self.current_search_text, self.current_search_type)
        else:
            self.load_history()
    
    def clear_search(self):
        """Clear the search input and reload all history items."""
        self.search_input.clear()
        self.search_type_filter.setCurrentText("All Types")
        self.current_search_text = ""
        self.current_search_type = "All Types"
        self.load_history()
    
    def filter_history_list(self, search_text, filter_type="All Types"):
        """Filter the history list based on the search text and type filter."""
        # Clear current history list
        self.history_list.clear()
        self.clipboard_history.clear()
        
        # Convert filter type to data type
        data_type_filter = None
        if filter_type == "Text":
            data_type_filter = "text"
        elif filter_type == "Images":
            data_type_filter = "image"
        elif filter_type == "Files":
            data_type_filter = "files"
        
        # Get filtered items from history manager
        items = self.history_manager.search_items(search_text, data_type_filter, limit=100)
        
        # Add items to history list
        for item in items:
            # Create list item
            list_item = ClipboardListItem(item.data_type, item.content, item.timestamp)
            
            # Add to history list
            self.history_list.addItem(list_item)
            self.clipboard_history.append(list_item)
        
        # Update status with more detailed information
        filter_text = f" ({filter_type.lower()})" if filter_type != "All Types" else ""
        self.status_bar.showMessage(f"Found {len(items)} items matching '{search_text}'{filter_text}")
    
    def closeEvent(self, event):
        """Handle window close event."""
        # Minimize to tray instead of closing
        if self.tray_icon.isVisible():
            QMessageBox.information(
                self, "Clipboard Viewer",
                "The application will continue running in the system tray. "
                "To exit, right-click the tray icon and select 'Exit'."
            )
            self.hide()
            event.ignore()
        else:
            event.accept()
    
    def update_hotkeys(self):
        """Update hotkeys based on settings."""
        # Unregister all existing hotkeys
        self.hotkey_manager.unregister_all_hotkeys()
        
        # Get hotkey settings
        settings = QSettings()
        settings.beginGroup("Hotkeys")
        
        # Register toggle window hotkey
        toggle_hotkey = settings.value("toggle_window", "Ctrl+Shift+V")
        self.hotkey_manager.register_hotkey("toggle_window", toggle_hotkey, self.toggle_window_visibility)
        
        # Register copy last item hotkey
        copy_last_hotkey = settings.value("copy_last_item", "Ctrl+Shift+C")
        self.hotkey_manager.register_hotkey("copy_last_item", copy_last_hotkey, self.copy_last_item)
        
        settings.endGroup()
    
    def toggle_window_visibility(self):
        """Toggle the window visibility."""
        if self.isVisible():
            self.hide()
        else:
            self.show()
            self.activateWindow()
    
    def copy_last_item(self):
        """Copy the most recent clipboard item back to the clipboard."""
        if self.history_list.count() > 0:
            # Get the first item (most recent)
            item = self.history_list.item(0)
            if item:
                self.copy_selected_to_clipboard(item)
                self.status_bar.showMessage("Last item copied to clipboard")