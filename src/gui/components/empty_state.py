from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtGui import QIcon, QFont, QPixmap
from PyQt6.QtCore import Qt, QSize
import os

class EmptyStateWidget(QWidget):
    """
    Widget shown when the clipboard history is empty.
    Provides helpful tips and a friendly message.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.setSpacing(20)
        
        # Illustration / Icon
        self.icon_label = QLabel()
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        assets_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "assets", "icons")
        app_icon_path = os.path.join(assets_dir, "app_icon.svg")
        
        if os.path.exists(app_icon_path):
            pixmap = QIcon(app_icon_path).pixmap(QSize(128, 128))
            self.icon_label.setPixmap(pixmap)
        else:
            self.icon_label.setText("📋")
            self.icon_label.setStyleSheet("font-size: 80px;")
            
        self.main_layout.addWidget(self.icon_label)
        
        # Main message
        self.title_label = QLabel("Your clipboard history is empty")
        self.title_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        self.title_label.setStyleSheet("color: #212529;")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.title_label)
        
        # Description / Tip
        self.desc_label = QLabel(
            "Copy anything (text, images, or files) and they will appear here automatically.\n"
            "Use Ctrl+C to copy items as usual."
        )
        self.desc_label.setFont(QFont("Segoe UI", 11))
        self.desc_label.setStyleSheet("color: #6C757D;")
        self.desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.desc_label.setWordWrap(True)
        self.main_layout.addWidget(self.desc_label)
        
        # Tip box
        self.tip_frame = QWidget()
        self.tip_frame.setStyleSheet("""
            QWidget {
                background-color: #E7F1FF;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        tip_layout = QVBoxLayout(self.tip_frame)
        tip_text = QLabel("💡 Pro Tip: You can pin important items to keep them forever!")
        tip_text.setStyleSheet("color: #084298; font-weight: 500;")
        tip_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tip_layout.addWidget(tip_text)
        
        self.main_layout.addWidget(self.tip_frame)
        
        # Add some stretch at the bottom to keep everything centered
        self.main_layout.addStretch()
