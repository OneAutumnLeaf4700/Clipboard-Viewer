import sys
import os
from datetime import datetime
from PyQt6.QtWidgets import (QMainWindow, QApplication, QSplitter, QListWidget, 
                            QListWidgetItem, QVBoxLayout, QHBoxLayout, QWidget, 
                            QLabel, QPushButton, QMenu, QSystemTrayIcon, 
                            QMessageBox, QFrame, QToolBar, QStatusBar, QFileDialog, QDialog, QSizePolicy)
from PyQt6.QtGui import QIcon, QAction, QPixmap, QFont, QCursor
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QTimer, QSettings

# Import the clipboard data retrieval function
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.clipboard_utils import get_clipboard_data
from gui.preview_widget import PreviewWidget
from utils.hotkeys import HotkeyManager
from utils.notification_manager import NotificationManager

# Import material theme
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from gui.themes.material_theme import apply_material_theme_to_app, get_material_stylesheet

class ClipboardListItem(QListWidgetItem):
    """Custom list widget item to store clipboard data and its type."""
    
    def __init__(self, data_type, content, timestamp=None):
        super().__init__()
        self.data_type = data_type
        self.content = content
        self.timestamp = timestamp or datetime.now()
        
        # Set display text based on data type with proper icon paths
        if data_type == "text":
            display_text = content[:50] + "..." if len(content) > 50 else content
            self.setText(f"{self.timestamp.strftime('%H:%M:%S')} - {display_text}")
            self.setIcon(QIcon(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "assets", "icons", "text_icon.svg")))
        elif data_type == "image":
            self.setText(f"{self.timestamp.strftime('%H:%M:%S')} - [Image]")
            self.setIcon(QIcon(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "assets", "icons", "image_icon.svg")))
        elif data_type == "files":
            file_count = len(content)
            file_text = f"{file_count} file{'s' if file_count > 1 else ''}"
            self.setText(f"{self.timestamp.strftime('%H:%M:%S')} - {file_text}")
            self.setIcon(QIcon(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "assets", "icons", "file_icon.svg")))
        else:
            self.setText(f"{self.timestamp.strftime('%H:%M:%S')} - [Unknown format]")
            self.setIcon(QIcon(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "assets", "icons", "unknown_icon.svg")))


