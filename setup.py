#!/usr/bin/env python3
"""
Complete setup script for Music Downloader
Installs all dependencies and configures the environment automatically
Works on Windows, macOS, and Linux
"""

import os
import sys
import subprocess
import platform
import urllib.request
import zipfile
import tarfile
import shutil
from pathlib import Path

def run_command(command, check=True):
    """Run a shell command and return the result"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=check)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return False, e.stdout, e.stderr

def check_python_version():
    """Check if Python version is 3.8 or higher"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python 3.8+ required. Current version: {version.major}.{version.minor}")
        sys.exit(1)
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")

def install_pip_packages():
    """Install required Python packages"""
    packages = [
        'yt-dlp>=2024.1.0',
        'mutagen>=1.45.0',
        'spotipy>=2.22.0',
        'requests>=2.28.0',
        'PyQt6>=6.4.0',
        'fuzzywuzzy>=0.18.0',
        'python-Levenshtein>=0.20.0'
    ]
    
    print("📦 Installing Python packages...")
    for package in packages:
        print(f"  Installing {package}...")
        success, stdout, stderr = run_command(f'pip install "{package}"')
        if not success:
            print(f"  ⚠️  Failed to install {package}: {stderr}")
        else:
            print(f"  ✅ {package}")

def check_ffmpeg():
    """Check if FFmpeg is available"""
    success, stdout, stderr = run_command('ffmpeg -version', check=False)
    if success:
        print("✅ FFmpeg is available")
        return True
    else:
        print("❌ FFmpeg not found")
        return False

def install_ffmpeg_windows():
    """Install FFmpeg on Windows"""
    print("📦 Installing FFmpeg for Windows...")
    
    # Create local bin directory
    bin_dir = Path.cwd() / 'bin'
    bin_dir.mkdir(exist_ok=True)
    
    # Download FFmpeg
    ffmpeg_url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
    zip_path = bin_dir / "ffmpeg.zip"
    
    print("  Downloading FFmpeg...")
    urllib.request.urlretrieve(ffmpeg_url, zip_path)
    
    # Extract FFmpeg
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(bin_dir)
    
    # Find and move executables
    for item in bin_dir.iterdir():
        if item.is_dir() and 'ffmpeg' in item.name:
            ffmpeg_bin = item / 'bin'
            if ffmpeg_bin.exists():
                for exe in ffmpeg_bin.glob('*.exe'):
                    shutil.move(str(exe), str(bin_dir / exe.name))
                shutil.rmtree(item)
                break
    
    # Clean up
    zip_path.unlink()
    
    # Add to PATH for current session
    os.environ['PATH'] = str(bin_dir) + os.pathsep + os.environ.get('PATH', '')
    print("✅ FFmpeg installed locally")

def install_ffmpeg_macos():
    """Install FFmpeg on macOS"""
    print("📦 Installing FFmpeg for macOS...")
    
    # Try Homebrew first
    success, stdout, stderr = run_command('brew --version', check=False)
    if success:
        print("  Using Homebrew...")
        success, stdout, stderr = run_command('brew install ffmpeg')
        if success:
            print("✅ FFmpeg installed via Homebrew")
            return
    
    # Fallback to static build
    print("  Using static build...")
    bin_dir = Path.cwd() / 'bin'
    bin_dir.mkdir(exist_ok=True)
    
    ffmpeg_url = "https://evermeet.cx/ffmpeg/ffmpeg-5.1.2.zip"
    zip_path = bin_dir / "ffmpeg.zip"
    
    urllib.request.urlretrieve(ffmpeg_url, zip_path)
    
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(bin_dir)
    
    zip_path.unlink()
    
    # Make executable
    ffmpeg_path = bin_dir / 'ffmpeg'
    if ffmpeg_path.exists():
        os.chmod(ffmpeg_path, 0o755)
        os.environ['PATH'] = str(bin_dir) + os.pathsep + os.environ.get('PATH', '')
        print("✅ FFmpeg installed locally")

