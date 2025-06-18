import logging
from PyQt6.QtCore import QObject, pyqtSignal
import keyboard

class HotkeyManager(QObject):
    """Class to manage global hotkeys for the application."""
    
    # Signals
    hotkey_triggered = pyqtSignal(str)  # Signal emitted when a registered hotkey is triggered
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Initialize logger
        self.logger = logging.getLogger("HotkeyManager")
        
        # Dictionary to store registered hotkeys and their callbacks
        self.registered_hotkeys = {}
    
    def register_hotkey(self, hotkey_name, key_combination, callback=None):
        """Register a global hotkey.
        
        Args:
            hotkey_name: A unique name for the hotkey
            key_combination: The key combination (e.g., "ctrl+shift+v")
            callback: Optional callback function to call when hotkey is triggered
        
        Returns:
            bool: True if registration was successful, False otherwise
        """
        try:
            # Check if hotkey is already registered
            if hotkey_name in self.registered_hotkeys:
                self.unregister_hotkey(hotkey_name)
            
            # Register the hotkey with keyboard library
            keyboard.add_hotkey(key_combination, lambda: self._on_hotkey_triggered(hotkey_name))
            
            # Store the hotkey information
            self.registered_hotkeys[hotkey_name] = {
                "key_combination": key_combination,
                "callback": callback
            }
            
            self.logger.info(f"Registered hotkey '{hotkey_name}': {key_combination}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error registering hotkey '{hotkey_name}': {e}")
            return False
    
    def unregister_hotkey(self, hotkey_name):
        """Unregister a previously registered hotkey.
        
        Args:
            hotkey_name: The unique name of the hotkey to unregister
            
        Returns:
            bool: True if unregistration was successful, False otherwise
        """
        try:
            if hotkey_name in self.registered_hotkeys:
                key_combination = self.registered_hotkeys[hotkey_name]["key_combination"]
                
                # Unregister the hotkey with keyboard library
                keyboard.remove_hotkey(key_combination)
                
                # Remove from our dictionary
                del self.registered_hotkeys[hotkey_name]
                
                self.logger.info(f"Unregistered hotkey '{hotkey_name}': {key_combination}")
                return True
            else:
                self.logger.warning(f"Attempted to unregister non-existent hotkey: {hotkey_name}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error unregistering hotkey '{hotkey_name}': {e}")
            return False
    
    def update_hotkey(self, hotkey_name, new_key_combination):
        """Update the key combination for an existing hotkey.
        
        Args:
            hotkey_name: The unique name of the hotkey to update
            new_key_combination: The new key combination
            
        Returns:
            bool: True if update was successful, False otherwise
        """
        try:
            if hotkey_name in self.registered_hotkeys:
                callback = self.registered_hotkeys[hotkey_name]["callback"]
                
                # Unregister the old hotkey
                self.unregister_hotkey(hotkey_name)
                
                # Register with the new key combination
                return self.register_hotkey(hotkey_name, new_key_combination, callback)
            else:
                self.logger.warning(f"Attempted to update non-existent hotkey: {hotkey_name}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error updating hotkey '{hotkey_name}': {e}")
            return False
    
    def _on_hotkey_triggered(self, hotkey_name):
        """Internal method called when a hotkey is triggered."""
        self.logger.info(f"Hotkey triggered: {hotkey_name}")
        
        # Emit signal with the hotkey name
        self.hotkey_triggered.emit(hotkey_name)
        
        # Call the callback if one was provided
        if hotkey_name in self.registered_hotkeys and self.registered_hotkeys[hotkey_name]["callback"]:
            self.registered_hotkeys[hotkey_name]["callback"]()
    
    def unregister_all_hotkeys(self):
        """Unregister all hotkeys."""
        try:
            # Make a copy of the keys since we'll be modifying the dictionary
            hotkey_names = list(self.registered_hotkeys.keys())
            
            for hotkey_name in hotkey_names:
                self.unregister_hotkey(hotkey_name)
            
            self.logger.info("Unregistered all hotkeys")
            return True
            
        except Exception as e:
            self.logger.error(f"Error unregistering all hotkeys: {e}")
            return False