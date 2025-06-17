import time
import logging
import win32clipboard
from PIL import ImageGrab

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

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

def main():
    logging.info("Clipboard Viewer started.")
    
    clipboard_history = []  # In-memory list to store clipboard history
    last_clipboard_content = None  # To track the last clipboard content

    try:
        while True:
            # Get the current clipboard content and type
            data_type, current_clipboard_content = get_clipboard_data()

            # Check if the clipboard content has changed
            if current_clipboard_content != last_clipboard_content:
                last_clipboard_content = current_clipboard_content

                # Add the new content to the history
                clipboard_history.append((data_type, current_clipboard_content))
                logging.info(f"New clipboard content ({data_type}): {str(current_clipboard_content)[:100]}...")

            # Simulate a delay to avoid excessive CPU usage
            time.sleep(1)

    except KeyboardInterrupt:
        # Gracefully handle program termination
        logging.info("Program terminated by user.")
        logging.info("Clipboard history:")
        for index, (data_type, content) in enumerate(clipboard_history, start=1):
            logging.info(f"{index}: ({data_type}) {content}")

    except Exception as e:
        logging.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()