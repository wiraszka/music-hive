#!/usr/bin/env python3
"""
Test GUI search functionality with debugging
"""

import sys
import os
from PyQt6.QtWidgets import QApplication
from gui.download_tab import DownloadTab
from utils.config import Config

def test_gui_search():
    """Test the GUI search functionality"""
    app = QApplication(sys.argv)
    
    # Create config
    config = Config()
    
    # Create download tab
    download_tab = DownloadTab(config)
    download_tab.show()
    
    # Simulate search
    download_tab.search_input.setText("Flume")
    print("Simulating search for 'Flume'...")
    download_tab._search()
    
    # Keep app running briefly to see results
    app.processEvents()
    
    print("Search completed")

if __name__ == "__main__":
    test_gui_search()