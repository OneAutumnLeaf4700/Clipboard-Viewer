import os
import sqlite3
import logging
from datetime import datetime

class DatabaseManager:
    """Class to manage SQLite database operations for the clipboard history."""
    
    def __init__(self, db_path="data/clipboard_history.db"):
        # Initialize logger
        self.logger = logging.getLogger("DatabaseManager")
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Database path
        self.db_path = db_path
        
        # Initialize database
        self.init_database()
    
    def init_database(self):
        """Initialize the SQLite database and create tables if they don't exist."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Create clipboard_items table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS clipboard_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME NOT NULL,
                    data_type TEXT NOT NULL,
                    content BLOB NOT NULL,
                    favorite BOOLEAN NOT NULL DEFAULT 0
                )
            ''')
            
            # Create settings table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
            ''')
            
            # Create tags table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tags (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE
                )
            ''')
            
            # Create item_tags table (many-to-many relationship)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS item_tags (
                    item_id INTEGER,
                    tag_id INTEGER,
                    PRIMARY KEY (item_id, tag_id),
                    FOREIGN KEY (item_id) REFERENCES clipboard_items (id) ON DELETE CASCADE,
                    FOREIGN KEY (tag_id) REFERENCES tags (id) ON DELETE CASCADE
                )
            ''')
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Database initialized at {self.db_path}")
            
        except Exception as e:
            self.logger.error(f"Error initializing database: {e}")
    
    def get_connection(self):
        """Get a connection to the SQLite database."""
        try:
            # Enable foreign key constraints
            conn = sqlite3.connect(self.db_path)
            conn.execute("PRAGMA foreign_keys = ON")
            return conn
        except Exception as e:
            self.logger.error(f"Error connecting to database: {e}")
            raise
    
    def execute_query(self, query, params=(), fetch_mode=None):
        """Execute a SQL query and optionally fetch results.
        
        Args:
            query: The SQL query to execute
            params: Parameters for the query
            fetch_mode: None, 'one', 'all', or 'cursor'
            
        Returns:
            Depending on fetch_mode:
            - None: None (for INSERT, UPDATE, DELETE)
            - 'one': A single row
            - 'all': All rows
            - 'cursor': The cursor object (caller must close the connection)
        """
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute(query, params)
            
            if fetch_mode == 'one':
                result = cursor.fetchone()
                conn.close()
                return result
            elif fetch_mode == 'all':
                result = cursor.fetchall()
                conn.close()
                return result
            elif fetch_mode == 'cursor':
                # Caller is responsible for closing the connection
                return conn, cursor
            else:
                # For INSERT, UPDATE, DELETE
                conn.commit()
                conn.close()
                return None
                
        except Exception as e:
            self.logger.error(f"Error executing query: {e}\nQuery: {query}\nParams: {params}")
            if conn:
                conn.close()
            raise
    
    def insert_item(self, data_type, content, timestamp=None, favorite=False):
        """Insert a new clipboard item into the database.
        
        Args:
            data_type: Type of clipboard data (text, image, files, etc.)
            content: The serialized clipboard content
            timestamp: Optional timestamp (defaults to current time)
            favorite: Whether the item is marked as favorite
            
        Returns:
            The ID of the inserted item, or None if insertion failed
        """
        try:
            if timestamp is None:
                timestamp = datetime.now()
                
            timestamp_str = timestamp.isoformat()
            
            conn, cursor = self.execute_query(
                "INSERT INTO clipboard_items (timestamp, data_type, content, favorite) VALUES (?, ?, ?, ?)",
                (timestamp_str, data_type, content, favorite),
                fetch_mode='cursor'
            )
            
            # Get the ID of the inserted item
            item_id = cursor.lastrowid
            
            conn.commit()
            conn.close()
            
            return item_id
            
        except Exception as e:
            self.logger.error(f"Error inserting clipboard item: {e}")
            return None
    
    def get_items(self, limit=None, offset=0, data_type=None, favorites_only=False):
        """Get clipboard items from the database with optional filtering.
        
        Args:
            limit: Maximum number of items to retrieve
            offset: Number of items to skip
            data_type: Filter by data type
            favorites_only: Only retrieve favorite items
            
        Returns:
            List of tuples containing item data
        """
        try:
            query = "SELECT id, timestamp, data_type, content, favorite FROM clipboard_items"
            params = []
            
            # Add WHERE clauses for filtering
            where_clauses = []
            
            if data_type:
                where_clauses.append("data_type = ?")
                params.append(data_type)
                
            if favorites_only:
                where_clauses.append("favorite = 1")
            
            if where_clauses:
                query += " WHERE " + " AND ".join(where_clauses)
            
            # Add ORDER BY and LIMIT clauses
            query += " ORDER BY timestamp DESC"
            
            if limit is not None:
                query += " LIMIT ? OFFSET ?"
                params.extend([limit, offset])
            
            return self.execute_query(query, tuple(params), fetch_mode='all')
            
        except Exception as e:
            self.logger.error(f"Error retrieving clipboard items: {e}")
            return []
    
    def get_item_by_id(self, item_id):
        """Get a clipboard item by its ID.
        
        Args:
            item_id: The ID of the item to retrieve
            
        Returns:
            Tuple containing item data, or None if not found
        """
        try:
            return self.execute_query(
                "SELECT id, timestamp, data_type, content, favorite FROM clipboard_items WHERE id = ?",
                (item_id,),
                fetch_mode='one'
            )
            
        except Exception as e:
            self.logger.error(f"Error retrieving clipboard item {item_id}: {e}")
            return None
    
    def update_item(self, item_id, **kwargs):
        """Update a clipboard item in the database.
        
        Args:
            item_id: The ID of the item to update
            **kwargs: Fields to update (data_type, content, favorite)
            
        Returns:
            bool: True if update was successful, False otherwise
        """
        try:
            # Build the SET clause and parameters
            set_clauses = []
            params = []
            
            for field, value in kwargs.items():
                if field in ['data_type', 'content', 'favorite']:
                    set_clauses.append(f"{field} = ?")
                    params.append(value)
            
            if not set_clauses:
                return False  # Nothing to update
            
            # Add the item_id parameter
            params.append(item_id)
            
            # Execute the update query
            self.execute_query(
                f"UPDATE clipboard_items SET {', '.join(set_clauses)} WHERE id = ?",
                tuple(params)
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating clipboard item {item_id}: {e}")
            return False
    
    def delete_item(self, item_id):
        """Delete a clipboard item from the database.
        
        Args:
            item_id: The ID of the item to delete
            
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        try:
            self.execute_query(
                "DELETE FROM clipboard_items WHERE id = ?",
                (item_id,)
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error deleting clipboard item {item_id}: {e}")
            return False
    
    def clear_history(self, keep_favorites=True):
        """Clear clipboard history, optionally keeping favorites.
        
        Args:
            keep_favorites: Whether to keep favorite items
            
        Returns:
            bool: True if clearing was successful, False otherwise
        """
        try:
            if keep_favorites:
                self.execute_query("DELETE FROM clipboard_items WHERE favorite = 0")
            else:
                self.execute_query("DELETE FROM clipboard_items")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error clearing clipboard history: {e}")
            return False
    
    def get_setting(self, key, default=None):
        """Get a setting from the database.
        
        Args:
            key: The setting key
            default: Default value if setting is not found
            
        Returns:
            The setting value, or the default if not found
        """
        try:
            result = self.execute_query(
                "SELECT value FROM settings WHERE key = ?",
                (key,),
                fetch_mode='one'
            )
            
            return result[0] if result else default
            
        except Exception as e:
            self.logger.error(f"Error retrieving setting {key}: {e}")
            return default
    
    def set_setting(self, key, value):
        """Set a setting in the database.
        
        Args:
            key: The setting key
            value: The setting value
            
        Returns:
            bool: True if setting was successful, False otherwise
        """
        try:
            # Use REPLACE to insert or update
            self.execute_query(
                "REPLACE INTO settings (key, value) VALUES (?, ?)",
                (key, str(value))
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error setting {key} to {value}: {e}")
            return False
    
    def add_tag(self, tag_name):
        """Add a new tag to the database.
        
        Args:
            tag_name: The name of the tag
            
        Returns:
            The ID of the inserted tag, or None if insertion failed
        """
        try:
            # Check if tag already exists
            existing_tag = self.execute_query(
                "SELECT id FROM tags WHERE name = ?",
                (tag_name,),
                fetch_mode='one'
            )
            
            if existing_tag:
                return existing_tag[0]  # Return existing tag ID
            
            # Insert new tag
            conn, cursor = self.execute_query(
                "INSERT INTO tags (name) VALUES (?)",
                (tag_name,),
                fetch_mode='cursor'
            )
            
            tag_id = cursor.lastrowid
            
            conn.commit()
            conn.close()
            
            return tag_id
            
        except Exception as e:
            self.logger.error(f"Error adding tag {tag_name}: {e}")
            return None
    
    def tag_item(self, item_id, tag_id):
        """Associate a tag with a clipboard item.
        
        Args:
            item_id: The ID of the clipboard item
            tag_id: The ID of the tag
            
        Returns:
            bool: True if tagging was successful, False otherwise
        """
        try:
            # Use REPLACE to handle case where the association already exists
            self.execute_query(
                "REPLACE INTO item_tags (item_id, tag_id) VALUES (?, ?)",
                (item_id, tag_id)
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error tagging item {item_id} with tag {tag_id}: {e}")
            return False
    
    def untag_item(self, item_id, tag_id):
        """Remove a tag association from a clipboard item.
        
        Args:
            item_id: The ID of the clipboard item
            tag_id: The ID of the tag
            
        Returns:
            bool: True if untagging was successful, False otherwise
        """
        try:
            self.execute_query(
                "DELETE FROM item_tags WHERE item_id = ? AND tag_id = ?",
                (item_id, tag_id)
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error removing tag {tag_id} from item {item_id}: {e}")
            return False
    
    def get_item_tags(self, item_id):
        """Get all tags associated with a clipboard item.
        
        Args:
            item_id: The ID of the clipboard item
            
        Returns:
            List of tuples containing tag data (id, name)
        """
        try:
            return self.execute_query(
                """SELECT t.id, t.name 
                   FROM tags t 
                   JOIN item_tags it ON t.id = it.tag_id 
                   WHERE it.item_id = ?
                   ORDER BY t.name""",
                (item_id,),
                fetch_mode='all'
            )
            
        except Exception as e:
            self.logger.error(f"Error retrieving tags for item {item_id}: {e}")
            return []
    
    def get_all_tags(self):
        """Get all tags in the database.
        
        Returns:
            List of tuples containing tag data (id, name)
        """
        try:
            return self.execute_query(
                "SELECT id, name FROM tags ORDER BY name",
                fetch_mode='all'
            )
            
        except Exception as e:
            self.logger.error(f"Error retrieving all tags: {e}")
            return []
    
    def search_items(self, search_text, data_type=None, favorites_only=False, tag_id=None, limit=None):
        """Search for clipboard items matching the given criteria.
        
        Args:
            search_text: Text to search for in item content
            data_type: Filter by data type
            favorites_only: Only retrieve favorite items
            tag_id: Filter by tag ID
            limit: Maximum number of items to retrieve
            
        Returns:
            List of tuples containing item data
        """
        try:
            query = "SELECT DISTINCT ci.id, ci.timestamp, ci.data_type, ci.content, ci.favorite FROM clipboard_items ci"
            params = []
            
            # Join with item_tags if filtering by tag
            if tag_id is not None:
                query += " JOIN item_tags it ON ci.id = it.item_id"
            
            # Add WHERE clauses for filtering
            where_clauses = []
            
            # Add search text condition (only for text items)
            if search_text:
                where_clauses.append("(ci.data_type = 'text' AND ci.content LIKE ?)")
                params.append(f"%{search_text}%")
            
            if data_type:
                where_clauses.append("ci.data_type = ?")
                params.append(data_type)
                
            if favorites_only:
                where_clauses.append("ci.favorite = 1")
                
            if tag_id is not None:
                where_clauses.append("it.tag_id = ?")
                params.append(tag_id)
            
            if where_clauses:
                query += " WHERE " + " AND ".join(where_clauses)
            
            # Add ORDER BY and LIMIT clauses
            query += " ORDER BY ci.timestamp DESC"
            
            if limit is not None:
                query += " LIMIT ?"
                params.append(limit)
            
            return self.execute_query(query, tuple(params), fetch_mode='all')
            
        except Exception as e:
            self.logger.error(f"Error searching clipboard items: {e}")
            return []