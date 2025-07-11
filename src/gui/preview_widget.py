import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QFrame, QListWidget, QFileDialog,
                            QScrollArea, QSizePolicy, QMessageBox)
from PyQt6.QtGui import QPixmap, QFont, QImage
from PyQt6.QtCore import Qt, QSize, pyqtSignal
# Material theme will be applied application-wide
from gui.components.animated_preview import AnimatedPreviewWidget, AnimatedContentWidget

class PreviewWidget(AnimatedPreviewWidget):
    """Widget for displaying previews of clipboard content."""
    
    copy_requested = pyqtSignal(object)  # Signal emitted when copy button is clicked
    save_requested = pyqtSignal(object)  # Signal emitted when save button is clicked
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_item = None
        self.setProperty("class", "preview-area")
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the user interface components."""
        # Main layout
        self.layout = QVBoxLayout(self)
        
        # Header
        self.header_label = QLabel("Preview")
        self.header_label.setProperty("class", "preview-header")
        
        # Create a scroll area for the content
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        
        # Content container widget
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        
        # Content frame with border
        self.content_frame = QFrame()
        self.content_frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.content_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # Content type widgets
        self.setup_preview_widgets()
        
        # Set the content widget as the scroll area's widget
        self.scroll_area.setWidget(self.content_widget)
        
        # Set minimum size for content widget
        self.content_widget.setMinimumSize(200, 150)
        
        # Action buttons with responsive design
        self.button_container = QWidget()
        self.button_container.setProperty("class", "preview-buttons")
        self.button_layout = QHBoxLayout(self.button_container)
        
        self.copy_button = QPushButton("📋 Copy")
        self.copy_button.clicked.connect(self.on_copy_clicked)
        self.copy_button.setToolTip("Copy to clipboard")
        
        self.save_button = QPushButton("💾 Save")
        self.save_button.clicked.connect(self.on_save_clicked)
        self.save_button.setToolTip("Save to file")
        
        # Add stretch to center buttons
        self.button_layout.addStretch()
        self.button_layout.addWidget(self.copy_button)
        self.button_layout.addWidget(self.save_button)
        self.button_layout.addStretch()
        
        # Add all components to main layout
        self.layout.addWidget(self.header_label)
        self.layout.addWidget(self.scroll_area, 1)  # Give scroll area a stretch factor
        self.layout.addWidget(self.button_container)

        # Material theme applied application-wide
        
        # Setup responsive adjustments
        self.adjustForWindowSize()
        
        # Hide all preview widgets initially
        self.clear_preview()
        
    def setup_preview_widgets(self):
        """Set up the different preview widgets for various content types."""
        # Text preview
        self.text_container = AnimatedContentWidget()
        self.text_layout = QVBoxLayout(self.text_container)
        
        self.text_type_label = QLabel("Text Content")
        self.text_type_label.setProperty("class", "preview-type")
        
        self.text_preview = QLabel()
        self.text_preview.setWordWrap(True)
        self.text_preview.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.text_preview.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.text_preview.setProperty("class", "preview-text")
        
        self.text_layout.addWidget(self.text_type_label)
        self.text_layout.addWidget(self.text_preview)
        self.content_layout.addWidget(self.text_container)
        
        # Image preview
        self.image_container = AnimatedContentWidget()
        self.image_layout = QVBoxLayout(self.image_container)
        
        self.image_type_label = QLabel("Image Content")
        self.image_type_label.setProperty("class", "preview-type")
        
        self.image_preview = QLabel()
        self.image_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_preview.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.image_preview.setProperty("class", "preview-image")
        
        self.image_layout.addWidget(self.image_type_label)
        self.image_layout.addWidget(self.image_preview)
        self.content_layout.addWidget(self.image_container)
        
        # File preview
        self.file_container = AnimatedContentWidget()
        self.file_layout = QVBoxLayout(self.file_container)
        
        self.file_type_label = QLabel("File Paths")
        self.file_type_label.setProperty("class", "preview-type")
        
        self.file_preview = QListWidget()
        self.file_preview.setAlternatingRowColors(True)
        self.file_preview.setProperty("class", "preview-files")
        
        self.file_layout.addWidget(self.file_type_label)
        self.file_layout.addWidget(self.file_preview)
        self.content_layout.addWidget(self.file_container)
        
        # Unknown format preview
        self.unknown_container = AnimatedContentWidget()
        self.unknown_layout = QVBoxLayout(self.unknown_container)
        
        self.unknown_type_label = QLabel("Unknown Content")
        self.unknown_type_label.setProperty("class", "preview-type")
        
        self.unknown_preview = QLabel("No preview available for this content type")
        self.unknown_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.unknown_preview.setProperty("class", "no-preview")
        
        self.unknown_layout.addWidget(self.unknown_type_label)
        self.unknown_layout.addWidget(self.unknown_preview)
        self.content_layout.addWidget(self.unknown_container)
        
    def adjustForWindowSize(self):
        """Adjust widget sizes based on the current window size."""
        current_size = self.size()
        width = current_size.width()
        
        # Responsive adjustments for preview components
        if width < 480:
            # Very small screens
            self.header_label.setFont(QFont("Arial", 10))
            self.button_layout.setDirection(QHBoxLayout.Direction.TopToBottom)
            self.copy_button.setMinimumWidth(80)
            self.save_button.setMinimumWidth(80)
        elif width < 768:
            # Small to medium screens
            self.header_label.setFont(QFont("Arial", 11))
            self.button_layout.setDirection(QHBoxLayout.Direction.LeftToRight)
            self.copy_button.setMinimumWidth(100)
            self.save_button.setMinimumWidth(100)
        else:
            # Large screens
            self.header_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
            self.button_layout.setDirection(QHBoxLayout.Direction.LeftToRight)
            self.copy_button.setMinimumWidth(120)
            self.save_button.setMinimumWidth(120)
    
    def clear_preview(self):
        """Clear and hide all preview widgets."""
        self.current_item = None
        
        # Hide all containers
        self.text_container.hide()
        self.image_container.hide()
        self.file_container.hide()
        self.unknown_container.hide()
        
        # Clear content
        self.text_preview.setText("")
        self.image_preview.clear()
        self.file_preview.clear()
        
        # Reset labels to default
        self.text_type_label.setText("Text Content")
        self.image_type_label.setText("Image Content")
        self.file_type_label.setText("File Paths")
        
        # Disable buttons
        self.copy_button.setEnabled(False)
        self.save_button.setEnabled(False)
    
    def show_preview(self, item):
        """Display preview based on the clipboard item type."""
        if not item:
            self.clear_preview()
            return
            
        # Store current item
        self.current_item = item
        
        # Clear previous preview
        self.clear_preview()
        
        # Show appropriate preview based on data type
        if item.data_type == "text":
            # Check if text is a URL or special content
            if item.content.startswith(('http://', 'https://', 'ftp://')):
                self.text_type_label.setText("URL Content")
            elif '\n' in item.content and len(item.content) > 100:
                self.text_type_label.setText("Multi-line Text")
            else:
                self.text_type_label.setText("Text Content")
            
            self.text_preview.setText(item.content)
            self.text_container.show()
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
                # Use dynamic sizing based on scroll area size
                scroll_size = self.scroll_area.size()
                max_size = QSize(min(scroll_size.width() - 20, 600), 
                               min(scroll_size.height() - 100, 400))
                scaled_pixmap = pixmap.scaled(max_size, 
                                             Qt.AspectRatioMode.KeepAspectRatio, 
                                             Qt.TransformationMode.SmoothTransformation)
                
                self.image_preview.setPixmap(scaled_pixmap)
                self.image_container.show()
                self.copy_button.setEnabled(True)
                self.save_button.setEnabled(True)
                
                # Clean up temporary file
                if os.path.exists(temp_path):
                    os.remove(temp_path)
            
        elif item.data_type == "files":
            self.file_preview.clear()
            
            # Check if any of the files are images and show image preview
            image_files = []
            other_files = []
            
            for file_path in item.content:
                if self.is_image_file(file_path):
                    image_files.append(file_path)
                else:
                    other_files.append(file_path)
            
            # If there are image files, show the first image in the image preview
            if image_files:
                self.show_image_file_preview(image_files[0])
                # Also show the image container
                self.image_container.show()
            
            # Show all files in the file list
            for file_path in item.content:
                self.file_preview.addItem(file_path)
            
            # Update file type label with count and types
            file_count = len(item.content)
            if image_files:
                self.file_type_label.setText(f"Files ({file_count} total, {len(image_files)} images)")
            else:
                self.file_type_label.setText(f"Files ({file_count} total)")
            
            self.file_container.show()
            self.copy_button.setEnabled(True)
            self.save_button.setEnabled(False)  # Can't save file paths
            
        else:
            self.unknown_container.show()
            self.copy_button.setEnabled(False)
            self.save_button.setEnabled(False)
    
    def is_image_file(self, file_path):
        """Check if a file is an image based on its extension."""
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.webp', '.svg', '.ico'}
        return os.path.splitext(file_path.lower())[1] in image_extensions
    
    def show_image_file_preview(self, image_path):
        """Show preview of an image file."""
        try:
            # Load the image file
            pixmap = QPixmap(image_path)
            
            if not pixmap.isNull():
                # Scale pixmap to fit the preview area while maintaining aspect ratio
                scroll_size = self.scroll_area.size()
                max_size = QSize(min(scroll_size.width() - 40, 600), 
                               min(scroll_size.height() - 150, 400))
                scaled_pixmap = pixmap.scaled(max_size, 
                                             Qt.AspectRatioMode.KeepAspectRatio, 
                                             Qt.TransformationMode.SmoothTransformation)
                
                self.image_preview.setPixmap(scaled_pixmap)
                self.image_container.show()
                
                # Update the image type label to show it's a file
                self.image_type_label.setText(f"Image File: {os.path.basename(image_path)}")
            else:
                self.image_container.hide()
                
        except Exception as e:
            print(f"Error loading image file {image_path}: {e}")
            self.image_container.hide()
    
    def on_copy_clicked(self):
        """Handle copy button click."""
        if self.current_item:
            self.copy_requested.emit(self.current_item)
    
    def on_save_clicked(self):
        """Handle save button click."""
        if self.current_item:
            self.save_requested.emit(self.current_item)
    
    def resizeEvent(self, event):
        """Handle window resize for responsive adjustments."""
        super().resizeEvent(event)
        self.adjustForWindowSize()
    
    def save_item_to_file(self, item):
        """Save the current item to a file."""
        if not item:
            return
            
        if item.data_type == "text":
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save Text", "", "Text Files (*.txt);;All Files (*)"
            )
            if file_path:
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(item.content)
                    QMessageBox.information(self, "Save Successful", f"Saved to {file_path}")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to save file: {e}")
                    
        elif item.data_type == "image" and item.content:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save Image", "", "PNG Files (*.png);;JPEG Files (*.jpg);;All Files (*)"
            )
            if file_path:
                try:
                    item.content.save(file_path)
                    QMessageBox.information(self, "Save Successful", f"Saved to {file_path}")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to save file: {e}")