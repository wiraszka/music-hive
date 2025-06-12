#!/usr/bin/env python3
"""
Easy setup script for Adam's Music Downloader
Includes all necessary configuration and credentials
"""

import os
import sys
import subprocess

def main():
    print("Setting up Adam's Music Downloader...")
    
    # Set environment variables for this session
    os.environ['SPOTIFY_CLIENT_ID'] = '4f6b5c8d2e9a1b7c3f0e5d8a2b6c9e1f'
    os.environ['SPOTIFY_CLIENT_SECRET'] = 'a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6'
    
    # Install dependencies
    packages = ["PyQt6", "yt-dlp", "mutagen", "spotipy", "requests"]
    
    for package in packages:
        print(f"Installing {package}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package], 
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"✓ {package} installed")
        except subprocess.CalledProcessError:
            print(f"✗ Failed to install {package}")
            return 1
    
    print("\n✓ Setup complete!")
    print("Starting application...")
    
    # Run the application
    try:
        subprocess.run([sys.executable, "main.py"])
    except FileNotFoundError:
        print("Error: main.py not found. Make sure you're in the correct directory.")
        return 1
    except KeyboardInterrupt:
        print("\nApplication closed.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())