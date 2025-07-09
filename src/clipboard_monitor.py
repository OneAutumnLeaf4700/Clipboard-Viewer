import time
import logging
import win32clipboard
from PIL import ImageGrab
from PyQt6.QtCore import QObject, QTimer, pyqtSignal

class ClipboardItem:
    """Class to represent a clipboard item with its type, content, and timestamp."""
    
    def __init__(self, data_type, content, timestamp=None):
        from datetime import datetime
        self.data_type = data_type
        self.content = content
        self.timestamp = timestamp or datetime.now()
        self.favorite = False

class ClipboardMonitor(QObject):
    """Class to monitor clipboard changes and emit signals when changes are detected."""
    
    # Signal emitted when new clipboard content is detected
    new_content = pyqtSignal(object)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Initialize logger
        self.logger = logging.getLogger("ClipboardMonitor")
        
        # Initialize clipboard tracking variables
        self.last_clipboard_content = None
        
        # Initialize monitoring settings
        self.monitor_text = True
        self.monitor_images = True
        self.monitor_files = True
        
        # Set up timer for clipboard checking
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_clipboard)
        
    def start_monitoring(self, interval=1000):
        """Start monitoring the clipboard at the specified interval (in milliseconds)."""
        self.logger.info("Starting clipboard monitoring")
        self.timer.start(interval)
        
    def stop_monitoring(self):
        """Stop monitoring the clipboard."""
        self.logger.info("Stopping clipboard monitoring")
        self.timer.stop()
        
    def set_monitoring_options(self, monitor_text=True, monitor_images=True, monitor_files=True):
        """Set which content types to monitor."""
        self.monitor_text = monitor_text
        self.monitor_images = monitor_images
        self.monitor_files = monitor_files
        
    def check_clipboard(self):
        """Check for clipboard changes and emit signal if new content is detected."""
        data_type, current_clipboard_content = self.get_clipboard_data()
        
        # Skip if content type is not being monitored
        if data_type == "text" and not self.monitor_text:
            return
        elif data_type == "image" and not self.monitor_images:
            return
        elif data_type == "files" and not self.monitor_files:
            return
        
        # Check if the clipboard content has changed
        if (current_clipboard_content != self.last_clipboard_content and 
            current_clipboard_content is not None):
            self.last_clipboard_content = current_clipboard_content
            
            # Create new clipboard item
            new_item = ClipboardItem(data_type, current_clipboard_content)
            
            # Emit signal with new item
            self.new_content.emit(new_item)
            
            self.logger.info(f"New clipboard content ({data_type}): {str(current_clipboard_content)[:100]}...")
    
    def get_clipboard_data(self):
        """Retrieve the current clipboard content and its type."""
        try:
            win32clipboard.OpenClipboard()
            
            if win32clipboard.IsClipboardFormatAvailable(win32clipboard.CF_HDROP) and self.monitor_files:
                # Handle file paths (check this first since copied files can also have image data)
                files = win32clipboard.GetClipboardData(win32clipboard.CF_HDROP)
                win32clipboard.CloseClipboard()
                return "files", list(files)
                
            elif win32clipboard.IsClipboardFormatAvailable(win32clipboard.CF_UNICODETEXT) and self.monitor_text:
                # Handle Unicode text data
                data = win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)
                win32clipboard.CloseClipboard()
                return "text", data
                
            elif win32clipboard.IsClipboardFormatAvailable(win32clipboard.CF_BITMAP) and self.monitor_images:
                # Handle image data (actual image content, not file paths)
                win32clipboard.CloseClipboard()  # Close before using ImageGrab
                image = ImageGrab.grabclipboard()
                return "image", image
                
            else:
                win32clipboard.CloseClipboard()
                return "unknown", None
                
        except Exception as e:
            self.logger.error(f"Error retrieving clipboard data: {e}")
            try:
                win32clipboard.CloseClipboard()
            except:
                pass  # Already closed or not open
            return "error", None