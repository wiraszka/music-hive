#!/usr/bin/env python3
"""
Test script to verify navigation functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_navigation_structure():
    """Test that navigation components are properly structured"""
    
    print("=== Navigation Test ===\n")
    
    # Test main window structure
    print("Testing MainWindow structure...")
    try:
        from gui.main_window import MainWindow
        from utils.config import Config
        
        # Create test config
        config = Config()
        
        print("✓ MainWindow import successful")
        print("✓ Config import successful")
        
        # Test that the main window has the expected methods
        required_methods = [
            '_create_sidebar',
            '_create_sidebar_button', 
            '_on_sidebar_button_clicked',
            '_set_active_button'
        ]
        
        for method in required_methods:
            if hasattr(MainWindow, method):
                print(f"✓ Method {method} exists")
            else:
                print(f"✗ Method {method} missing")
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    
    print("\nTesting tab components...")
    
    # Test download tab
    try:
        from gui.download_tab import DownloadTab
        print("✓ DownloadTab import successful")
    except ImportError as e:
        print(f"✗ DownloadTab import error: {e}")
    
    # Test library tab  
    try:
        from gui.library_tab import LibraryTab
        print("✓ LibraryTab import successful")
    except ImportError as e:
        print(f"✗ LibraryTab import error: {e}")
    
    print("\nTesting styling...")
    
    # Test styling
    try:
        from gui.style import get_stylesheet, Theme
        stylesheet = get_stylesheet(Theme.DARK)
        
        # Check for sidebar button styles
        if "sidebar_button" in stylesheet:
            print("✓ Sidebar button styling found")
        else:
            print("✗ Sidebar button styling missing")
            
        # Check for light gray colors
        if "#cccccc" in stylesheet:
            print("✓ Light gray color scheme applied")
        else:
            print("✗ Light gray colors not found")
            
    except ImportError as e:
        print(f"✗ Style import error: {e}")
    
    print("\n=== Navigation Structure Complete ===")
    print("\nExpected behavior when running locally:")
    print("1. Application starts with Download tab active")
    print("2. Clicking 'Library' tab switches to library view")
    print("3. Clicking 'Settings' tab shows settings page")
    print("4. Clicking 'About' tab shows about information")
    print("5. Active tab has light gray border highlight")
    print("6. All buttons use light gray (#cccccc) color scheme")
    
    return True

if __name__ == "__main__":
    test_navigation_structure()