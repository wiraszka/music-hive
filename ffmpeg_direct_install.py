#!/usr/bin/env python3
"""
Direct FFmpeg installer for macOS without requiring Homebrew or admin privileges
Downloads pre-compiled FFmpeg binaries directly
"""

import os
import sys
import subprocess
import urllib.request
import zipfile
import tarfile
import shutil
import platform

def get_system_info():
    """Get system architecture information"""
    machine = platform.machine().lower()
    if machine in ['arm64', 'aarch64']:
        return 'arm64'
    elif machine in ['x86_64', 'amd64']:
        return 'x86_64'
    else:
        return machine

def download_file(url, filename):
    """Download a file with progress indication"""
    print(f"Downloading {filename}...")
    try:
        urllib.request.urlretrieve(url, filename)
        return True
    except Exception as e:
        print(f"Download failed: {e}")
        return False

def extract_archive(archive_path, extract_to):
    """Extract archive file"""
    print(f"Extracting {archive_path}...")
    try:
        if archive_path.endswith('.zip'):
            with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                zip_ref.extractall(extract_to)
        elif archive_path.endswith(('.tar.gz', '.tgz')):
            with tarfile.open(archive_path, 'r:gz') as tar_ref:
                tar_ref.extractall(extract_to)
        elif archive_path.endswith('.tar.xz'):
            with tarfile.open(archive_path, 'r:xz') as tar_ref:
                tar_ref.extractall(extract_to)
        return True
    except Exception as e:
        print(f"Extraction failed: {e}")
        return False

def install_ffmpeg_macos():
    """Install FFmpeg directly on macOS without Homebrew"""
    arch = get_system_info()
    
    # Create local bin directory
    home_dir = os.path.expanduser("~")
    local_bin = os.path.join(home_dir, ".local", "bin")
    os.makedirs(local_bin, exist_ok=True)
    
    # FFmpeg download URLs for macOS
    if arch == 'arm64':
        ffmpeg_url = "https://www.osxexperts.net/ffmpeg6arm.zip"
        filename = "ffmpeg6arm.zip"
    else:
        ffmpeg_url = "https://www.osxexperts.net/ffmpeg6intel.zip"
        filename = "ffmpeg6intel.zip"
    
    temp_dir = os.path.join(home_dir, ".ffmpeg_temp")
    os.makedirs(temp_dir, exist_ok=True)
    
    try:
        # Download FFmpeg
        archive_path = os.path.join(temp_dir, filename)
        if not download_file(ffmpeg_url, archive_path):
            return False
        
        # Extract archive
        if not extract_archive(archive_path, temp_dir):
            return False
        
        # Find ffmpeg and ffprobe binaries
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                if file in ['ffmpeg', 'ffprobe']:
                    src_path = os.path.join(root, file)
                    dst_path = os.path.join(local_bin, file)
                    shutil.copy2(src_path, dst_path)
                    os.chmod(dst_path, 0o755)  # Make executable
                    print(f"✓ Installed {file} to {dst_path}")
        
        # Update PATH in current session
        current_path = os.environ.get("PATH", "")
        if local_bin not in current_path:
            os.environ["PATH"] = f"{local_bin}:{current_path}"
            print(f"✓ Added {local_bin} to PATH")
        
        # Clean up temp directory
        shutil.rmtree(temp_dir, ignore_errors=True)
        
        return True
        
    except Exception as e:
        print(f"Installation failed: {e}")
        # Clean up on failure
        shutil.rmtree(temp_dir, ignore_errors=True)
        return False

def install_ffmpeg_alternative():
    """Alternative FFmpeg installation using static builds"""
    home_dir = os.path.expanduser("~")
    local_bin = os.path.join(home_dir, ".local", "bin")
    os.makedirs(local_bin, exist_ok=True)
    
    arch = get_system_info()
    
    # Use evermeet.cx static builds (reliable source)
    base_url = "https://evermeet.cx/ffmpeg"
    
    binaries = ['ffmpeg', 'ffprobe']
    
    for binary in binaries:
        if arch == 'arm64':
            download_url = f"{base_url}/{binary}.zip"
        else:
            download_url = f"{base_url}/{binary}.zip"
        
        try:
            print(f"Downloading {binary}...")
            zip_path = os.path.join(local_bin, f"{binary}.zip")
            
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
            
        except Exception as e:
            print(f"Failed to install {binary}: {e}")
            return False
    
    # Update PATH
    current_path = os.environ.get("PATH", "")
    if local_bin not in current_path:
        os.environ["PATH"] = f"{local_bin}:{current_path}"
        print(f"✓ Added {local_bin} to PATH")
    
    return True

def check_ffmpeg():
    """Check if FFmpeg is installed and working"""
    try:
        subprocess.check_output(["ffmpeg", "-version"], stderr=subprocess.DEVNULL)
        subprocess.check_output(["ffprobe", "-version"], stderr=subprocess.DEVNULL)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def main():
    """Main installation process"""
    print("Direct FFmpeg Installation for macOS")
    print("=" * 40)
    
    if check_ffmpeg():
        print("✓ FFmpeg is already installed and working")
        return True
    
    print("Installing FFmpeg directly (no admin privileges required)...")
    
    # Try primary installation method
    if install_ffmpeg_alternative():
        if check_ffmpeg():
            print("✓ FFmpeg installation successful")
            print(f"✓ Binaries installed to: {os.path.expanduser('~/.local/bin')}")
            return True
        else:
            print("⚠ Installation completed but FFmpeg not detected in PATH")
    
    # If primary method fails, try alternative
    print("Trying alternative installation method...")
    if install_ffmpeg_macos():
        if check_ffmpeg():
            print("✓ FFmpeg installation successful")
            return True
    
    print("✗ Automatic installation failed")
    print("\nManual installation options:")
    print("1. Download from: https://evermeet.cx/ffmpeg/")
    print("2. Extract and place ffmpeg/ffprobe in ~/.local/bin/")
    print("3. Add ~/.local/bin to your PATH")
    
    return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)