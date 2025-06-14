#!/usr/bin/env python3
"""
Test FFmpeg direct installation without admin privileges
"""

import os
import sys
import subprocess
import urllib.request
import zipfile
import platform

def test_ffmpeg_direct_install():
    """Test direct FFmpeg installation"""
    print("Testing direct FFmpeg installation...")
    
    # Create local bin directory
    home_dir = os.path.expanduser("~")
    local_bin = os.path.join(home_dir, ".local", "bin")
    os.makedirs(local_bin, exist_ok=True)
    
    # Download FFmpeg from evermeet.cx (reliable static builds for macOS)
    binaries = ['ffmpeg', 'ffprobe']
    base_url = "https://evermeet.cx/ffmpeg"
    
    try:
        for binary in binaries:
            print(f"Downloading {binary}...")
            download_url = f"{base_url}/{binary}.zip"
            zip_path = os.path.join(local_bin, f"{binary}.zip")
            
            # Download
            urllib.request.urlretrieve(download_url, zip_path)
            
            # Extract binary
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extract(binary, local_bin)
            
            # Make executable
            binary_path = os.path.join(local_bin, binary)
            os.chmod(binary_path, 0o755)
            
            # Clean up zip
            os.remove(zip_path)
            print(f"✓ {binary} installed to {binary_path}")
        
        # Update PATH for current session
        current_path = os.environ.get("PATH", "")
        if local_bin not in current_path:
            os.environ["PATH"] = f"{local_bin}:{current_path}"
            print(f"✓ Added {local_bin} to PATH")
        
        # Test FFmpeg
        try:
            result = subprocess.run(["ffmpeg", "-version"], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print("✓ FFmpeg is working correctly")
                print(f"Version: {result.stdout.split('ffmpeg version')[1].split()[0]}")
                return True
            else:
                print("✗ FFmpeg test failed")
                return False
        except Exception as e:
            print(f"✗ FFmpeg test error: {e}")
            return False
            
    except Exception as e:
        print(f"✗ Installation failed: {e}")
        return False

def main():
    """Main test function"""
    print("FFmpeg Direct Installation Test")
    print("=" * 35)
    
    system = platform.system()
    print(f"System: {system}")
    
    if system != "Darwin":
        print("This test is designed for macOS")
        return False
    
    # Check if FFmpeg is already available
    try:
        result = subprocess.run(["ffmpeg", "-version"], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✓ FFmpeg already available")
            return True
    except:
        pass
    
    # Test direct installation
    return test_ffmpeg_direct_install()

if __name__ == "__main__":
    success = main()
    print(f"\nTest {'PASSED' if success else 'FAILED'}")
    sys.exit(0 if success else 1)