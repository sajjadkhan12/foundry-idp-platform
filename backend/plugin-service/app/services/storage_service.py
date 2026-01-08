"""Storage service for plugin artifacts"""
import os
import shutil
from pathlib import Path
from typing import BinaryIO
from app.config import settings


class StorageService:
    """Service for storing plugin artifacts"""
    
    def __init__(self):
        self.base_path = Path(settings.PLUGINS_STORAGE_PATH)
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    def save_plugin(self, plugin_id: str, version: str, file_content: bytes) -> str:
        """
        Save a plugin ZIP file
        Returns the storage path
        """
        plugin_dir = self.base_path / plugin_id / version
        plugin_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = plugin_dir / "plugin.zip"
        
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        return str(file_path)
    
    def get_plugin_path(self, plugin_id: str, version: str) -> Path:
        """Get the path to a plugin ZIP file"""
        return self.base_path / plugin_id / version / "plugin.zip"
    
    def delete_plugin(self, plugin_id: str, version: str):
        """Delete a plugin version"""
        plugin_dir = self.base_path / plugin_id / version
        if plugin_dir.exists():
            shutil.rmtree(plugin_dir)


# Singleton instance
storage_service = StorageService()
