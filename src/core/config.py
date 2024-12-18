import json
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from src.utils.logger import Logger

log = Logger()

class ConfigHandler(FileSystemEventHandler):
    def __init__(self, config_manager):
        self.config_manager = config_manager

    def on_modified(self, event):
        if event.src_path == os.path.abspath(self.config_manager.config_path):
            log.debug("Configuration file modified, reloading")
            self.config_manager.load_config()
            self.config_manager.notify_observers()

class Config:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.initialized = False
        return cls._instance

    def __init__(self):
        if not self.initialized:
            log.debug("Initializing configuration manager")
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
            log.ok("Configuration manager initialized")
            self.initialized = True

    def load_config(self):
        try:
            log.debug(f"Loading configuration from {self.config_path}")
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
            log.ok("Configuration loaded successfully")
        except Exception as e:
            log.error(f"Failed to load config: {e}")

    def get(self, key, default=None):
        try:
            value = self.config
            for k in key.split('.'):
                value = value[k]
            return value
        except:
            return default

    def add_observer(self, callback):
        if callback not in self.observers:
            self.observers.append(callback)
            log.debug(f"Added configuration observer: {callback.__name__}")

    def remove_observer(self, callback):
        if callback in self.observers:
            self.observers.remove(callback)
            log.debug(f"Removed configuration observer: {callback.__name__}")

    def notify_observers(self):
        log.debug("Notifying configuration observers")
        for callback in self.observers:
            try:
                callback()
            except Exception as e:
                log.error(f"Failed to notify observer {callback.__name__}: {e}")

    def stop_observer(self):
        log.debug("Stopping configuration observer")
        self.observer.stop()
        self.observer.join()
        log.ok("Configuration observer stopped")
