import json
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ConfigHandler(FileSystemEventHandler):
    """Handles real-time config file changes"""
    def __init__(self, config_manager):
        self.config_manager = config_manager

    def on_modified(self, event):
        if event.src_path == os.path.abspath(self.config_manager.config_path):
            self.config_manager.load_config()
            self.config_manager.notify_observers()

class Config:
    """Configuration manager with real-time update capability"""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.initialized = False
        return cls._instance

    def __init__(self):
        if not self.initialized:
            base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            self.config_path = os.path.join(base_path, 'config', 'settings.json')
            self.config = {}
            self.observers = []
            self.load_config()
            
            self.observer = Observer()
            self.observer.schedule(
                ConfigHandler(self),
                path=os.path.dirname(os.path.abspath(self.config_path)),
                recursive=False
            )
            self.observer.start()
            self.initialized = True

    def load_config(self):
        """Load configuration from file"""
        try:
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")

    def get(self, key, default=None):
        """Get configuration value"""
        try:
            value = self.config
            for k in key.split('.'):
                value = value[k]
            return value
        except:
            return default

    def add_observer(self, callback):
        """Add callback to be notified of config changes"""
        if callback not in self.observers:
            self.observers.append(callback)

    def remove_observer(self, callback):
        """Remove callback from observers"""
        if callback in self.observers:
            self.observers.remove(callback)

    def notify_observers(self):
        """Notify all observers of config change"""
        for callback in self.observers:
            try:
                callback()
            except Exception as e:
                print(f"Error notifying observer: {e}")

    def stop_observer(self):
        """Stop watching config file"""
        self.observer.stop()
        self.observer.join()
