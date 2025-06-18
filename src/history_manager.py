import os
import sqlite3
import pickle
import logging
from datetime import datetime, timedelta
from PyQt6.QtCore import QObject, pyqtSignal

class HistoryManager(QObject):
    """Class to manage clipboard history with database storage."""
    
    # Signal emitted when history is updated
    history_updated = pyqtSignal()
    
    def __init__(self, db_path="data/clipboard_history.db", parent=None):
        super().__init__(parent)
        
        # Initialize logger
        self.logger = logging.getLogger("HistoryManager")
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Database path
        self.db_path = db_path
        
        # Initialize database
        self.init_database()
        
        # Settings
        self.max_history_items = 1000
        self.auto_cleanup_days = 30
        
    def init_database(self):
        """Initialize the SQLite database for storing clipboard history."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create tables if they don't exist
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS clipboard_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME NOT NULL,
                    data_type TEXT NOT NULL,
                    content BLOB NOT NULL,
                    favorite BOOLEAN NOT NULL DEFAULT 0
                )
            ''')
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Database initialized at {self.db_path}")
            
        except Exception as e:
            self.logger.error(f"Error initializing database: {e}")
    
    def add_item(self, item):
        """Add a new clipboard item to the database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Serialize content using pickle
            serialized_content = pickle.dumps(item.content)
            
            # Insert new item
            cursor.execute('''
                INSERT INTO clipboard_items (timestamp, data_type, content, favorite)
                VALUES (?, ?, ?, ?)
            ''', (item.timestamp, item.data_type, serialized_content, item.favorite))
            
            conn.commit()
            
            # Check if we need to clean up old items
            self.cleanup_old_items(cursor, conn)
            
            conn.close()
            
            # Emit signal that history has been updated
            self.history_updated.emit()
            
            self.logger.info(f"Added new {item.data_type} item to history")
            
        except Exception as e:
            self.logger.error(f"Error adding item to database: {e}")
    
    def get_all_items(self, limit=None):
        """Retrieve all clipboard items from the database."""
        items = []
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Set default limit if not specified
            if limit is None:
                limit = self.max_history_items
            
            # Query items, newest first
            cursor.execute('''
                SELECT id, timestamp, data_type, content, favorite
                FROM clipboard_items
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (limit,))
            
            rows = cursor.fetchall()
            
            for row in rows:
                item_id, timestamp_str, data_type, serialized_content, favorite = row
                
                # Deserialize content
                content = pickle.loads(serialized_content)
                
                # Convert timestamp string to datetime
                timestamp = datetime.fromisoformat(timestamp_str)
                
                # Create ClipboardItem
                from clipboard_monitor import ClipboardItem
                item = ClipboardItem(data_type, content, timestamp)
                item.favorite = bool(favorite)
                item.id = item_id  # Add database ID for reference
                
                items.append(item)
            
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error retrieving items from database: {e}")
        
        return items
    
    def get_items_by_type(self, data_type, limit=None):
        """Retrieve clipboard items of a specific type from the database."""
        items = []
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Set default limit if not specified
            if limit is None:
                limit = self.max_history_items
            
            # Query items of specified type, newest first
            cursor.execute('''
                SELECT id, timestamp, data_type, content, favorite
                FROM clipboard_items
                WHERE data_type = ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (data_type, limit))
            
            rows = cursor.fetchall()
            
            for row in rows:
                item_id, timestamp_str, data_type, serialized_content, favorite = row
                
                # Deserialize content
                content = pickle.loads(serialized_content)
                
                # Convert timestamp string to datetime
                timestamp = datetime.fromisoformat(timestamp_str)
                
                # Create ClipboardItem
                from clipboard_monitor import ClipboardItem
                item = ClipboardItem(data_type, content, timestamp)
                item.favorite = bool(favorite)
                item.id = item_id  # Add database ID for reference
                
                items.append(item)
            
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error retrieving items from database: {e}")
        
        return items
    
    def get_favorites(self, limit=None):
        """Retrieve favorite clipboard items from the database."""
        items = []
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Set default limit if not specified
            if limit is None:
                limit = self.max_history_items
            
            # Query favorite items, newest first
            cursor.execute('''
                SELECT id, timestamp, data_type, content, favorite
                FROM clipboard_items
                WHERE favorite = 1
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (limit,))
            
            rows = cursor.fetchall()
            
            for row in rows:
                item_id, timestamp_str, data_type, serialized_content, favorite = row
                
                # Deserialize content
                content = pickle.loads(serialized_content)
                
                # Convert timestamp string to datetime
                timestamp = datetime.fromisoformat(timestamp_str)
                
                # Create ClipboardItem
                from clipboard_monitor import ClipboardItem
                item = ClipboardItem(data_type, content, timestamp)
                item.favorite = bool(favorite)
                item.id = item_id  # Add database ID for reference
                
                items.append(item)
            
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error retrieving favorites from database: {e}")
        
        return items
    
    def toggle_favorite(self, item_id):
        """Toggle the favorite status of an item."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get current favorite status
            cursor.execute('''
                SELECT favorite FROM clipboard_items WHERE id = ?
            ''', (item_id,))
            
            row = cursor.fetchone()
            if row:
                current_status = bool(row[0])
                
                # Toggle status
                new_status = not current_status
                
                cursor.execute('''
                    UPDATE clipboard_items
                    SET favorite = ?
                    WHERE id = ?
                ''', (new_status, item_id))
                
                conn.commit()
                conn.close()
                
                # Emit signal that history has been updated
                self.history_updated.emit()
                
                self.logger.info(f"Toggled favorite status for item {item_id} to {new_status}")
                
                return new_status
            
            conn.close()
            return None
            
        except Exception as e:
            self.logger.error(f"Error toggling favorite status: {e}")
            return None
    
    def delete_item(self, item_id):
        """Delete an item from the database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                DELETE FROM clipboard_items WHERE id = ?
            ''', (item_id,))
            
            conn.commit()
            conn.close()
            
            # Emit signal that history has been updated
            self.history_updated.emit()
            
            self.logger.info(f"Deleted item {item_id} from history")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error deleting item: {e}")
            return False
    
    def clear_history(self, keep_favorites=True):
        """Clear all history items, optionally keeping favorites."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if keep_favorites:
                cursor.execute('''
                    DELETE FROM clipboard_items WHERE favorite = 0
                ''')
            else:
                cursor.execute('''
                    DELETE FROM clipboard_items
                ''')
            
            conn.commit()
            conn.close()
            
            # Emit signal that history has been updated
            self.history_updated.emit()
            
            self.logger.info(f"Cleared history (keep_favorites={keep_favorites})")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error clearing history: {e}")
            return False
    
    def cleanup_old_items(self, cursor=None, conn=None):
        """Remove old items exceeding the maximum history size or age."""
        close_connection = False
        
        try:
            # Create connection if not provided
            if cursor is None or conn is None:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                close_connection = True
            
            # Get count of non-favorite items
            cursor.execute('''
                SELECT COUNT(*) FROM clipboard_items WHERE favorite = 0
            ''')
            
            count = cursor.fetchone()[0]
            
            # Remove oldest items if exceeding max_history_items
            if count > self.max_history_items:
                # Calculate how many to remove
                to_remove = count - self.max_history_items
                
                cursor.execute('''
                    DELETE FROM clipboard_items
                    WHERE id IN (
                        SELECT id FROM clipboard_items
                        WHERE favorite = 0
                        ORDER BY timestamp ASC
                        LIMIT ?
                    )
                ''', (to_remove,))
                
                self.logger.info(f"Removed {to_remove} old items exceeding max history size")
            
            # Remove items older than auto_cleanup_days
            if self.auto_cleanup_days > 0:
                cutoff_date = datetime.now() - timedelta(days=self.auto_cleanup_days)
                
                cursor.execute('''
                    DELETE FROM clipboard_items
                    WHERE favorite = 0 AND timestamp < ?
                ''', (cutoff_date.isoformat(),))
                
                removed_count = cursor.rowcount
                if removed_count > 0:
                    self.logger.info(f"Removed {removed_count} items older than {self.auto_cleanup_days} days")
            
            # Commit changes if we created the connection
            if close_connection:
                conn.commit()
                conn.close()
                
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
            
            # Close connection if we created it
            if close_connection and conn:
                conn.close()
    
    def set_max_history_items(self, max_items):
        """Set the maximum number of history items to keep."""
        self.max_history_items = max_items
        self.cleanup_old_items()
    
    def set_auto_cleanup_days(self, days):
        """Set the number of days after which to automatically clean up items."""
        self.auto_cleanup_days = days
        self.cleanup_old_items()
    
    def export_history(self, file_path, format_type="json"):
        """Export clipboard history to a file in the specified format."""
        items = self.get_all_items()
        
        try:
            if format_type.lower() == "json":
                import json
                
                # Convert items to serializable format
                serializable_items = []
                for item in items:
                    serialized_item = {
                        "id": getattr(item, "id", None),
                        "timestamp": item.timestamp.isoformat(),
                        "data_type": item.data_type,
                        "favorite": item.favorite
                    }
                    
                    # Handle different content types
                    if item.data_type == "text":
                        serialized_item["content"] = item.content
                    elif item.data_type == "files":
                        serialized_item["content"] = item.content
                    else:
                        # Skip binary content like images
                        serialized_item["content"] = f"[{item.data_type} data]"
                    
                    serializable_items.append(serialized_item)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(serializable_items, f, indent=2)
                
            elif format_type.lower() == "csv":
                import csv
                
                with open(file_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(["ID", "Timestamp", "Type", "Favorite", "Content"])
                    
                    for item in items:
                        # Handle different content types
                        if item.data_type == "text":
                            content = item.content
                        elif item.data_type == "files":
                            content = ", ".join(item.content)
                        else:
                            # Skip binary content like images
                            content = f"[{item.data_type} data]"
                        
                        writer.writerow([
                            getattr(item, "id", ""),
                            item.timestamp.isoformat(),
                            item.data_type,
                            "Yes" if item.favorite else "No",
                            content
                        ])
            
            self.logger.info(f"Exported history to {file_path} in {format_type} format")
            return True
            
        except Exception as e:
            self.logger.error(f"Error exporting history: {e}")
            return False