def install_ffmpeg_linux():
    """Install FFmpeg on Linux"""
    print("📦 Installing FFmpeg for Linux...")
    
    # Try package managers
    distro_commands = [
        'apt-get update && apt-get install -y ffmpeg',  # Ubuntu/Debian
        'yum install -y ffmpeg',                        # CentOS/RHEL
        'dnf install -y ffmpeg',                        # Fedora
        'pacman -S --noconfirm ffmpeg',                 # Arch
        'zypper install -y ffmpeg'                      # openSUSE
    ]
    
    for cmd in distro_commands:
        success, stdout, stderr = run_command(f'sudo {cmd}', check=False)
        if success:
            print(f"✅ FFmpeg installed via system package manager")
            return
    
    # Fallback to static build
    print("  Using static build...")
    bin_dir = Path.cwd() / 'bin'
    bin_dir.mkdir(exist_ok=True)
    
    ffmpeg_url = "https://johnvansickle.com/ffmpeg/builds/ffmpeg-git-amd64-static.tar.xz"
    tar_path = bin_dir / "ffmpeg.tar.xz"
    
    urllib.request.urlretrieve(ffmpeg_url, tar_path)
    
    with tarfile.open(tar_path, 'r:xz') as tar_ref:
        tar_ref.extractall(bin_dir)
    
    # Find and move executables
    for item in bin_dir.iterdir():
        if item.is_dir() and 'ffmpeg' in item.name:
            for exe in ['ffmpeg', 'ffprobe']:
                exe_path = item / exe
                if exe_path.exists():
                    shutil.move(str(exe_path), str(bin_dir / exe))
                    os.chmod(bin_dir / exe, 0o755)
            shutil.rmtree(item)
            break
    
    tar_path.unlink()
    os.environ['PATH'] = str(bin_dir) + os.pathsep + os.environ.get('PATH', '')
    print("✅ FFmpeg installed locally")

def install_ffmpeg():
    """Install FFmpeg based on the operating system"""
    if check_ffmpeg():
        return
    
    system = platform.system().lower()
    try:
        if system == 'windows':
            install_ffmpeg_windows()
        elif system == 'darwin':  # macOS
            install_ffmpeg_macos()
        elif system == 'linux':
            install_ffmpeg_linux()
        else:
            print(f"⚠️  Unsupported OS: {system}")
            print("   Please install FFmpeg manually")
    except Exception as e:
        print(f"⚠️  FFmpeg installation failed: {e}")
        print("   The app will try to work without FFmpeg")

def create_credentials_file():
    """Create a credentials file template"""
    credentials_path = Path('credentials.env')
    if not credentials_path.exists():
        print("📝 Creating credentials template...")
        with open(credentials_path, 'w') as f:
            f.write("""# Spotify API Credentials
# Get these from: https://developer.spotify.com/dashboard
SPOTIFY_CLIENT_ID=your_client_id_here
SPOTIFY_CLIENT_SECRET=your_client_secret_here

# Optional: Custom download directory
# DOWNLOAD_DIR=/path/to/your/music/folder
""")
        print("✅ Created credentials.env template")
        print("   Please edit credentials.env with your Spotify API keys")
    else:
        print("✅ credentials.env already exists")

def test_installation():
    """Test if the installation was successful"""
    print("🧪 Testing installation...")
    
    # Test Python imports
    test_imports = [
        'yt_dlp',
        'mutagen', 
        'spotipy',
        'requests',
        'PyQt6.QtWidgets',
        'fuzzywuzzy'
    ]
    
    failed_imports = []
    for module in test_imports:
        try:
            __import__(module)
            print(f"  ✅ {module}")
        except ImportError:
            print(f"  ❌ {module}")
            failed_imports.append(module)
    
    # Test FFmpeg
    if check_ffmpeg():
        print("  ✅ ffmpeg")
    else:
        print("  ⚠️  ffmpeg (will try imageio-ffmpeg fallback)")
    
    if failed_imports:
        print(f"❌ Installation incomplete. Failed: {', '.join(failed_imports)}")
        return False
    else:
        print("✅ Installation successful!")
        return True

def main():
    """Main setup function"""
    print("🎵 Music Downloader Setup")
    print("=" * 40)
    
    # Check Python version
    check_python_version()
    
    # Install Python packages
    install_pip_packages()
    
    # Install FFmpeg
    install_ffmpeg()
    
    # Create credentials file
    create_credentials_file()
    
    # Test installation
    success = test_installation()
    
    print("\n" + "=" * 40)
    if success:
        print("🎉 Setup Complete!")
        print("\nNext steps:")
        print("1. Edit credentials.env with your Spotify API keys")
        print("2. Run: python main.py")
        print("\nGet Spotify API keys from:")
        print("https://developer.spotify.com/dashboard")
    else:
        print("⚠️  Setup had issues. Please check the errors above.")
        print("You may need to manually install failed packages.")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)