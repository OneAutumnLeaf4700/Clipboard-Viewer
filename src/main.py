import logging
import pyperclip

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    logging.info("Clipboard Viewer started.")
    try:
        # Get clipboard content
        clipboard_content = pyperclip.paste()
        logging.info(f"Clipboard content: {clipboard_content}")
    except Exception as e:
        logging.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()