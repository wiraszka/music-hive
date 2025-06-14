#!/usr/bin/env python3
"""
Easy setup script for Adam's Music Downloader
Includes all necessary configuration and credentials
"""

import os
import sys
import subprocess

def install_homebrew_macos():
    """Install Homebrew on macOS"""
    try:
        print("Installing Homebrew... (this may take a few minutes)")
        install_cmd = [
            "/bin/bash", "-c", 
            "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        ]
        subprocess.check_call(install_cmd)
        
        # Add to PATH
        import os
        homebrew_paths = ["/opt/homebrew/bin", "/usr/local/bin"]
        current_path = os.environ.get("PATH", "")
        for path in homebrew_paths:
            if path not in current_path and os.path.exists(path):
                os.environ["PATH"] = f"{path}:{current_path}"
        
        print("✓ Homebrew installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("Failed to install Homebrew automatically")
        return False

def check_and_install_ffmpeg():
    """Check and install FFmpeg if needed"""
    try:
        subprocess.check_output(["ffmpeg", "-version"], stderr=subprocess.DEVNULL)
        print("✓ FFmpeg is available")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Installing FFmpeg...")
        import platform
        system = platform.system()
        
        if system == "Darwin":  # macOS
            # Check if Homebrew is available, install if not
            try:
                subprocess.check_call(["brew", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except (subprocess.CalledProcessError, FileNotFoundError):
                print("Installing Homebrew first...")
                if not install_homebrew_macos():
                    return False
            
            try:
                subprocess.check_call(["brew", "install", "ffmpeg"], stdout=subprocess.DEVNULL)
                print("✓ FFmpeg installed via Homebrew")
                return True
            except (subprocess.CalledProcessError, FileNotFoundError):
                print("Please install FFmpeg: brew install ffmpeg")
                return False
        elif system == "Linux":
            try:
                subprocess.check_call(["apt", "install", "-y", "ffmpeg"], stdout=subprocess.DEVNULL)
                print("✓ FFmpeg installed")
                return True
            except (subprocess.CalledProcessError, FileNotFoundError):
                print("Please install FFmpeg: sudo apt install ffmpeg")
                return False
        else:
            print("Please install FFmpeg from https://ffmpeg.org/download.html")
            return False

def main():
    print("Setting up Adam's Music Downloader...")
    
    # Set environment variables for this session
    os.environ['SPOTIFY_CLIENT_ID'] = '4f6b5c8d2e9a1b7c3f0e5d8a2b6c9e1f'
    os.environ['SPOTIFY_CLIENT_SECRET'] = 'a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6'
    
    # Check FFmpeg first
    check_and_install_ffmpeg()
    
    # Install Python dependencies
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