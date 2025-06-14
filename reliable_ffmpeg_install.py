#!/usr/bin/env python3
"""
Reliable FFmpeg installation for macOS without admin privileges
Uses official static builds from gyan.dev (trusted FFmpeg distributor)
"""

import os
import sys
import subprocess
import urllib.request
import tarfile
import zipfile
import platform
import json

def check_ffmpeg():
    """Check if FFmpeg is available"""
    try:
        result = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True)
        if result.returncode == 0:
            return True
    except FileNotFoundError:
        pass
    return False

def get_latest_ffmpeg_release():
    """Get latest FFmpeg release info from GitHub API"""
    try:
        url = "https://api.github.com/repos/BtbN/FFmpeg-Builds/releases/latest"
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())
        
        # Find macOS build
        arch = platform.machine().lower()
        if arch in ['arm64', 'aarch64']:
            target = "macos-arm64"
        else:
            target = "macos-64"
        
        for asset in data['assets']:
            if target in asset['name'] and 'lgpl' in asset['name']:
                return asset['browser_download_url']
        
        return None
    except Exception:
        return None

def install_ffmpeg_from_gyan():
    """Install FFmpeg using gyan.dev builds (very reliable)"""
    home_dir = os.path.expanduser("~")
    local_bin = os.path.join(home_dir, ".local", "bin")
    os.makedirs(local_bin, exist_ok=True)
    
    arch = platform.machine().lower()
    
    try:
        # Use gyan.dev static builds - very reliable source
        print("Downloading FFmpeg from gyan.dev...")
        
        if arch in ['arm64', 'aarch64']:
            # For Apple Silicon
            download_url = "https://www.gyan.dev/ffmpeg/builds/packages/ffmpeg-6.1-macos-arm64-lgpl.zip"
        else:
            # For Intel
            download_url = "https://www.gyan.dev/ffmpeg/builds/packages/ffmpeg-6.1-macos-intel-lgpl.zip"
        
        zip_path = os.path.join(local_bin, "ffmpeg-download.zip")
        
        # Download with error handling
        try:
            urllib.request.urlretrieve(download_url, zip_path)
        except urllib.error.HTTPError as e:
            print(f"Download failed with HTTP {e.code}")
            return False
        
        print("Extracting FFmpeg...")
        
        # Extract archive
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(local_bin)
        
        # Find and move binaries
        extracted_dir = None
        for item in os.listdir(local_bin):
            item_path = os.path.join(local_bin, item)
            if os.path.isdir(item_path) and "ffmpeg" in item:
                extracted_dir = item_path
                break
        
        if extracted_dir:
            bin_dir = os.path.join(extracted_dir, "bin")
            if os.path.exists(bin_dir):
                for binary in ["ffmpeg", "ffprobe"]:
                    src = os.path.join(bin_dir, binary)
                    dst = os.path.join(local_bin, binary)
                    if os.path.exists(src):
                        if os.path.exists(dst):
                            os.remove(dst)
                        os.rename(src, dst)
                        os.chmod(dst, 0o755)
                        print(f"✓ {binary} installed")
            
            # Clean up extracted directory
            import shutil
            shutil.rmtree(extracted_dir, ignore_errors=True)
        
        # Clean up zip file
        os.remove(zip_path)
        
        # Update PATH
        current_path = os.environ.get("PATH", "")
        if local_bin not in current_path:
            os.environ["PATH"] = f"{local_bin}:{current_path}"
            print(f"✓ Added {local_bin} to PATH")
        
        return check_ffmpeg()
        
    except Exception as e:
        print(f"Installation failed: {e}")
        return False

def install_ffmpeg_github():
    """Install FFmpeg from GitHub releases"""
    download_url = get_latest_ffmpeg_release()
    if not download_url:
        return False
    
    home_dir = os.path.expanduser("~")
    local_bin = os.path.join(home_dir, ".local", "bin")
    os.makedirs(local_bin, exist_ok=True)
    
    try:
        print("Downloading FFmpeg from GitHub...")
        archive_path = os.path.join(local_bin, "ffmpeg-github.tar.xz")
        urllib.request.urlretrieve(download_url, archive_path)
        
        print("Extracting FFmpeg...")
        with tarfile.open(archive_path, 'r:xz') as tar:
            tar.extractall(local_bin)
        
        # Find binaries and move to local_bin
        for root, dirs, files in os.walk(local_bin):
            for file in files:
                if file in ['ffmpeg', 'ffprobe'] and 'bin' in root:
                    src_path = os.path.join(root, file)
                    dst_path = os.path.join(local_bin, file)
                    if src_path != dst_path:
                        if os.path.exists(dst_path):
                            os.remove(dst_path)
                        os.rename(src_path, dst_path)
                        os.chmod(dst_path, 0o755)
        
        # Clean up
        os.remove(archive_path)
        
        # Update PATH
        current_path = os.environ.get("PATH", "")
        if local_bin not in current_path:
            os.environ["PATH"] = f"{local_bin}:{current_path}"
        
        return check_ffmpeg()
        
    except Exception as e:
        print(f"GitHub installation failed: {e}")
        return False

def main():
    """Main installation process"""
    print("Reliable FFmpeg Installation")
    print("=" * 30)
    
    if check_ffmpeg():
        print("✓ FFmpeg is already available")
        return True
    
    print("Installing FFmpeg without admin privileges...")
    
    # Try gyan.dev first (most reliable)
    if install_ffmpeg_from_gyan():
        print("✓ FFmpeg installed successfully from gyan.dev")
        return True
    
    # Try GitHub releases as fallback
    if install_ffmpeg_github():
        print("✓ FFmpeg installed successfully from GitHub")
        return True
    
    # Provide manual instructions
    print("\nAutomatic installation failed. Manual installation options:")
    print("\n1. Homebrew (requires admin):")
    print("   brew install ffmpeg")
    print("\n2. MacPorts (requires admin):")
    print("   sudo port install ffmpeg")
    print("\n3. Manual download:")
    print("   • Visit: https://www.gyan.dev/ffmpeg/builds/")
    print("   • Download macOS build")
    print("   • Extract to ~/.local/bin/")
    print("   • Add to PATH: export PATH=\"$HOME/.local/bin:$PATH\"")
    
    return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)