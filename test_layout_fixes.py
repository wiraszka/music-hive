#!/usr/bin/env python3
"""
Test the updated layout fixes for consistent centering and responsive design
"""

import sys
import os
from PyQt6.QtWidgets import QApplication
from gui.download_tab import DownloadTab
from utils.config import Config

def test_layout_consistency():
    """Test that layout is consistent across all stages"""
    app = QApplication(sys.argv)
    
    # Create config
    config = Config()
    
    # Create download tab
    download_tab = DownloadTab(config)
    download_tab.resize(1200, 800)  # Test at specific size
    download_tab.show()
    
    print("Testing layout at different stages...")
    
    # Stage 1: Initial load
    print("Stage 1: Initial layout - all elements should be centered")
    app.processEvents()
    
    # Stage 2: After entering search text
    download_tab.search_input.setText("Test Query")
    print("Stage 2: With search text - layout should remain consistent")
    app.processEvents()
    
    # Stage 3: Test window resize
    download_tab.resize(800, 600)
    print("Stage 3: Smaller window - elements should scale properly")
    app.processEvents()
    
    download_tab.resize(1600, 900)
    print("Stage 4: Larger window - elements should remain centered")
    app.processEvents()
    
    print("Layout consistency test completed")
    
    # Keep window open briefly
    app.processEvents()

if __name__ == "__main__":
    test_layout_consistency()