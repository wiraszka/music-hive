#!/usr/bin/env python3
"""
Music Downloader & Library Manager
Author: Adam Wiraszka
https://github.com/wiraszka/music-downloader

An application for downloading music from YouTube, with Spotify metadata integration
and a local music library manager.
"""

import os
import sys
import logging
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QDir

from gui.main_window import MainWindow
from utils.config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def main():
    """Main application entry point"""
    try:
        # Create application instance
        app = QApplication(sys.argv)
        app.setApplicationName("Music Downloader & Library Manager")
        
        # Set working directory to the script location
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        
        # Load application configuration
        config = Config()
        
        # Define default download location if not set
        if not config.download_location:
            home_dir = QDir.homePath()
            music_dir = os.path.join(home_dir, "Music")
            if not os.path.exists(music_dir):
                os.makedirs(music_dir)
            config.download_location = music_dir
            config.save()
        
        # Create main window
        window = MainWindow(config)
        window.show()
        
        # Start the application event loop
        sys.exit(app.exec())
        
    except Exception as e:
        logger.error(f"Application error: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
