import os
import logging
from datetime import datetime
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGraphicsOpacityEffect, QApplication
from PyQt6.QtCore import QTimer, QPropertyAnimation, QEasingCurve, QRect, pyqtSignal, QObject, Qt
from PyQt6.QtGui import QFont, QPalette, QColor

class NotificationManager(QObject):
    """Manages various types of notifications for the clipboard application."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger("NotificationManager")
        self.parent_widget = parent
        self.notifications = []
        self.max_notifications = 5
        
        # Notification settings
        self.show_clipboard_notifications = True
        self.show_system_tray_notifications = True
        self.notification_duration = 3000  # 3 seconds
        
        # Statistics tracking
        self.stats = {
            'total_items': 0,
            'text_items': 0,
            'image_items': 0,
            'file_items': 0,
            'session_start': datetime.now()
        }
        
    def show_clipboard_notification(self, title, message, notification_type="info"):
        """Show a notification when clipboard content changes."""
        if not self.show_clipboard_notifications:
            return
            
        self.show_toast_notification(title, message, notification_type)
        
    def show_system_tray_notification(self, title, message, icon=None):
        """Show a system tray notification."""
        if not self.show_system_tray_notifications or not self.parent_widget:
            return
            
        if hasattr(self.parent_widget, 'tray_icon') and self.parent_widget.tray_icon:
            self.parent_widget.tray_icon.showMessage(title, message, icon or self.parent_widget.tray_icon.MessageIcon.Information, self.notification_duration)
    
    def show_toast_notification(self, title, message, notification_type="info", content_type=None):
        """Show a toast notification on screen with detailed information."""
        if not self.parent_widget:
            return
            
        # Update statistics based on content type
        if content_type:
            self.update_statistics(content_type)
        
        # Append statistics to message for clipboard notifications
        if content_type:
            message += f"\n📊 Session Stats: {self.stats['total_items']} items"
            message += f"\n📝 Text: {self.stats['text_items']} | 🖼️ Images: {self.stats['image_items']} | 📁 Files: {self.stats['file_items']}"
        
        # Create toast notification
        toast = ToastNotification(title, message, notification_type, self.parent_widget)
        toast.show()
        
        # Add to notifications list
        self.notifications.append(toast)
        
        # Remove old notifications if exceeding max
        if len(self.notifications) > self.max_notifications:
            old_toast = self.notifications.pop(0)
            old_toast.close()
        
        # Position notifications
        self._position_notifications()
        
        # Auto-remove after duration
        QTimer.singleShot(self.notification_duration, lambda: self._remove_notification(toast))
    
    def update_statistics(self, content_type):
        """Update the statistics based on content type."""
        self.stats['total_items'] += 1
        if content_type == 'text':
            self.stats['text_items'] += 1
        elif content_type == 'image':
            self.stats['image_items'] += 1
        elif content_type == 'files':
            self.stats['file_items'] += 1
    
    def get_session_summary(self):
        """Get a summary of the current session statistics."""
        session_duration = datetime.now() - self.stats['session_start']
        hours, remainder = divmod(session_duration.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        return {
            'total_items': self.stats['total_items'],
            'text_items': self.stats['text_items'],
            'image_items': self.stats['image_items'],
            'file_items': self.stats['file_items'],
            'session_duration': f"{hours:02d}:{minutes:02d}:{seconds:02d}",
            'avg_items_per_minute': round(self.stats['total_items'] / max(session_duration.seconds / 60, 1), 1)
        }
    
    def _position_notifications(self):
        """Position toast notifications on screen."""
        if not self.parent_widget:
            return
            
        parent_rect = self.parent_widget.geometry()
        parent_width = parent_rect.width()
        
        # Responsive notification positioning
        if parent_width < 768:  # Mobile/tablet
            notification_width = min(300, parent_width - 40)
            x = parent_rect.left() + (parent_width - notification_width) // 2  # Center horizontally
            y = parent_rect.top() + 10  # Small top margin
            spacing = 60  # Smaller spacing for mobile
        else:  # Desktop
            notification_width = 320
            x = parent_rect.right() - notification_width - 20  # Right side with margin
            y = parent_rect.top() + 50  # Standard top margin
            spacing = 70  # Standard spacing
        
        for i, notification in enumerate(self.notifications):
            notification.move(x, y + i * spacing)
            # Adjust notification width if needed
            if hasattr(notification, 'setFixedWidth'):
                notification.setFixedWidth(notification_width)
    
    def adjust_for_window_size(self, width, height):
        """Adjust notification settings based on window size."""
        # Adjust notification duration based on screen size
        if width < 600:
            self.notification_duration = 4000  # Longer duration for small screens
            self.max_notifications = 3  # Fewer notifications on small screens
        elif width < 1024:
            self.notification_duration = 3500  # Medium duration
            self.max_notifications = 4
        else:
            self.notification_duration = 3000  # Standard duration
            self.max_notifications = 5
        
        # Reposition existing notifications
        self._position_notifications()
    
    def _remove_notification(self, toast):
        """Remove a toast notification."""
        if toast in self.notifications:
            self.notifications.remove(toast)
            toast.close()
            self._position_notifications()
    
    def clear_all_notifications(self):
        """Clear all active notifications."""
        for notification in self.notifications:
            notification.close()
        self.notifications.clear()
    
    def set_notification_settings(self, show_clipboard=True, show_system_tray=True, duration=3000):
        """Update notification settings."""
        self.show_clipboard_notifications = show_clipboard
        self.show_system_tray_notifications = show_system_tray
        self.notification_duration = duration

class ToastNotification(QWidget):
    """Custom toast notification widget."""
    
    def __init__(self, title, message, notification_type="info", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Notification")
        
        # Adjust size based on message length
        line_count = message.count('\n') + 1
        base_height = 60
        extra_height = max(0, (line_count - 2) * 20)
        self.setFixedSize(320, base_height + extra_height)
        
        self.setWindowFlags(self.windowFlags() | 
                           self.windowType().WindowStaysOnTopHint | 
                           self.windowType().FramelessWindowHint)
        
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.notification_type = notification_type
        self.setup_ui(title, message)
        self.setup_animations()
        
    def setup_ui(self, title, message):
        """Set up the notification UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Icon based on notification type
        icon_label = QLabel()
        icon_label.setFixedSize(20, 20)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        if self.notification_type == "success":
            icon_label.setText("✅")
            bg_color = "#D4EDDA"
            border_color = "#C3E6CB"
        elif self.notification_type == "error":
            icon_label.setText("❌")
            bg_color = "#F8D7DA"
            border_color = "#F5C6CB"
        elif self.notification_type == "warning":
            icon_label.setText("⚠️")
            bg_color = "#FFF3CD"
            border_color = "#FFEAA7"
        else:  # info
            icon_label.setText("ℹ️")
            bg_color = "#D1ECF1"
            border_color = "#BEE5EB"
        
        # Content
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(2)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        title_label.setWordWrap(True)
        
        message_label = QLabel(message)
        message_label.setFont(QFont("Arial", 8))
        message_label.setWordWrap(True)
        
        content_layout.addWidget(title_label)
        content_layout.addWidget(message_label)
        
        # Close button
        close_button = QPushButton("×")
        close_button.setFixedSize(20, 20)
        close_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                font-size: 14px;
                font-weight: bold;
                color: #666;
            }
            QPushButton:hover {
                background-color: rgba(0, 0, 0, 0.1);
                border-radius: 10px;
            }
        """)
        close_button.clicked.connect(self.close)
        
        layout.addWidget(icon_label)
        layout.addLayout(content_layout)
        layout.addWidget(close_button)
        
        # Style the notification
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {bg_color};
                border: 1px solid {border_color};
                border-radius: 8px;
            }}
            QLabel {{
                color: #333;
                background-color: transparent;
                border: none;
            }}
        """)
        
    def setup_animations(self):
        """Set up fade in/out animations."""
        self.opacity_effect = QGraphicsOpacityEffect()
        self.setGraphicsEffect(self.opacity_effect)
        
        self.fade_in_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_in_animation.setDuration(300)
        self.fade_in_animation.setStartValue(0)
        self.fade_in_animation.setEndValue(1)
        self.fade_in_animation.setEasingCurve(QEasingCurve.Type.OutQuad)
        
        self.fade_out_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_out_animation.setDuration(300)
        self.fade_out_animation.setStartValue(1)
        self.fade_out_animation.setEndValue(0)
        self.fade_out_animation.setEasingCurve(QEasingCurve.Type.InQuad)
        self.fade_out_animation.finished.connect(self.hide)
        
    def show(self):
        """Show the notification with fade in animation."""
        super().show()
        self.fade_in_animation.start()
        
    def close(self):
        """Close the notification with fade out animation."""
        self.fade_out_animation.start()
        QTimer.singleShot(300, super().close)
