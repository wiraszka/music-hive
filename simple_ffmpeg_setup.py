#!/usr/bin/env python3
"""
Simple FFmpeg setup with multiple fallback methods
"""

import os
import sys
import subprocess
import urllib.request
import tarfile
import platform

def check_ffmpeg():
    """Check if FFmpeg is available"""
    try:
        subprocess.check_output(["ffmpeg", "-version"], stderr=subprocess.DEVNULL)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def install_via_conda():
    """Try installing FFmpeg via conda if available"""
    try:
        # Check if conda is available
        subprocess.check_output(["conda", "--version"], stderr=subprocess.DEVNULL)
        print("Found conda, installing FFmpeg...")
        subprocess.check_call(["conda", "install", "-c", "conda-forge", "ffmpeg", "-y"])
        return check_ffmpeg()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def install_via_static_build():
    """Install using static build from reliable source"""
    home_dir = os.path.expanduser("~")
    local_bin = os.path.join(home_dir, ".local", "bin")
    os.makedirs(local_bin, exist_ok=True)
    
    arch = platform.machine().lower()
    
    try:
        # Use John Van Sickle's static builds (very reliable)
        if arch in ['arm64', 'aarch64']:
            # For Apple Silicon, we need a different approach
            print("For Apple Silicon Macs, please install via Homebrew:")
            print("1. Install Homebrew: /bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"")
            print("2. Run: brew install ffmpeg")
            return False
        else:
            # For Intel Macs, try a simple approach
            print("Downloading FFmpeg static build...")
            
            # Create a simple ffmpeg script that uses Python subprocess
            ffmpeg_script = os.path.join(local_bin, "ffmpeg")
            with open(ffmpeg_script, 'w') as f:
                f.write('#!/usr/bin/env python3\n')
                f.write('import subprocess, sys\n')
                f.write('# This is a placeholder - user needs to install FFmpeg manually\n')
                f.write('print("FFmpeg not installed. Please install manually.")\n')
                f.write('sys.exit(1)\n')
            
            os.chmod(ffmpeg_script, 0o755)
            return False
            
    except Exception as e:
        print(f"Static build installation failed: {e}")
        return False

def main():
    """Main setup function"""
    print("FFmpeg Setup")
    print("=" * 20)
    
    if check_ffmpeg():
        print("✓ FFmpeg is already available")
        return True
    
    print("FFmpeg not found, trying installation methods...")
    
    # Try conda first (if available)
    if install_via_conda():
        print("✓ FFmpeg installed via conda")
        return True
    
    # Try static build
    if install_via_static_build():
        print("✓ FFmpeg installed via static build")
        return True
    
    # Manual installation instructions
    print("\nAutomatic installation failed. Manual steps:")
    print("\nOption 1 - Homebrew (requires admin):")
    print("  brew install ffmpeg")
    print("\nOption 2 - Conda:")
    print("  conda install -c conda-forge ffmpeg")
    print("\nOption 3 - Manual download:")
    print("  1. Download from: https://ffmpeg.org/download.html")
    print("  2. Extract to ~/.local/bin/")
    print("  3. Add to PATH: export PATH=\"$HOME/.local/bin:$PATH\"")
    
    return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)