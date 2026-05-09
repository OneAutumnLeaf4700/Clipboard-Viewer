import logging
import sys
from PIL import ImageGrab
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QMimeData

def get_clipboard_data():
    """Retrieve the current clipboard content and its type in a cross-platform way."""
    try:
        app = QApplication.instance()
        if not app:
            return "error", "QApplication not initialized"
            
        clipboard = app.clipboard()
        mime_data = clipboard.mimeData()
        
        if mime_data.hasUrls():
            # Handle file paths
            files = [url.toLocalFile() for url in mime_data.urls() if url.isLocalFile()]
            if files:
                return "files", files
                
        if mime_data.hasImage():
            # Handle image data
            from PyQt6.QtGui import QImage
            qimage = clipboard.image()
            if not qimage.isNull():
                # Convert QImage to PIL Image for consistency if needed, 
                # or just return the QImage/Pixmap. 
                # The rest of the app seems to expect PIL Image based on previous code.
                import io
                from PIL import Image
                buffer = io.BytesIO()
                qimage.save(buffer, "PNG")
                image = Image.open(buffer)
                return "image", image
                
        if mime_data.hasText():
            # Handle text data
            return "text", mime_data.text()
            
        return "unknown", None
        
    except Exception as e:
        logging.error(f"Error retrieving clipboard data: {e}")
        return "error", None