"""
Configuration management module
"""

import os
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class Config:
    """Class to handle application configuration"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration
        
        Args:
            config_path: Optional path to configuration file
        """
        # Default config path in user's home directory
        if config_path is None:
            home_dir = os.path.expanduser("~")
            self.config_path = os.path.join(home_dir, ".music_downloader_config.json")
        else:
            self.config_path = config_path
        
        # Default configuration
        self.default_config = {
            "download_location": os.path.join(os.path.expanduser("~"), "Music"),
            "music_dir": "",
            "last_used_quality": "320k",
            "default_audio_quality": "320k",
            "auto_scan_library": True,
            "spotify_enabled": True
        }
        
        # Current configuration
        self.config = self.default_config.copy()
        
        # Load configuration
        self.load()
    
    def load(self) -> bool:
        """
        Load configuration from file
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    loaded_config = json.load(f)
                    
                    # Update config with loaded values
                    self.config.update(loaded_config)
                    
                    return True
            else:
                # If config doesn't exist, create it with default values
                return self.save()
                
        except Exception as e:
            logger.error(f"Failed to load configuration: {str(e)}")
            return False
    
    def save(self) -> bool:
        """
        Save configuration to file
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=4)
                
            return True
            
        except Exception as e:
            logger.error(f"Failed to save configuration: {str(e)}")
            return False
    
    def reset(self) -> bool:
        """
        Reset configuration to defaults
        
        Returns:
            True if successful, False otherwise
        """
        self.config = self.default_config.copy()
        return self.save()
    
    @property
    def download_location(self) -> str:
        """Get download location"""
        return self.config.get("download_location", self.default_config["download_location"])
    
    @download_location.setter
    def download_location(self, value: str):
        """Set download location"""
        self.config["download_location"] = value
    
    @property
    def music_dir(self) -> str:
        """Get music directory"""
        return self.config.get("music_dir", self.default_config["music_dir"])
    
    @music_dir.setter
    def music_dir(self, value: str):
        """Set music directory"""
        self.config["music_dir"] = value
    
    @property
    def last_used_quality(self) -> str:
        """Get last used quality"""
        return self.config.get("last_used_quality", self.default_config["last_used_quality"])
    
    @last_used_quality.setter
    def last_used_quality(self, value: str):
        """Set last used quality"""
        self.config["last_used_quality"] = value
        
    @property
    def default_audio_quality(self) -> str:
        """Get default audio quality"""
        return self.config.get("default_audio_quality", self.default_config["default_audio_quality"])
    
    @default_audio_quality.setter
    def default_audio_quality(self, value: str):
        """Set default audio quality"""
        self.config["default_audio_quality"] = value
    
    @property
    def auto_scan_library(self) -> bool:
        """Get auto scan library flag"""
        return self.config.get("auto_scan_library", self.default_config["auto_scan_library"])
    
    @auto_scan_library.setter
    def auto_scan_library(self, value: bool):
        """Set auto scan library flag"""
        self.config["auto_scan_library"] = value
    
    @property
    def spotify_enabled(self) -> bool:
        """Get Spotify enabled flag"""
        return self.config.get("spotify_enabled", self.default_config["spotify_enabled"])
    
    @spotify_enabled.setter
    def spotify_enabled(self, value: bool):
        """Set Spotify enabled flag"""
        self.config["spotify_enabled"] = value
