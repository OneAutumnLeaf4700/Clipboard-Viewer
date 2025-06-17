import time
import logging
import pyperclip

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def main():
    logging.info("Clipboard Viewer started.")
    
    clipboard_history = []  # In-memory list to store clipboard history
    last_clipboard_content = None  # To track the last clipboard content

    try:
        while True:
            # Get the current clipboard content
            current_clipboard_content = pyperclip.paste()

            # Check if the clipboard content has changed
            if current_clipboard_content != last_clipboard_content:
                last_clipboard_content = current_clipboard_content

                # Add the new content to the history
                clipboard_history.append(current_clipboard_content)
                logging.info(f"New clipboard content: {current_clipboard_content}")

            # Simulate a delay to avoid excessive CPU usage
            time.sleep(1)

    except KeyboardInterrupt:
        # Gracefully handle program termination
        logging.info("Program terminated by user.")
        logging.info("Clipboard history:")
        for index, content in enumerate(clipboard_history, start=1):
            logging.info(f"{index}: {content}")

    except Exception as e:
        logging.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()