class MainWindow(QMainWindow):
    """Main window for the Clipboard Viewer application."""
    
    # Signal emitted when settings are changed
    settings_changed = pyqtSignal()
    
    def __init__(self, history_manager, clipboard_monitor):
        super().__init__()
        
        # Window setup with responsive design and branding
        self.setWindowTitle("📋 Clipboard Viewer")
        self.setMinimumSize(800, 600)  # Increased default size for more spacious layout
        self.resize(1200, 800)  # Default size
        
        # Set application icon
        app_icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "assets", "icons", "app_icon.svg")
        if os.path.exists(app_icon_path):
            self.setWindowIcon(QIcon(app_icon_path))
        
        # Material Design theme will be applied later
        # Track window size for responsive adjustments
        self.last_window_size = self.size()
        
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
        
        # Initialize notification manager
        self.notification_manager = NotificationManager(self)
        
        # Connect settings changed signal
        self.settings_changed.connect(self.update_hotkeys)
        self.settings_changed.connect(self.apply_theme_from_settings)
        
        # Create central widget and layout with responsive design
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        # Responsive adjustments: set stretch factors
        self.main_layout.setStretch(0, 1)
        self.main_layout.setStretch(1, 2)

        # Create splitter for history and preview with responsive sizing
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setChildrenCollapsible(False)  # Avoid collapsing widgets
        
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
        
        # Search type filter with more options
        self.search_type_filter = QComboBox()
        self.search_type_filter.addItems([
            "All Types", 
            "Text", 
            "Images", 
            "Files", 
            "Favorites", 
            "Recent (24h)", 
            "This Week"
        ])
        self.search_type_filter.currentTextChanged.connect(self.on_search_filter_changed)
        self.search_type_filter.setToolTip("Filter by content type or time period\nKeyboard shortcuts: Ctrl+1-7")
        
        # Add keyboard shortcuts for filter selection
        from PyQt6.QtGui import QShortcut, QKeySequence
        for i in range(7):
            shortcut = QShortcut(QKeySequence(f"Ctrl+{i+1}"), self)
            shortcut.activated.connect(lambda idx=i: self.set_filter_by_index(idx))
        
        # Add a clear filter button
        self.clear_filter_button = QPushButton("Clear Filter")
        self.clear_filter_button.setProperty("type", "small")
        self.clear_filter_button.setToolTip("Clear all filters and show all items")
        self.clear_filter_button.clicked.connect(self.clear_all_filters)
        self.clear_filter_button.setMaximumWidth(100)
        
        # Search debounce timer
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.perform_search)
        
        self.search_layout.addWidget(self.search_input)
        self.search_layout.addWidget(self.search_type_filter)
        self.search_layout.addWidget(self.clear_filter_button)
        
        self.history_list = QListWidget()
        self.history_list.setAlternatingRowColors(True)
        self.history_list.currentItemChanged.connect(self.on_item_selected)
        self.history_list.itemDoubleClicked.connect(self.copy_selected_to_clipboard)
        
        # Add context menu to history list
        self.history_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.history_list.customContextMenuRequested.connect(self.show_history_context_menu)
        
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
        self.splitter.setSizes([1, 3])  # Use relative sizes for better responsiveness
        
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
        
        # Set up responsive layout adjustments
        self.adjustLayoutForWindowSize()
        
        # Apply Material Design theme to the entire application
        from PyQt6.QtWidgets import QApplication
        from gui.themes.material_theme import detect_system_theme
        app = QApplication.instance()
        system_theme = detect_system_theme()
        apply_material_theme_to_app(app, system_theme)
    
    def create_toolbar(self):
        """Create the application toolbar with proper icons and branding."""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setIconSize(QSize(20, 20))
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.addToolBar(toolbar)
        
        # Clear history action with icon
        clear_icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "assets", "icons", "clear_icon.svg")
        clear_action = QAction("🗑️ Clear History", self)
        if os.path.exists(clear_icon_path):
            clear_action.setIcon(QIcon(clear_icon_path))
        clear_action.setToolTip("Clear all clipboard history")
        clear_action.triggered.connect(self.clear_history)
        toolbar.addAction(clear_action)
        
        toolbar.addSeparator()
        
        # Settings action with icon
        settings_icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "assets", "icons", "settings_icon.svg")
        settings_action = QAction("⚙️ Settings", self)
        if os.path.exists(settings_icon_path):
            settings_action.setIcon(QIcon(settings_icon_path))
        settings_action.setToolTip("Open application settings")
        settings_action.triggered.connect(self.show_settings)
        toolbar.addAction(settings_action)
        
        # Add stretch to push items to the left
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        toolbar.addWidget(spacer)
        
        # Add branding label
        branding_label = QLabel("Clipboard Viewer v1.0")
        branding_label.setStyleSheet("color: #6C757D; font-size: 12px; margin-right: 10px;")
        toolbar.addWidget(branding_label)
    
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
        
        # Set system tray icon
        app_icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "assets", "icons", "app_icon.svg")
        if os.path.exists(app_icon_path):
            self.tray_icon.setIcon(QIcon(app_icon_path))
            self.tray_icon.show()
    
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
        
        # Update status with session statistics
        session_stats = self.notification_manager.get_session_summary()
        self.status_bar.showMessage(
            f"New {item.data_type} content | Session: {session_stats['total_items']} items "
            f"(📝 {session_stats['text_items']} | 🖼️ {session_stats['image_items']} | 📁 {session_stats['file_items']}) "
            f"| Duration: {session_stats['session_duration']}"
        )
        
        # Show notification for new clipboard content
        content_preview = ""
        if item.data_type == "text":
            content_preview = item.content[:50] + "..." if len(item.content) > 50 else item.content
        elif item.data_type == "image":
            content_preview = "Image captured"
        elif item.data_type == "files":
            file_count = len(item.content)
            content_preview = f"{file_count} file{'s' if file_count > 1 else ''} copied"
        else:
            content_preview = "Unknown content type"
        
        self.notification_manager.show_clipboard_notification(
            f"📋 New {item.data_type.title()} Copied",
            content_preview,
            "info"
        )
        
        # Also show enhanced toast notification with statistics
        self.notification_manager.show_toast_notification(
            f"📋 New {item.data_type.title()} Copied",
            content_preview,
            "info",
            item.data_type
        )
        
        # Also show system tray notification if enabled
        self.notification_manager.show_system_tray_notification(
            "Clipboard Viewer",
            f"New {item.data_type} content copied"
        )
    
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
        
        # Show notification for copied item
        self.notification_manager.show_clipboard_notification(
            "📋 Item Copied",
            "Item has been copied back to clipboard",
            "success"
        )
    
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
                    
                    # Show success notification
                    self.notification_manager.show_clipboard_notification(
                        "💾 File Saved",
                        f"Text saved to {os.path.basename(file_path)}",
                        "success"
                    )
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to save file: {e}")
                    
                    # Show error notification
                    self.notification_manager.show_clipboard_notification(
                        "❌ Save Failed",
                        f"Failed to save file: {str(e)}",
                        "error"
                    )
                    
        elif current_item.data_type == "image" and current_item.content:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save Image", "", "PNG Files (*.png);;JPEG Files (*.jpg);;All Files (*)"
            )
            if file_path:
                try:
                    current_item.content.save(file_path)
                    self.status_bar.showMessage(f"Saved to {file_path}")
                    
                    # Show success notification
                    self.notification_manager.show_clipboard_notification(
                        "💾 Image Saved",
                        f"Image saved to {os.path.basename(file_path)}",
                        "success"
                    )
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to save file: {e}")
                    
                    # Show error notification
                    self.notification_manager.show_clipboard_notification(
                        "❌ Save Failed",
                        f"Failed to save image: {str(e)}",
                        "error"
                    )
    
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
            
            # Show notification for cleared history
            self.notification_manager.show_clipboard_notification(
                "🗑️ History Cleared",
                "All clipboard history has been cleared",
                "warning"
            )
    
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
        
        # Determine the actual theme to use
        if theme == "System":
            from gui.themes.material_theme import detect_system_theme
            theme_type = detect_system_theme()
        else:
            theme_type = theme.lower()
        
        # Apply the Material Design theme
        app = QApplication.instance()
        apply_material_theme_to_app(app, theme_type)
    
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
        
        # If no search text, apply filter directly
        if not self.current_search_text.strip():
            if filter_type == "All Types":
                self.load_history()
            else:
                self.filter_history_list("", filter_type)
        else:
            # Apply both search and filter
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
    
    def clear_all_filters(self):
        """Clear all filters and show all items."""
        self.search_input.clear()
        self.search_type_filter.setCurrentText("All Types")
        self.current_search_text = ""
        self.current_search_type = "All Types"
        self.load_history()
        
        # Show notification
        self.notification_manager.show_clipboard_notification(
            "🔄 Filters Cleared",
            "All filters have been cleared, showing all items",
            "info"
        )
    
    def set_filter_by_index(self, index):
        """Set the filter by index (for keyboard shortcuts)."""
        if 0 <= index < self.search_type_filter.count():
            self.search_type_filter.setCurrentIndex(index)
            filter_name = self.search_type_filter.itemText(index)
            
            # Show notification
            self.notification_manager.show_clipboard_notification(
                f"🔍 Filter: {filter_name}",
                f"Filter set to {filter_name} via keyboard shortcut",
                "info"
            )
    
    def filter_history_list(self, search_text, filter_type="All Types"):
        """Filter the history list based on the search text and type filter."""
        from datetime import datetime, timedelta
        
        # Clear current history list
        self.history_list.clear()
        self.clipboard_history.clear()
        
        # Handle different filter types
        if filter_type == "Favorites":
            # Get favorite items
            items = self.history_manager.get_favorites(limit=100)
            
            # Filter by search text if provided
            if search_text.strip():
                filtered_items = []
                for item in items:
                    if self._item_matches_search(item, search_text):
                        filtered_items.append(item)
                items = filtered_items
                
        elif filter_type == "Recent (24h)":
            # Get all items and filter by time
            all_items = self.history_manager.get_all_items(limit=1000)
            cutoff_time = datetime.now() - timedelta(hours=24)
            
            items = [item for item in all_items if item.timestamp >= cutoff_time]
            
            # Filter by search text if provided
            if search_text.strip():
                filtered_items = []
                for item in items:
                    if self._item_matches_search(item, search_text):
                        filtered_items.append(item)
                items = filtered_items
                
        elif filter_type == "This Week":
            # Get all items and filter by time
            all_items = self.history_manager.get_all_items(limit=1000)
            cutoff_time = datetime.now() - timedelta(days=7)
            
            items = [item for item in all_items if item.timestamp >= cutoff_time]
            
            # Filter by search text if provided
            if search_text.strip():
                filtered_items = []
                for item in items:
                    if self._item_matches_search(item, search_text):
                        filtered_items.append(item)
                items = filtered_items
                
        else:
            # Handle content type filters
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
        if search_text.strip():
            filter_text = f" ({filter_type.lower()})" if filter_type != "All Types" else ""
            self.status_bar.showMessage(f"Found {len(items)} items matching '{search_text}'{filter_text}")
        else:
            self.status_bar.showMessage(f"Showing {len(items)} items ({filter_type})")
        
        # Show notification for search results
        if len(items) == 0:
            search_desc = f"matching '{search_text}'" if search_text.strip() else f"in {filter_type.lower()}"
            self.notification_manager.show_clipboard_notification(
                "🔍 No Results",
                f"No items found {search_desc}",
                "warning"
            )
        else:
            search_desc = f"matching '{search_text}'" if search_text.strip() else f"in {filter_type.lower()}"
            self.notification_manager.show_clipboard_notification(
                "🔍 Filter Results",
                f"Found {len(items)} items {search_desc}",
                "info"
            )
    
    def _item_matches_search(self, item, search_text):
        """Check if an item matches the search text."""
        search_text = search_text.lower()
        
        if item.data_type == 'text' and isinstance(item.content, str):
            return search_text in item.content.lower()
        elif item.data_type == 'files' and isinstance(item.content, list):
            return any(search_text in str(file_path).lower() for file_path in item.content)
        elif item.data_type == 'image':
            return search_text in "[Image]".lower()
        else:
            return search_text in str(item.content).lower()
    
    def resizeEvent(self, event):
        """Handle window resize for responsive layout."""
        super().resizeEvent(event)
        self.adjustLayoutForWindowSize()
        
    def adjustLayoutForWindowSize(self):
        """Adjust layout based on window size for responsive design."""
        current_size = self.size()
        width = current_size.width()
        height = current_size.height()
        
        # Define responsive breakpoints
        breakpoints = {
            'mobile': 480,
            'tablet': 768,
            'desktop': 1024,
            'large': 1440
        }
        
        # Adjust splitter orientation and sizes
        if width < breakpoints['tablet']:
            # Mobile and small tablet view
            self.splitter.setOrientation(Qt.Orientation.Vertical)
            self.splitter.setSizes([1, 2])  # History smaller, preview larger
        elif width < breakpoints['desktop']:
            # Large tablet view
            self.splitter.setOrientation(Qt.Orientation.Horizontal)
            self.splitter.setSizes([2, 3])  # More balanced split
        else:
            # Desktop view
            self.splitter.setOrientation(Qt.Orientation.Horizontal)
            self.splitter.setSizes([1, 3])  # Traditional split
        
        # Adjust search layout responsively
        if width < breakpoints['mobile']:
            # Stack search elements vertically for very small screens
            self.search_layout.setDirection(QHBoxLayout.Direction.TopToBottom)
            self.search_input.setMinimumWidth(200)
            self.search_type_filter.setMinimumWidth(120)
            self.clear_filter_button.setMaximumWidth(80)
        elif width < breakpoints['tablet']:
            # Horizontal but with minimum widths
            self.search_layout.setDirection(QHBoxLayout.Direction.LeftToRight)
            self.search_input.setMinimumWidth(150)
            self.search_type_filter.setMinimumWidth(100)
            self.clear_filter_button.setMaximumWidth(80)
        else:
            # Normal horizontal layout
            self.search_layout.setDirection(QHBoxLayout.Direction.LeftToRight)
            self.search_input.setMinimumWidth(200)
            self.search_type_filter.setMinimumWidth(120)
            self.clear_filter_button.setMaximumWidth(100)
        
        # Adjust toolbar based on window size
        self.adjustToolbarForWindowSize(width)
        
        # Adjust font sizes based on window size
        self.adjustFontSizesForWindowSize(width)
        
        # Adjust notification positioning for responsive design
        self.adjustNotificationPositioning(width, height)
    
    def adjustToolbarForWindowSize(self, width):
        """Adjust toolbar layout for different window sizes."""
        toolbar = self.findChild(QToolBar)
        if not toolbar:
            return
            
        if width < 600:
            # Very small screens - icon only
            toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
            toolbar.setIconSize(QSize(16, 16))
        elif width < 800:
            # Small screens - smaller icons with text
            toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
            toolbar.setIconSize(QSize(16, 16))
        else:
            # Normal screens - full size
            toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
            toolbar.setIconSize(QSize(20, 20))
    
    def adjustFontSizesForWindowSize(self, width):
        """Adjust font sizes based on window size for better readability."""
        if width < 600:
            # Small screens - smaller fonts
            self.history_header.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            self.search_input.setFont(QFont("Arial", 9))
            self.search_type_filter.setFont(QFont("Arial", 9))
        elif width < 800:
            # Medium screens - medium fonts
            self.history_header.setFont(QFont("Arial", 11, QFont.Weight.Bold))
            self.search_input.setFont(QFont("Arial", 10))
            self.search_type_filter.setFont(QFont("Arial", 10))
        else:
            # Large screens - normal fonts
            self.history_header.setFont(QFont("Arial", 12, QFont.Weight.Bold))
            self.search_input.setFont(QFont("Arial", 11))
            self.search_type_filter.setFont(QFont("Arial", 11))
    
    def adjustNotificationPositioning(self, width, height):
        """Adjust notification positioning based on window size."""
        if hasattr(self, 'notification_manager'):
            self.notification_manager.adjust_for_window_size(width, height)
    
    def closeEvent(self, event):
        """Handle window close event."""
        # Clear all notifications
        self.notification_manager.clear_all_notifications()
        
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
    
    def show_history_context_menu(self, position):
        """Show context menu for history items."""
        item = self.history_list.itemAt(position)
        if not item:
            return
        
        context_menu = QMenu(self)
        
        # Copy action
        copy_action = QAction("📋 Copy to Clipboard", self)
        copy_action.triggered.connect(lambda: self.copy_selected_to_clipboard())
        context_menu.addAction(copy_action)
        
        # Save action
        save_action = QAction("💾 Save to File", self)
        save_action.triggered.connect(lambda: self.save_selected_item())
        context_menu.addAction(save_action)
        
        context_menu.addSeparator()
        
        # Toggle favorite action
        favorite_action = QAction("⭐ Toggle Favorite", self)
        favorite_action.triggered.connect(lambda: self.toggle_item_favorite(item))
        context_menu.addAction(favorite_action)
        
        # Delete action
        delete_action = QAction("🗑️ Delete", self)
        delete_action.triggered.connect(lambda: self.delete_history_item(item))
        context_menu.addAction(delete_action)
        
        # Show the context menu
        context_menu.exec(self.history_list.mapToGlobal(position))
    
    def toggle_item_favorite(self, item):
        """Toggle the favorite status of a history item."""
        # This would need to be implemented with the database item ID
        # For now, show a notification
        self.notification_manager.show_clipboard_notification(
            "⭐ Favorite Toggle",
            "Favorites functionality would be fully implemented with database integration",
            "info"
        )
    
    def delete_history_item(self, item):
        """Delete a history item."""
        reply = QMessageBox.question(
            self, "Delete Item",
            "Are you sure you want to delete this item?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            row = self.history_list.row(item)
            self.history_list.takeItem(row)
            
            # Remove from clipboard_history list
            if row < len(self.clipboard_history):
                self.clipboard_history.pop(row)
            
            # Remove from original_clipboard_history list
            if row < len(self.original_clipboard_history):
                self.original_clipboard_history.pop(row)
            
            self.status_bar.showMessage("Item deleted")
            
            # Show notification
            self.notification_manager.show_clipboard_notification(
                "🗑️ Item Deleted",
                "History item has been deleted",
                "warning"
            )
