#!/usr/bin/env python3
"""
Working Setup Script for Adam's Music Downloader
Focuses on getting the application running with clear FFmpeg installation guidance
"""

import os
import sys
import subprocess
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

def install_python_dependencies():
    """Install required Python packages"""
    packages = ['yt-dlp', 'mutagen', 'spotipy', 'requests', 'PyQt6']
    
    print("Installing Python dependencies...")
    failed_packages = []
    
    for package in packages:
        try:
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install', package
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"✓ {package}")
        except subprocess.CalledProcessError:
            print(f"✗ Failed to install {package}")
            failed_packages.append(package)
    
    if failed_packages:
        print(f"Failed to install: {', '.join(failed_packages)}")
        print("Try running: pip3 install " + " ".join(failed_packages))
        return False
    
    return True

def check_ffmpeg():
    """Check if FFmpeg is available"""
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(f"✓ FFmpeg found: {version_line}")
            return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    
    return False

def provide_ffmpeg_instructions():
    """Provide clear FFmpeg installation instructions"""
    system = platform.system()
    
    print("⚠ FFmpeg not found - required for audio conversion")
    print("\nFFmpeg Installation Options:")
    
    if system == "Darwin":  # macOS
        print("\n🍺 Option 1: Homebrew (Recommended)")
        print("   /bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"")
        print("   brew install ffmpeg")
        
        print("\n📦 Option 2: MacPorts")
        print("   Download from: https://www.macports.org/install.php")
        print("   sudo port install ffmpeg")
        
        print("\n📁 Option 3: Manual Download")
        print("   1. Visit: https://www.gyan.dev/ffmpeg/builds/")
        print("   2. Download 'macOS build'")
        print("   3. Extract and copy ffmpeg, ffprobe to ~/.local/bin/")
        print("   4. chmod +x ~/.local/bin/ffmpeg ~/.local/bin/ffprobe")
        print("   5. Add to PATH: export PATH=\"$HOME/.local/bin:$PATH\"")
        
        print("\n🐍 Option 4: Conda")
        print("   conda install -c conda-forge ffmpeg")
        
    elif system == "Linux":
        print("\n📦 Ubuntu/Debian:")
        print("   sudo apt update && sudo apt install ffmpeg")
        
        print("\n📦 CentOS/RHEL:")
        print("   sudo yum install ffmpeg")
        
        print("\n📦 Fedora:")
        print("   sudo dnf install ffmpeg")
        
        print("\n🐍 Conda:")
        print("   conda install -c conda-forge ffmpeg")
        
    elif system == "Windows":
        print("\n📁 Windows:")
        print("   1. Visit: https://www.gyan.dev/ffmpeg/builds/")
        print("   2. Download Windows build")
        print("   3. Extract to C:\\ffmpeg\\")
        print("   4. Add C:\\ffmpeg\\bin to PATH")
        
        print("\n🐍 Conda:")
        print("   conda install -c conda-forge ffmpeg")

def setup_credentials():
    """Set up Spotify API credentials"""
    os.environ['SPOTIFY_CLIENT_ID'] = 'd8d22be2095f480591ce7de628699e26'
    os.environ['SPOTIFY_CLIENT_SECRET'] = '71fbff9545254217b40e800f222cba84'
    print("✓ Spotify API credentials configured")

def create_directories():
    """Create necessary directories"""
    home_dir = os.path.expanduser("~")
    dirs_to_create = [
        os.path.join(home_dir, "Music", "Downloads"),
        os.path.join(home_dir, ".local", "bin")
    ]
    
    for directory in dirs_to_create:
        os.makedirs(directory, exist_ok=True)
    
    print(f"✓ Created directories")

def test_imports():
    """Test if all required modules can be imported"""
    modules = [
        ('yt_dlp', 'yt-dlp'),
        ('mutagen', 'mutagen'),
        ('spotipy', 'spotipy'),
        ('requests', 'requests'),
        ('PyQt6.QtWidgets', 'PyQt6')
    ]
    
    print("Testing module imports...")
    failed_imports = []
    
    for module, package in modules:
        try:
            __import__(module)
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package}")
            failed_imports.append(package)
    
    return len(failed_imports) == 0

def main():
    """Main setup process"""
    print("Adam's Music Downloader - Setup")
    print("=" * 35)
    
    # Check Python version
    if not check_python():
        print("\nPlease install Python 3.7 or higher")
        return False
    
    # Install Python dependencies
    if not install_python_dependencies():
        print("\nFailed to install some Python dependencies")
        return False
    
    # Test imports
    if not test_imports():
        print("\nSome modules failed to import - please check installation")
        return False
    
    # Setup credentials and directories
    setup_credentials()
    create_directories()
    
    # Check FFmpeg
    ffmpeg_available = check_ffmpeg()
    
    if not ffmpeg_available:
        provide_ffmpeg_instructions()
        print("\n" + "=" * 50)
        print("⚠ SETUP INCOMPLETE: FFmpeg required")
        print("Install FFmpeg using one of the methods above,")
        print("then run this setup again to verify.")
        print("=" * 50)
        return False
    
    print("\n" + "=" * 35)
    print("✓ Setup completed successfully!")
    print("\nTo start the application:")
    print("  python3 main.py")
    print("=" * 35)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)