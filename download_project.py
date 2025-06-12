#!/usr/bin/env python3
"""
Simple script to help download all project files
This creates a list of all important project files for easy download
"""

import os
import shutil
from pathlib import Path

def create_project_structure():
    """Create a clean project directory structure"""
    
    # Main project files
    main_files = [
        'main.py',
        'downloader.py', 
        'search_spotify.py',
        'search_youtube.py',
        'process_text.py',
        'README.md',
        '.gitignore'
    ]
    
    # Directories to copy
    directories = [
        'gui',
        'library', 
        'utils',
        'assets',
        'preview',
        'attached_assets'
    ]
    
    print("=== Adam's Music Downloader Project Files ===\n")
    
    print("Main Files:")
    for file in main_files:
        if os.path.exists(file):
            size = os.path.getsize(file)
            print(f"  ✓ {file} ({size} bytes)")
        else:
            print(f"  ✗ {file} (missing)")
    
    print("\nDirectories:")
    for directory in directories:
        if os.path.exists(directory):
            file_count = len(list(Path(directory).rglob('*')))
            print(f"  ✓ {directory}/ ({file_count} files)")
        else:
            print(f"  ✗ {directory}/ (missing)")
    
    print("\n=== Download Instructions ===")
    print("To download these files to your Mac:")
    print("1. Right-click on each file in the file panel on the left")
    print("2. Select 'Download' from the menu")
    print("3. For folders, download the individual files inside them")
    print("\nAlternatively:")
    print("- Use the main Replit menu (three lines) → Export/Download")
    print("- Or select multiple files and right-click → Download")
    
    return True

if __name__ == "__main__":
    create_project_structure()