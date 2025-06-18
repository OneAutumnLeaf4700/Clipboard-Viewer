import logging
import win32clipboard
from PIL import ImageGrab

def get_clipboard_data():
    """Retrieve the current clipboard content and its type."""
    win32clipboard.OpenClipboard()
    try:
        if win32clipboard.IsClipboardFormatAvailable(win32clipboard.CF_UNICODETEXT):
            # Handle Unicode text data
            data = win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)
            return "text", data
        elif win32clipboard.IsClipboardFormatAvailable(win32clipboard.CF_BITMAP):
            # Handle image data
            image = ImageGrab.grabclipboard()
            return "image", image
        elif win32clipboard.IsClipboardFormatAvailable(win32clipboard.CF_HDROP):
            # Handle file paths
            files = win32clipboard.GetClipboardData(win32clipboard.CF_HDROP)
            return "files", list(files)
        else:
            return "unknown", None
    except Exception as e:
        logging.error(f"Error retrieving clipboard data: {e}")
        return "error", None
    finally:
        win32clipboard.CloseClipboard()