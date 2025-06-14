#!/usr/bin/env python3
"""
Automatic setup script for Adam's Music Downloader
Includes embedded credentials and installs everything automatically
"""

import os
import sys
import subprocess
import importlib

# Required dependencies for the application
REQUIRED_PACKAGES = [
    'yt-dlp>=2025.4.30',
    'mutagen>=1.47.0', 
    'spotipy>=2.25.1',
    'requests>=2.32.3',
    'PyQt6>=6.9.0',
    'fuzzywuzzy>=0.18.0',
    'python-levenshtein>=0.27.1',
    'imageio-ffmpeg>=0.6.0'
]

def check_ffmpeg():
    """Check if FFmpeg is installed"""
    try:
        subprocess.check_output(["ffmpeg", "-version"], stderr=subprocess.DEVNULL)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def install_homebrew_if_needed():
    """Install Homebrew if not present on macOS"""
    try:
        subprocess.check_call(["brew", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Installing Homebrew...")
        try:
            install_cmd = [
                "/bin/bash", "-c", 
                "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
            ]
            subprocess.check_call(install_cmd, stdout=subprocess.DEVNULL)
            
            # Add to PATH
            import os
            homebrew_paths = ["/opt/homebrew/bin", "/usr/local/bin"]
            current_path = os.environ.get("PATH", "")
            for path in homebrew_paths:
                if path not in current_path and os.path.exists(path):
                    os.environ["PATH"] = f"{path}:{current_path}"
            
            return True
        except subprocess.CalledProcessError:
            return False

def install_ffmpeg_direct_macos():
    """Install FFmpeg directly without admin privileges"""
    import urllib.request
    import zipfile
    
    home_dir = os.path.expanduser("~")
    local_bin = os.path.join(home_dir, ".local", "bin")
    os.makedirs(local_bin, exist_ok=True)
    
    binaries = ['ffmpeg', 'ffprobe']
    base_url = "https://evermeet.cx/ffmpeg"
    
    try:
        for binary in binaries:
            download_url = f"{base_url}/{binary}.zip"
            zip_path = os.path.join(local_bin, f"{binary}.zip")
            
            urllib.request.urlretrieve(download_url, zip_path)
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extract(binary, local_bin)
            
            binary_path = os.path.join(local_bin, binary)
            os.chmod(binary_path, 0o755)
            os.remove(zip_path)
        
        # Update PATH
        current_path = os.environ.get("PATH", "")
        if local_bin not in current_path:
            os.environ["PATH"] = f"{local_bin}:{current_path}"
        
        return True
        
    except Exception:
        return False

def install_ffmpeg():
    """Install FFmpeg based on platform"""
    import platform
    system = platform.system()
    
    if system == "Darwin":  # macOS
        return install_ffmpeg_direct_macos()
    elif system == "Linux":
        try:
            subprocess.check_call(["apt", "install", "-y", "ffmpeg"], stdout=subprocess.DEVNULL)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("Please install FFmpeg: sudo apt install ffmpeg")
            return False
    else:
        print("Please install FFmpeg manually from https://ffmpeg.org/download.html")
        return False

def main():
    print("Setting up Adam's Music Downloader...")
    
    # Set Spotify API credentials directly in environment
    os.environ['SPOTIFY_CLIENT_ID'] = 'd8d22be2095f480591ce7de628699e26'
    os.environ['SPOTIFY_CLIENT_SECRET'] = '71fbff9545254217b40e800f222cba84'
    
    # Check FFmpeg first
    if not check_ffmpeg():
        print("Installing FFmpeg...")
        if not install_ffmpeg():
            print("⚠ FFmpeg installation failed - downloads may not work properly")
    else:
        print("✓ FFmpeg is installed")
    
    # Install Python dependencies
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