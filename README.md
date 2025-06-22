# Clipboard Viewer

A Python application that monitors and maintains a history of all clipboard content, allowing you to view, search, and restore any previously copied item.

## Features

- **Real-time Clipboard Monitoring**: Automatically captures all clipboard changes
- **History Management**: View chronological list of all copied items
- **Multi-format Support**: 
  - Plain text
  - Rich text/HTML
  - Images (PNG, JPEG, etc.)
  - File paths
  - Custom formats
- **Search & Filter**: Find specific clipboard entries quickly
- **Favorites System**: Pin frequently used items
- **Export/Import**: Backup and restore clipboard history
- **System Tray Integration**: Run in background with minimal UI footprint
- **Hotkey Access**: Quick access with customizable keyboard shortcuts

## Technical Details

- **Language**: Python 3.8+
- **GUI Framework**: PyQt6
- **Platform**: Windows (with potential cross-platform support)
- **Database**: SQLite for history storage
- **Dependencies**: See `requirements.txt`

## Project Structure

```
Clipboard Viewer/
├── src/
│   ├── main.py              # Application entry point
│   ├── clipboard_monitor.py # Clipboard monitoring service
│   ├── history_manager.py   # History storage and retrieval
│   ├── gui/
│   │   ├── __init__.py
│   │   ├── main_window.py   # Main application window
│   │   ├── history_view.py  # Clipboard history display
│   │   ├── search_dialog.py # Search and filter interface
│   │   └── settings_dialog.py # Application settings
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── database.py      # SQLite database operations
│   │   ├── hotkeys.py       # Global hotkey management
│   │   └── system_tray.py   # System tray integration
│   └── models/
│       ├── __init__.py
│       └── clipboard_item.py # Clipboard item data model
├── assets/
│   ├── icons/               # Application icons
│   └── styles/              # QSS stylesheets
├── data/                    # User data directory
├── requirements.txt         # Python dependencies
├── setup.py                # Installation script
└── README.md
```

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd "Clipboard Viewer"
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python src/main.py
   ```

## Usage

1. **Start the application** - it will begin monitoring clipboard automatically
2. **View history** - Click the system tray icon or use the hotkey (default: Ctrl+Shift+V)
3. **Copy items** - Double-click any history item to copy it back to clipboard
4. **Search** - Use the search bar to find specific content
5. **Manage favorites** - Right-click items to add/remove from favorites
6. **Settings** - Configure hotkeys, history limits, and data retention

## Features in Detail

### Clipboard Monitoring
- Monitors clipboard changes in real-time
- Captures text, images, and file paths
- Handles multiple clipboard formats simultaneously
- Optional duplicate detection and filtering

### History Management
- Persistent storage using SQLite database
- Configurable history size limits
- Automatic cleanup of old entries
- Export history to various formats (JSON, CSV, HTML)

### User Interface
- Clean, modern PyQt6 interface
- Dark/light theme support
- Resizable columns and customizable layout
- Preview pane for images and formatted text
- Drag-and-drop support

### Privacy & Security
- Optional encryption for sensitive data
- Configurable data retention periods
- Exclude specific applications from monitoring
- Password protection for application access

## Configuration

The application stores settings in `data/config.json`:

```json
{
  "hotkey": "Ctrl+Shift+V",
  "max_history_items": 1000,
  "auto_cleanup_days": 30,
  "monitor_images": true,
  "monitor_files": true,
  "exclude_apps": ["KeePass", "1Password"],
  "theme": "system"
}
```

## Requirements

- Python 3.8 or higher
- Windows 10+ (primary target)
- 50MB free disk space for history storage
- Internet connection for initial setup only
