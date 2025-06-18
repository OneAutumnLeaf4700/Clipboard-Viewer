import sys
import os
from datetime import datetime
from PyQt6.QtWidgets import (QMainWindow, QApplication, QSplitter, QListWidget, 
                            QListWidgetItem, QVBoxLayout, QHBoxLayout, QWidget, 
                            QLabel, QPushButton, QMenu, QSystemTrayIcon, 
                            QMessageBox, QFrame, QToolBar, QStatusBar, QFileDialog)
from PyQt6.QtGui import QIcon, QAction, QPixmap, QFont, QCursor
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QTimer

# Import the clipboard data retrieval function
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.clipboard_utils import get_clipboard_data

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


class PreviewWidget(QWidget):
    """Widget for displaying previews of clipboard content."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        
        # Header
        self.header_label = QLabel("Preview")
        self.header_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        
        # Content area
        self.content_frame = QFrame()
        self.content_frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.content_layout = QVBoxLayout(self.content_frame)
        
        # Content widgets
        self.text_preview = QLabel()
        self.text_preview.setWordWrap(True)
        self.text_preview.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        
        self.image_preview = QLabel()
        self.image_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.file_preview = QListWidget()
        
        # Add widgets to content layout
        self.content_layout.addWidget(self.text_preview)
        self.content_layout.addWidget(self.image_preview)
        self.content_layout.addWidget(self.file_preview)
        
        # Action buttons
        self.button_layout = QHBoxLayout()
        self.copy_button = QPushButton("Copy to Clipboard")
        self.save_button = QPushButton("Save As...")
        self.button_layout.addWidget(self.copy_button)
        self.button_layout.addWidget(self.save_button)
        
        # Add all components to main layout
        self.layout.addWidget(self.header_label)
        self.layout.addWidget(self.content_frame)
        self.layout.addLayout(self.button_layout)
        
        # Hide all preview widgets initially
        self.clear_preview()
        
    def clear_preview(self):
        """Clear and hide all preview widgets."""
        self.text_preview.setText("")
        self.text_preview.hide()
        
        self.image_preview.clear()
        self.image_preview.hide()
        
        self.file_preview.clear()
        self.file_preview.hide()
        
        self.copy_button.setEnabled(False)
        self.save_button.setEnabled(False)
    
    def show_preview(self, item):
        """Display preview based on the clipboard item type."""
        if not item:
            self.clear_preview()
            return
            
        # Clear previous preview
        self.clear_preview()
        
        # Show appropriate preview based on data type
        if item.data_type == "text":
            self.text_preview.setText(item.content)
            self.text_preview.show()
            self.copy_button.setEnabled(True)
            self.save_button.setEnabled(True)
            
        elif item.data_type == "image" and item.content:
            # Convert PIL image to QPixmap
            if hasattr(item.content, 'save'):
                # Save to temporary file and load as QPixmap
                temp_path = "temp_preview.png"
                item.content.save(temp_path)
                pixmap = QPixmap(temp_path)
                
                # Scale pixmap to fit the preview area while maintaining aspect ratio
                max_size = QSize(400, 300)
                scaled_pixmap = pixmap.scaled(max_size, 
                                             Qt.AspectRatioMode.KeepAspectRatio, 
                                             Qt.TransformationMode.SmoothTransformation)
                
                self.image_preview.setPixmap(scaled_pixmap)
                self.image_preview.show()
                self.copy_button.setEnabled(True)
                self.save_button.setEnabled(True)
                
                # Clean up temporary file
                if os.path.exists(temp_path):
                    os.remove(temp_path)
            
        elif item.data_type == "files":
            self.file_preview.clear()
            for file_path in item.content:
                self.file_preview.addItem(file_path)
            self.file_preview.show()
            self.copy_button.setEnabled(True)
            self.save_button.setEnabled(False)  # Can't save file paths
            
        else:
            self.text_preview.setText("[No preview available for this content type]")
            self.text_preview.show()
            self.copy_button.setEnabled(False)
            self.save_button.setEnabled(False)


class MainWindow(QMainWindow):
    """Main window for the Clipboard Viewer application."""
    
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
        
        # Add search bar
        self.search_layout = QHBoxLayout()
        from PyQt6.QtWidgets import QLineEdit
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search clipboard history...")
        self.search_input.textChanged.connect(self.on_search_text_changed)
        
        self.clear_search_button = QPushButton("Clear")
        self.clear_search_button.clicked.connect(self.clear_search)
        self.clear_search_button.setEnabled(False)
        
        self.search_layout.addWidget(self.search_input)
        self.search_layout.addWidget(self.clear_search_button)
        
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
        """Show the settings dialog."""
        # Placeholder for settings dialog
        QMessageBox.information(self, "Settings", "Settings dialog would appear here")
    
    def on_search_text_changed(self, text):
        """Handle search text changes and filter the history list."""
        if text:
            self.clear_search_button.setEnabled(True)
            self.filter_history_list(text)
        else:
            self.clear_search_button.setEnabled(False)
            self.load_history()  # Reload all history items
    
    def clear_search(self):
        """Clear the search input and reload all history items."""
        self.search_input.clear()
        self.clear_search_button.setEnabled(False)
        self.load_history()
    
    def filter_history_list(self, search_text):
        """Filter the history list based on the search text."""
        # Clear current history list
        self.history_list.clear()
        self.clipboard_history.clear()
        
        # Get filtered items from history manager
        items = self.history_manager.search_items(search_text, limit=100)
        
        # Add items to history list
        for item in items:
            # Create list item
            list_item = ClipboardListItem(item.data_type, item.content, item.timestamp)
            
            # Add to history list
            self.history_list.addItem(list_item)
            self.clipboard_history.append(list_item)
        
        # Update status
        self.status_bar.showMessage(f"Found {len(items)} items matching '{search_text}'")
    
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