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
    """Check system-specific requirements including FFmpeg"""
    system = platform.system()
    
    if system == "Darwin":  # macOS
        print("✓ Running on macOS")
        return check_and_install_ffmpeg_macos()
    elif system == "Linux":
        print("✓ Running on Linux")
        return check_and_install_ffmpeg_linux()
    elif system == "Windows":
        print("✓ Running on Windows")
        return check_and_install_ffmpeg_windows()
    else:
        print(f"⚠️  Untested system: {system}")
        return check_ffmpeg_basic()

def check_ffmpeg_basic():
    """Basic FFmpeg check for unknown systems"""
    try:
        subprocess.check_output(["ffmpeg", "-version"], stderr=subprocess.DEVNULL)
        print("✓ FFmpeg is installed")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("✗ FFmpeg not found - please install manually")
        print("Download from: https://ffmpeg.org/download.html")
        return False

def check_and_install_ffmpeg_macos():
    """Check for FFmpeg and provide installation guidance"""
    try:
        result = subprocess.check_output(["ffmpeg", "-version"], stderr=subprocess.DEVNULL)
        print("✓ FFmpeg is installed")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠ FFmpeg not found")
        print("\nTo install FFmpeg on macOS, choose one option:")
        print("\n1. Homebrew (recommended):")
        print("   brew install ffmpeg")
        print("\n2. Download manually:")
        print("   • Visit: https://www.gyan.dev/ffmpeg/builds/")
        print("   • Download macOS build")
        print("   • Extract ffmpeg and ffprobe to ~/.local/bin/")
        print("   • Run: chmod +x ~/.local/bin/ffmpeg ~/.local/bin/ffprobe")
        print("   • Add to PATH: export PATH=\"$HOME/.local/bin:$PATH\"")
        print("\n3. Using conda:")
        print("   conda install -c conda-forge ffmpeg")
        print("\nAfter installing FFmpeg, run this setup again.")
        return False

def install_ffmpeg_direct_macos():
    """Install FFmpeg directly without Homebrew or admin privileges"""
    import urllib.request
    import zipfile
    import platform
    
    # Get system architecture
    machine = platform.machine().lower()
    arch = 'arm64' if machine in ['arm64', 'aarch64'] else 'x86_64'
    
    # Create local bin directory
    home_dir = os.path.expanduser("~")
    local_bin = os.path.join(home_dir, ".local", "bin")
    os.makedirs(local_bin, exist_ok=True)
    
    print("Downloading FFmpeg binaries...")
    
    # Download FFmpeg and FFprobe from evermeet.cx (reliable static builds)
    binaries = ['ffmpeg', 'ffprobe']
    base_url = "https://evermeet.cx/ffmpeg"
    
    try:
        for binary in binaries:
            download_url = f"{base_url}/{binary}.zip"
            zip_path = os.path.join(local_bin, f"{binary}.zip")
            
            print(f"Downloading {binary}...")
            urllib.request.urlretrieve(download_url, zip_path)
            
            # Extract binary
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extract(binary, local_bin)
            
            # Make executable
            binary_path = os.path.join(local_bin, binary)
            os.chmod(binary_path, 0o755)
            
            # Clean up zip
            os.remove(zip_path)
            print(f"✓ Installed {binary}")
        
        # Update PATH for current session
        current_path = os.environ.get("PATH", "")
        if local_bin not in current_path:
            os.environ["PATH"] = f"{local_bin}:{current_path}"
            print(f"✓ Added {local_bin} to PATH")
        
        # Verify installation
        try:
            subprocess.check_output(["ffmpeg", "-version"], stderr=subprocess.DEVNULL)
            print("✓ FFmpeg installation verified")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("⚠ FFmpeg installed but not found in PATH")
            return False
            
    except Exception as e:
        print(f"✗ Direct installation failed: {e}")
        print("Manual installation: Download from https://evermeet.cx/ffmpeg/")
        return False

def install_homebrew():
    """Install Homebrew on macOS using a more reliable method"""
    try:
        print("Installing Homebrew automatically...")
        
        # Use shell=True for better compatibility with the installation script
        install_command = 'curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh | /bin/bash'
        
        # Set NONINTERACTIVE environment variable to skip prompts
        env = os.environ.copy()
        env['NONINTERACTIVE'] = '1'
        
        result = subprocess.run(
            install_command,
            shell=True,
            env=env,
            capture_output=False,  # Allow real-time output
            text=True
        )
        
        if result.returncode == 0:
            print("✓ Homebrew installation completed")
            
            # Update PATH for current session
            homebrew_paths = [
                "/opt/homebrew/bin",  # Apple Silicon
                "/usr/local/bin"      # Intel
            ]
            
            current_path = os.environ.get("PATH", "")
            for path in homebrew_paths:
                if os.path.exists(path) and path not in current_path:
                    os.environ["PATH"] = f"{path}:{current_path}"
                    print(f"✓ Added {path} to PATH")
            
            # Verify Homebrew installation
            try:
                subprocess.check_call(["brew", "--version"], stdout=subprocess.DEVNULL)
                return True
            except (subprocess.CalledProcessError, FileNotFoundError):
                print("⚠ Homebrew installed but not in PATH, trying manual PATH update...")
                return False
        else:
            print(f"✗ Homebrew installation failed with code {result.returncode}")
            return False
            
    except Exception as e:
        print(f"✗ Error during Homebrew installation: {e}")
        return False

def check_and_install_ffmpeg_linux():
    """Check and install FFmpeg on Linux"""
    try:
        subprocess.check_output(["ffmpeg", "-version"], stderr=subprocess.DEVNULL)
        print("✓ FFmpeg is installed")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠ FFmpeg not found - attempting installation...")
        
        # Try different package managers
        package_managers = [
            (["apt", "update"], ["apt", "install", "-y", "ffmpeg"]),
            (["yum", "install", "-y", "ffmpeg"], None),
            (["dnf", "install", "-y", "ffmpeg"], None),
            (["pacman", "-S", "--noconfirm", "ffmpeg"], None)
        ]
        
        for update_cmd, install_cmd in package_managers:
            try:
                if update_cmd and install_cmd:
                    subprocess.check_call(update_cmd, stdout=subprocess.DEVNULL)
                    subprocess.check_call(install_cmd)
                else:
                    subprocess.check_call(update_cmd)
                print("✓ FFmpeg installed successfully")
                return True
            except (subprocess.CalledProcessError, FileNotFoundError):
                continue
        
        print("✗ Could not install FFmpeg automatically")
        print("Please install manually using your system's package manager")
        return False

def check_and_install_ffmpeg_windows():
    """Check and install FFmpeg on Windows"""
    try:
        subprocess.check_output(["ffmpeg", "-version"], stderr=subprocess.DEVNULL)
        print("✓ FFmpeg is installed")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("✗ FFmpeg not found")
        print("Please install FFmpeg manually:")
        print("1. Download from: https://www.gyan.dev/ffmpeg/builds/")
        print("2. Extract to C:\\ffmpeg\\")
        print("3. Add C:\\ffmpeg\\bin to your system PATH")
        print("4. Restart your terminal/command prompt")
        return False

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