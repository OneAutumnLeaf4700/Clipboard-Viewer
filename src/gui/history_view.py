from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget, 
                            QListWidgetItem, QLabel, QPushButton, QLineEdit,
                            QComboBox, QMenu, QMessageBox)
from PyQt6.QtGui import QIcon, QAction, QFont
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from datetime import datetime

class HistoryView(QWidget):
    """Widget for displaying and managing clipboard history."""
    
    item_selected = pyqtSignal(object)  # Signal emitted when an item is selected
    item_deleted = pyqtSignal(object)   # Signal emitted when an item is deleted
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the user interface components."""
        # Main layout
        self.layout = QVBoxLayout(self)
        
        # Header with title and controls
        header_layout = QHBoxLayout()
        
        self.title_label = QLabel("Clipboard History")
        self.title_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search history...")
        self.search_input.textChanged.connect(self.filter_history)
        
        self.filter_combo = QComboBox()
        self.filter_combo.addItem("All Types")
        self.filter_combo.addItem("Text Only")
        self.filter_combo.addItem("Images Only")
        self.filter_combo.addItem("Files Only")
        self.filter_combo.currentIndexChanged.connect(self.filter_history)
        
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.search_input)
        header_layout.addWidget(self.filter_combo)
        
        # History list
        self.history_list = QListWidget()
        self.history_list.setAlternatingRowColors(True)
        self.history_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.history_list.customContextMenuRequested.connect(self.show_context_menu)
        self.history_list.currentItemChanged.connect(self.on_item_selected)
        
        # Add components to main layout
        self.layout.addLayout(header_layout)
        self.layout.addWidget(self.history_list)
        
    def add_item(self, item):
        """Add a new item to the history list."""
        self.history_list.insertItem(0, item)  # Add at the top
        
    def remove_item(self, item):
        """Remove an item from the history list."""
        row = self.history_list.row(item)
        if row >= 0:
            removed_item = self.history_list.takeItem(row)
            self.item_deleted.emit(removed_item)
            
    def clear_history(self):
        """Clear all items from the history list."""
        self.history_list.clear()
        
    def filter_history(self):
        """Filter history items based on search text and type filter."""
        search_text = self.search_input.text().lower()
        filter_index = self.filter_combo.currentIndex()
        
        # Show/hide items based on filter criteria
        for i in range(self.history_list.count()):
            item = self.history_list.item(i)
            
            # Check if item matches the type filter
            type_match = True
            if filter_index == 1:  # Text Only
                type_match = item.data_type == "text"
            elif filter_index == 2:  # Images Only
                type_match = item.data_type == "image"
            elif filter_index == 3:  # Files Only
                type_match = item.data_type == "files"
            
            # Check if item matches the search text
            text_match = True
            if search_text:
                if item.data_type == "text":
                    text_match = search_text in item.content.lower()
                elif item.data_type == "files":
                    # Search in file paths
                    text_match = any(search_text in file_path.lower() for file_path in item.content)
                else:
                    # For images and other types, search in the display text
                    text_match = search_text in item.text().lower()
            
            # Show/hide the item based on both filters
            self.history_list.setRowHidden(i, not (type_match and text_match))
    
    def on_item_selected(self, current, previous):
        """Handle selection of an item in the history list."""
        if current:
            self.item_selected.emit(current)
    
    def show_context_menu(self, position):
        """Show context menu for history items."""
        item = self.history_list.itemAt(position)
        if not item:
            return
            
        context_menu = QMenu(self)
        
        # Copy action
        copy_action = QAction("Copy to Clipboard", self)
        copy_action.triggered.connect(lambda: self.copy_to_clipboard(item))
        context_menu.addAction(copy_action)
        
        # Delete action
        delete_action = QAction("Delete", self)
        delete_action.triggered.connect(lambda: self.remove_item(item))
        context_menu.addAction(delete_action)
        
        # Add to favorites action (placeholder)
        favorite_action = QAction("Add to Favorites", self)
        favorite_action.triggered.connect(lambda: self.toggle_favorite(item))
        context_menu.addAction(favorite_action)
        
        # Show the context menu
        context_menu.exec(self.history_list.mapToGlobal(position))
    
    def copy_to_clipboard(self, item):
        """Copy the selected item back to the clipboard."""
        # This is a placeholder - actual implementation would need to
        # handle different data types when copying back to clipboard
        QMessageBox.information(self, "Clipboard", "Item copied to clipboard")
    
    def toggle_favorite(self, item):
        """Toggle favorite status for an item."""
        # This is a placeholder for the favorites functionality
        QMessageBox.information(self, "Favorites", "Favorites functionality would be implemented here")