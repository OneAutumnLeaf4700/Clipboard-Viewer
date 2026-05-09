from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QLabel, 
                            QPushButton, QFrame, QSizePolicy, QGraphicsOpacityEffect)
from PyQt6.QtGui import QIcon, QFont, QColor
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QPropertyAnimation, QEasingCurve
import os

class HistoryItemWidget(QFrame):
    """
    Custom widget for clipboard history items.
    Provides a modern, card-like interface for each history entry.
    """
    
    # Signals for user interactions
    copy_requested = pyqtSignal(object)
    delete_requested = pyqtSignal(object)
    pin_requested = pyqtSignal(object)
    
    def __init__(self, data_type, content, timestamp, is_pinned=False, parent=None):
        super().__init__(parent)
        self.data_type = data_type
        self.content = content
        self.timestamp = timestamp
        self.is_pinned = is_pinned
        
        self.setObjectName("historyItemCard")
        self.setFrameShape(QFrame.Shape.NoFrame)
        
        # Opacity effect for fade-in animation
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(1.0) # Default to fully visible
        
        self.setup_ui()
        self.update_pin_style()
        
    def animate_fade_in(self, duration=500):
        """Perform a fade-in animation."""
        self.opacity_effect.setOpacity(0.0)
        self.animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.animation.setDuration(duration)
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.animation.start()
        
    def setup_ui(self):
        # Main layout for the card
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(12, 8, 12, 8)
        self.main_layout.setSpacing(12)
        
        # Icon section
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(32, 32)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.set_type_icon()
        self.main_layout.addWidget(self.icon_label)
        
        # Content section
        self.content_layout = QVBoxLayout()
        self.content_layout.setSpacing(2)
        
        # Timestamp label
        self.time_label = QLabel(self.timestamp.strftime("%H:%M:%S • %Y-%m-%d"))
        self.time_label.setStyleSheet("color: #6C757D; font-size: 10px; font-weight: 500;")
        self.content_layout.addWidget(self.time_label)
        
        # Content snippet
        self.snippet_label = QLabel(self.get_content_snippet())
        self.snippet_label.setStyleSheet("color: #212529; font-size: 13px; font-weight: 400;")
        self.snippet_label.setWordWrap(False)
        self.content_layout.addWidget(self.snippet_label)
        
        self.main_layout.addLayout(self.content_layout, 1)
        
        # Actions section
        self.actions_layout = QHBoxLayout()
        self.actions_layout.setSpacing(4)
        
        # Pin button
        self.pin_button = QPushButton()
        self.pin_button.setFixedSize(28, 28)
        self.pin_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.pin_button.setToolTip("Pin/Unpin item")
        self.pin_button.clicked.connect(lambda: self.pin_requested.emit(self))
        self.actions_layout.addWidget(self.pin_button)
        
        # Copy button
        self.copy_button = QPushButton("📋") # Using emoji as fallback if icon fails
        self.copy_button.setFixedSize(28, 28)
        self.copy_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.copy_button.setToolTip("Copy to clipboard")
        self.copy_button.clicked.connect(lambda: self.copy_requested.emit(self))
        self.actions_layout.addWidget(self.copy_button)
        
        # Delete button
        self.delete_button = QPushButton("🗑️")
        self.delete_button.setFixedSize(28, 28)
        self.delete_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.delete_button.setToolTip("Remove from history")
        self.delete_button.clicked.connect(lambda: self.delete_requested.emit(self))
        self.actions_layout.addWidget(self.delete_button)
        
        self.main_layout.addLayout(self.actions_layout)
        
        # Set background and border styling
        self.setStyleSheet("""
            #historyItemCard {
                background-color: #FFFFFF;
                border: 1px solid #E9ECEF;
                border-radius: 8px;
            }
            #historyItemCard:hover {
                background-color: #F8F9FA;
                border-color: #DEE2E6;
            }
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #E9ECEF;
            }
        """)

    def set_type_icon(self):
        icon_path = ""
        assets_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "assets", "icons")
        
        if self.data_type == "text":
            icon_path = os.path.join(assets_dir, "text_icon.svg")
        elif self.data_type == "image":
            icon_path = os.path.join(assets_dir, "image_icon.svg")
        elif self.data_type == "files":
            icon_path = os.path.join(assets_dir, "file_icon.svg")
        else:
            icon_path = os.path.join(assets_dir, "unknown_icon.svg")
            
        if os.path.exists(icon_path):
            pixmap = QIcon(icon_path).pixmap(QSize(24, 24))
            self.icon_label.setPixmap(pixmap)
        else:
            # Fallback text if icon is missing
            self.icon_label.setText("📄" if self.data_type == "text" else "🖼️" if self.data_type == "image" else "📁")

    def get_content_snippet(self):
        if self.data_type == "text":
            text = self.content.strip().replace('\n', ' ')
            return (text[:60] + "...") if len(text) > 60 else text
        elif self.data_type == "image":
            return "[Image Content]"
        elif self.data_type == "files":
            count = len(self.content)
            return f"{count} file{'s' if count > 1 else ''}"
        return "[Unknown Data]"

    def update_pin_style(self):
        if self.is_pinned:
            self.pin_button.setText("📌")
            self.pin_button.setStyleSheet("background-color: #E7F1FF; border-radius: 4px;")
            self.setStyleSheet(self.styleSheet() + """
                #historyItemCard {
                    border-left: 4px solid #0D6EFD;
                }
            """)
        else:
            self.pin_button.setText("📍")
            self.pin_button.setStyleSheet("")
            # Reset border-left if not pinned (this is a bit simplified)
            self.setStyleSheet(self.styleSheet().replace("border-left: 4px solid #0D6EFD;", ""))

    def toggle_pin(self):
        self.is_pinned = not self.is_pinned
        self.update_pin_style()
