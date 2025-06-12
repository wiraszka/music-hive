#!/usr/bin/env python3
"""
Quick setup script for Adam's Music Downloader
Automatically installs dependencies and guides through API setup
"""

import os
import sys
import subprocess
import webbrowser

def install_dependencies():
    """Install required packages"""
    packages = ["PyQt6", "yt-dlp", "mutagen", "spotipy", "requests"]
    
    print("Installing dependencies...")
    for package in packages:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package], 
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"✓ {package}")
        except subprocess.CalledProcessError:
            print(f"✗ Failed to install {package}")
            return False
    return True

def setup_spotify_credentials():
    """Guide user through Spotify API setup"""
    print("\nSpotify API Setup Required:")
    print("1. Opening Spotify Developer Dashboard...")
    
    try:
        webbrowser.open("https://developer.spotify.com/dashboard")
    except:
        print("Please visit: https://developer.spotify.com/dashboard")
    
    print("\n2. Create a new app with these settings:")
    print("   - App name: Music Downloader")
    print("   - Description: Personal music app")
    print("   - Redirect URI: http://localhost:8080/callback")
    
    print("\n3. Copy your credentials:")
    client_id = input("Enter your Client ID: ").strip()
    client_secret = input("Enter your Client Secret: ").strip()
    
    if not client_id or not client_secret:
        print("Invalid credentials provided")
        return False
    
    # Set environment variables for this session
    os.environ['SPOTIFY_CLIENT_ID'] = client_id
    os.environ['SPOTIFY_CLIENT_SECRET'] = client_secret
    
    # Save to shell profile for future sessions
    shell_profile = os.path.expanduser("~/.zshrc")
    if not os.path.exists(shell_profile):
        shell_profile = os.path.expanduser("~/.bash_profile")
    
    with open(shell_profile, "a") as f:
        f.write(f'\nexport SPOTIFY_CLIENT_ID="{client_id}"\n')
        f.write(f'export SPOTIFY_CLIENT_SECRET="{client_secret}"\n')
    
    print(f"✓ Credentials saved to {shell_profile}")
    return True

def main():
    print("Adam's Music Downloader - Quick Setup")
    print("=" * 40)
    
    # Install dependencies
    if not install_dependencies():
        print("Setup failed - could not install dependencies")
        return 1
    
    # Setup Spotify credentials
    if not setup_spotify_credentials():
        print("Setup incomplete - Spotify credentials required")
        return 1
    
    print("\n✓ Setup complete!")
    print("\nStarting application...")
    
    # Create default directories
    os.makedirs(os.path.expanduser("~/Music/Downloads"), exist_ok=True)
    
    # Run the application
    try:
        subprocess.run([sys.executable, "main.py"])
    except FileNotFoundError:
        print("Error: main.py not found in current directory")
        print("Make sure you're in the project folder")
        return 1
    except KeyboardInterrupt:
        print("\nApplication closed")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())