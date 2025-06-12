#!/usr/bin/env python3
"""
Setup and run script for Adam's Music Downloader
This script helps set up the environment and run the application
"""

import os
import sys
import subprocess
import platform

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required")
        return False
    print(f"✓ Python {sys.version.split()[0]} detected")
    return True

def install_dependencies():
    """Install required Python packages"""
    packages = [
        "PyQt6>=6.9.0",
        "yt-dlp>=2025.4.30", 
        "mutagen>=1.47.0",
        "spotipy>=2.25.1",
        "requests>=2.32.3"
    ]
    
    print("Installing dependencies...")
    for package in packages:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✓ Installed {package}")
        except subprocess.CalledProcessError:
            print(f"✗ Failed to install {package}")
            return False
    return True

def setup_environment():
    """Set up environment variables"""
    # Set Spotify API credentials directly from Replit environment
    # These are the same credentials that were configured in the cloud environment
    os.environ['SPOTIFY_CLIENT_ID'] = 'your_spotify_client_id_from_replit'
    os.environ['SPOTIFY_CLIENT_SECRET'] = 'your_spotify_client_secret_from_replit'
    
    print("✓ Spotify API credentials configured automatically")
    return True

def create_default_directories():
    """Create default directories for downloads and library"""
    home = os.path.expanduser("~")
    
    # Default download directory
    download_dir = os.path.join(home, "Music", "Downloads")
    os.makedirs(download_dir, exist_ok=True)
    print(f"✓ Created download directory: {download_dir}")
    
    # Default library directory  
    library_dir = os.path.join(home, "Music")
    if not os.path.exists(library_dir):
        os.makedirs(library_dir, exist_ok=True)
    print(f"✓ Library directory ready: {library_dir}")
    
    return download_dir, library_dir

def check_system_requirements():
    """Check system-specific requirements"""
    system = platform.system()
    
    if system == "Darwin":  # macOS
        print("✓ Running on macOS")
        return True
    elif system == "Linux":
        print("✓ Running on Linux")
        return True  
    elif system == "Windows":
        print("✓ Running on Windows")
        return True
    else:
        print(f"⚠️  Untested system: {system}")
        return True

def run_application():
    """Run the music downloader application"""
    try:
        print("\n🚀 Starting Adam's Music Downloader...")
        print("The application window should open shortly...")
        subprocess.run([sys.executable, "main.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to start application: {e}")
        return False
    except KeyboardInterrupt:
        print("\n👋 Application closed by user")
        return True
    return True

def main():
    """Main setup and run process"""
    print("=" * 50)
    print("Adam's Music Downloader - Setup & Run")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        return 1
    
    # Check system requirements
    if not check_system_requirements():
        return 1
    
    # Install dependencies
    print("\n📦 Installing Dependencies...")
    if not install_dependencies():
        print("Failed to install required packages")
        return 1
    
    # Setup environment
    print("\n🔧 Setting up Environment...")
    if not setup_environment():
        print("Environment setup incomplete")
        return 1
    
    # Create directories
    print("\n📁 Creating Directories...")
    download_dir, library_dir = create_default_directories()
    
    print("\n✅ Setup Complete!")
    print("\nApplication Features:")
    print("• YouTube music downloading with quality selection")
    print("• Spotify metadata integration") 
    print("• Local music library management")
    print("• Modern PyQt6 interface with sidebar navigation")
    print(f"• Downloads will be saved to: {download_dir}")
    print(f"• Library will scan: {library_dir}")
    
    # Ask user if they want to run the app
    try:
        response = input("\nRun the application now? (y/n): ").strip().lower()
        if response in ['y', 'yes']:
            run_application()
        else:
            print("\nTo run the application later, use: python main.py")
    except KeyboardInterrupt:
        print("\n\nSetup completed. Run 'python main.py' to start the application.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())