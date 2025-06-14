#!/usr/bin/env python3
"""
Standalone FFmpeg installer for macOS
Handles Homebrew installation if needed
"""

import subprocess
import os
import sys

def check_ffmpeg():
    """Check if FFmpeg is already installed"""
    try:
        subprocess.check_output(["ffmpeg", "-version"], stderr=subprocess.DEVNULL)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def check_homebrew():
    """Check if Homebrew is installed"""
    try:
        subprocess.check_output(["brew", "--version"], stderr=subprocess.DEVNULL)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def install_homebrew():
    """Install Homebrew"""
    print("Installing Homebrew (this may take several minutes and require your password)...")
    try:
        # Use curl and bash directly
        cmd = 'curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh | bash'
        result = subprocess.run(cmd, shell=True, check=True, capture_output=False)
        
        # Update PATH for current session
        homebrew_paths = ["/opt/homebrew/bin", "/usr/local/bin"]
        current_path = os.environ.get("PATH", "")
        
        for path in homebrew_paths:
            if os.path.exists(path) and path not in current_path:
                os.environ["PATH"] = f"{path}:{current_path}"
                print(f"Added {path} to PATH")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to install Homebrew: {e}")
        return False

def install_ffmpeg():
    """Install FFmpeg via Homebrew"""
    print("Installing FFmpeg...")
    try:
        subprocess.check_call(["brew", "install", "ffmpeg"])
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to install FFmpeg: {e}")
        return False

def main():
    """Main installation process"""
    print("FFmpeg Installation for macOS")
    print("=" * 40)
    
    # Check if FFmpeg is already installed
    if check_ffmpeg():
        print("✓ FFmpeg is already installed")
        return True
    
    # Check if Homebrew is installed
    if not check_homebrew():
        print("Homebrew not found. Installing...")
        if not install_homebrew():
            print("\nFailed to install Homebrew automatically.")
            print("Please install manually:")
            print('Run: /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"')
            return False
        print("✓ Homebrew installed successfully")
    else:
        print("✓ Homebrew is already installed")
    
    # Install FFmpeg
    if not install_ffmpeg():
        print("\nFailed to install FFmpeg automatically.")
        print("Please install manually: brew install ffmpeg")
        return False
    
    print("✓ FFmpeg installed successfully")
    
    # Verify installation
    if check_ffmpeg():
        print("✓ FFmpeg installation verified")
        return True
    else:
        print("⚠ FFmpeg installation could not be verified")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)