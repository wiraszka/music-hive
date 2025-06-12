#!/usr/bin/env python3
"""
Automatic setup script for Adam's Music Downloader
Includes embedded credentials and installs everything automatically
"""

import os
import sys
import subprocess

def main():
    print("Setting up Adam's Music Downloader...")
    
    # Set Spotify API credentials directly in environment
    os.environ['SPOTIFY_CLIENT_ID'] = 'd8d22be2095f480591ce7de628699e26'
    os.environ['SPOTIFY_CLIENT_SECRET'] = '71fbff9545254217b40e800f222cba84'
    
    # Install dependencies silently
    packages = ["PyQt6", "yt-dlp", "mutagen", "spotipy", "requests"]
    
    print("Installing dependencies...")
    for package in packages:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package], 
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"✓ {package}")
        except subprocess.CalledProcessError:
            print(f"✗ Failed to install {package}")
            return 1
    
    # Create default directories
    download_dir = os.path.expanduser("~/Music/Downloads")
    os.makedirs(download_dir, exist_ok=True)
    print(f"✓ Created download directory: {download_dir}")
    
    print("\n✅ Setup complete!")
    print("Launching application...")
    
    # Launch the application
    try:
        subprocess.run([sys.executable, "main.py"])
    except FileNotFoundError:
        print("Error: main.py not found. Make sure you're in the project directory.")
        return 1
    except KeyboardInterrupt:
        print("\nApplication closed.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())