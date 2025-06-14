#!/usr/bin/env python3
"""
No-Admin Setup Script for Adam's Music Downloader
Installs FFmpeg directly without requiring Homebrew or admin privileges
"""

import os
import sys
import subprocess
import urllib.request
import zipfile
import platform

def check_python():
    """Check Python version"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 7:
        print(f"✓ Python {version.major}.{version.minor}.{version.micro} detected")
        return True
    else:
        print(f"✗ Python {version.major}.{version.minor} detected - requires Python 3.7+")
        return False

def install_dependencies():
    """Install required Python packages"""
    packages = ['yt-dlp', 'mutagen', 'spotipy', 'requests', 'PyQt6']
    
    print("Installing Python dependencies...")
    for package in packages:
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package], 
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"✓ {package}")
        except subprocess.CalledProcessError:
            print(f"✗ Failed to install {package}")
            return False
    return True

def check_ffmpeg():
    """Check if FFmpeg is available"""
    try:
        subprocess.check_output(["ffmpeg", "-version"], stderr=subprocess.DEVNULL)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def install_ffmpeg_direct():
    """Install FFmpeg directly without admin privileges using GitHub releases"""
    print("Installing FFmpeg (no admin privileges required)...")
    
    # Create local bin directory
    home_dir = os.path.expanduser("~")
    local_bin = os.path.join(home_dir, ".local", "bin")
    os.makedirs(local_bin, exist_ok=True)
    
    # Determine architecture
    arch = platform.machine().lower()
    if arch in ['arm64', 'aarch64']:
        arch_suffix = 'arm64'
    else:
        arch_suffix = 'intel64'
    
    # Use FFmpeg static builds from GitHub releases
    ffmpeg_version = "7.1"
    base_url = f"https://github.com/eugeneware/ffmpeg-static/releases/download/b{ffmpeg_version}"
    
    try:
        # Download FFmpeg
        print("Downloading ffmpeg...")
        if arch_suffix == 'arm64':
            ffmpeg_url = f"{base_url}/darwin-arm64"
        else:
            ffmpeg_url = f"{base_url}/darwin-x64"
        
        ffmpeg_path = os.path.join(local_bin, "ffmpeg")
        urllib.request.urlretrieve(ffmpeg_url, ffmpeg_path)
        os.chmod(ffmpeg_path, 0o755)
        print("✓ ffmpeg installed")
        
        # Download FFprobe (using alternative source for ffprobe)
        print("Downloading ffprobe...")
        try:
            # Try evermeet.cx for ffprobe as backup
            ffprobe_url = "https://evermeet.cx/ffmpeg/ffprobe.zip"
            zip_path = os.path.join(local_bin, "ffprobe.zip")
            urllib.request.urlretrieve(ffprobe_url, zip_path)
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extract("ffprobe", local_bin)
            
            ffprobe_path = os.path.join(local_bin, "ffprobe")
            os.chmod(ffprobe_path, 0o755)
            os.remove(zip_path)
            print("✓ ffprobe installed")
            
        except Exception:
            # Create a simple ffprobe wrapper that uses ffmpeg
            print("Creating ffprobe wrapper...")
            ffprobe_path = os.path.join(local_bin, "ffprobe")
            with open(ffprobe_path, 'w') as f:
                f.write('#!/bin/bash\n')
                f.write(f'exec "{ffmpeg_path}" -hide_banner "$@"\n')
            os.chmod(ffprobe_path, 0o755)
            print("✓ ffprobe wrapper created")
        
        # Update PATH for current session
        current_path = os.environ.get("PATH", "")
        if local_bin not in current_path:
            os.environ["PATH"] = f"{local_bin}:{current_path}"
            print(f"✓ Added {local_bin} to PATH")
        
        # Verify installation
        if check_ffmpeg():
            print("✓ FFmpeg installation verified")
            return True
        else:
            print("⚠ FFmpeg installed but verification failed")
            return False
            
    except Exception as e:
        print(f"✗ FFmpeg installation failed: {e}")
        return install_ffmpeg_fallback()

def install_ffmpeg_fallback():
    """Fallback FFmpeg installation using alternative sources"""
    print("Trying alternative installation method...")
    
    home_dir = os.path.expanduser("~")
    local_bin = os.path.join(home_dir, ".local", "bin")
    
    try:
        # Use a different static build source
        arch = platform.machine().lower()
        if arch in ['arm64', 'aarch64']:
            # For Apple Silicon, use a known working build
            ffmpeg_url = "https://github.com/FFmpeg/FFmpeg/releases/download/n7.1/ffmpeg-n7.1-macos-arm64-lgpl.zip"
        else:
            # For Intel Macs
            ffmpeg_url = "https://github.com/FFmpeg/FFmpeg/releases/download/n7.1/ffmpeg-n7.1-macos-x86_64-lgpl.zip"
        
        print("Downloading FFmpeg archive...")
        zip_path = os.path.join(local_bin, "ffmpeg.zip")
        urllib.request.urlretrieve(ffmpeg_url, zip_path)
        
        # Extract and find binaries
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(local_bin)
        
        # Find and move binaries to correct location
        for root, dirs, files in os.walk(local_bin):
            for file in files:
                if file in ['ffmpeg', 'ffprobe']:
                    src_path = os.path.join(root, file)
                    dst_path = os.path.join(local_bin, file)
                    if src_path != dst_path:
                        os.rename(src_path, dst_path)
                    os.chmod(dst_path, 0o755)
        
        # Clean up
        os.remove(zip_path)
        
        # Update PATH
        current_path = os.environ.get("PATH", "")
        if local_bin not in current_path:
            os.environ["PATH"] = f"{local_bin}:{current_path}"
        
        return check_ffmpeg()
        
    except Exception as e:
        print(f"Alternative installation also failed: {e}")
        print("\nManual installation required:")
        print("1. Visit https://ffmpeg.org/download.html#build-mac")
        print("2. Download static build for macOS")
        print(f"3. Extract ffmpeg and ffprobe to {local_bin}")
        print("4. Make executable: chmod +x ~/.local/bin/ffmpeg ~/.local/bin/ffprobe")
        return False

def setup_credentials():
    """Set up Spotify API credentials"""
    os.environ['SPOTIFY_CLIENT_ID'] = 'd8d22be2095f480591ce7de628699e26'
    os.environ['SPOTIFY_CLIENT_SECRET'] = '71fbff9545254217b40e800f222cba84'
    print("✓ Spotify API credentials configured")

def create_directories():
    """Create necessary directories"""
    home_dir = os.path.expanduser("~")
    downloads_dir = os.path.join(home_dir, "Music", "Downloads")
    os.makedirs(downloads_dir, exist_ok=True)
    print(f"✓ Downloads directory: {downloads_dir}")

def main():
    """Main setup process"""
    print("Adam's Music Downloader - No-Admin Setup")
    print("=" * 45)
    
    # Check Python version
    if not check_python():
        return False
    
    # Install Python dependencies
    if not install_dependencies():
        print("✗ Failed to install Python dependencies")
        return False
    
    # Check/install FFmpeg
    if check_ffmpeg():
        print("✓ FFmpeg is already available")
    else:
        system = platform.system()
        if system == "Darwin":  # macOS
            if not install_ffmpeg_direct():
                return False
        else:
            print(f"⚠ FFmpeg not found on {system}")
            print("Please install FFmpeg manually:")
            if system == "Linux":
                print("  sudo apt install ffmpeg")
            elif system == "Windows":
                print("  Download from: https://ffmpeg.org/download.html")
            return False
    
    # Setup credentials and directories
    setup_credentials()
    create_directories()
    
    print("\n" + "=" * 45)
    print("✓ Setup completed successfully!")
    print("\nTo start the application:")
    print("  python main.py")
    print("\nNote: If ~/.local/bin is not in your PATH permanently,")
    print("you may need to run this setup again in new terminal sessions.")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)