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
    
    def show_toast_notification(self, title, message, notification_type="info"):
        """Show a toast notification on screen."""
        if not self.parent_widget:
            return
            
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
    
    def _position_notifications(self):
        """Position toast notifications on screen."""
        if not self.parent_widget:
            return
            
        parent_rect = self.parent_widget.geometry()
        x = parent_rect.right() - 320  # 20px margin + 300px width
        y = parent_rect.top() + 50  # Start from top
        
        for i, notification in enumerate(self.notifications):
            notification.move(x, y + i * 70)  # 70px spacing between notifications
    
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
        self.setFixedSize(300, 60)
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
