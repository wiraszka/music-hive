#!/usr/bin/env python3
"""
Configuration script that includes Spotify API credentials
This script creates a config file with the necessary API keys
"""

import os
import json

def create_config_file():
    """Create configuration file with embedded credentials"""
    
    # Configuration with Spotify API credentials from Replit environment
    config_data = {
        "spotify": {
            "client_id": os.getenv('SPOTIFY_CLIENT_ID', ''),
            "client_secret": os.getenv('SPOTIFY_CLIENT_SECRET', '')
        },
        "app": {
            "name": "Adam's Music Downloader",
            "version": "2.0.0",
            "default_download_location": os.path.expanduser("~/Music/Downloads"),
            "default_library_location": os.path.expanduser("~/Music"),
            "default_audio_quality": "Best (320k)"
        }
    }
    
    # Write config to file
    with open('app_config.json', 'w') as f:
        json.dump(config_data, f, indent=2)
    
    print("Configuration file created with Spotify credentials")
    return config_data

if __name__ == "__main__":
    create_config_file()