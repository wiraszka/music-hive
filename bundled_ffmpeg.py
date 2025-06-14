#!/usr/bin/env python3
"""
Self-contained FFmpeg solution using Python packages with bundled binaries
Works on Windows, macOS, and Linux without any manual installation
"""

import os
import sys
import subprocess
import platform

class BundledFFmpeg:
    def __init__(self):
        self.ffmpeg_path = None
        self.ffprobe_path = None
        
    def install_imageio_ffmpeg(self):
        """Install imageio-ffmpeg which includes FFmpeg binaries"""
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "imageio-ffmpeg"
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            import imageio_ffmpeg
            self.ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
            
            # Create ffprobe path (imageio-ffmpeg only provides ffmpeg)
            ffmpeg_dir = os.path.dirname(self.ffmpeg_path)
            ffprobe_name = "ffprobe"
            if platform.system() == "Windows":
                ffprobe_name += ".exe"
            self.ffprobe_path = os.path.join(ffmpeg_dir, ffprobe_name)
            
            # If ffprobe doesn't exist, create a wrapper
            if not os.path.exists(self.ffprobe_path):
                if platform.system() == "Windows":
                    # Create batch file wrapper for Windows
                    with open(self.ffprobe_path.replace('.exe', '.bat'), 'w') as f:
                        f.write(f'@echo off\n"{self.ffmpeg_path}" %*\n')
                    self.ffprobe_path = self.ffprobe_path.replace('.exe', '.bat')
                else:
                    # Create shell script wrapper for Unix
                    with open(self.ffprobe_path, 'w') as f:
                        f.write(f'#!/bin/bash\nexec "{self.ffmpeg_path}" "$@"\n')
                    os.chmod(self.ffprobe_path, 0o755)
            
            return True
            
        except Exception as e:
            print(f"Failed to install imageio-ffmpeg: {e}")
            return False
    
    def install_ffmpeg_python(self):
        """Install ffmpeg-python and try to get binaries"""
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "ffmpeg-python"
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # ffmpeg-python doesn't include binaries, but check if system ffmpeg exists
            import shutil
            self.ffmpeg_path = shutil.which('ffmpeg')
            self.ffprobe_path = shutil.which('ffprobe')
            
            return self.ffmpeg_path is not None
            
        except Exception:
            return False
    
    def download_static_binaries(self):
        """Download static FFmpeg binaries directly"""
        import urllib.request
        import zipfile
        import tempfile
        
        # Create binaries directory in the app folder
        app_dir = os.path.dirname(os.path.abspath(__file__))
        binaries_dir = os.path.join(app_dir, "ffmpeg_binaries")
        os.makedirs(binaries_dir, exist_ok=True)
        
        system = platform.system()
        machine = platform.machine().lower()
        
        # Reliable download URLs
        urls = {
            "Windows": "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip",
            "Darwin": "https://evermeet.cx/ffmpeg/getrelease/zip" if "arm" not in machine else "https://evermeet.cx/ffmpeg/getrelease/zip",
            "Linux": "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz"
        }
        
        if system not in urls:
            return False
        
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp_file:
                tmp_path = tmp_file.name
            
            print(f"Downloading FFmpeg for {system}...")
            urllib.request.urlretrieve(urls[system], tmp_path)
            
            # Extract files
            if tmp_path.endswith('.zip'):
                with zipfile.ZipFile(tmp_path, 'r') as zip_ref:
                    zip_ref.extractall(binaries_dir)
            else:
                import tarfile
                with tarfile.open(tmp_path, 'r:xz') as tar_ref:
                    tar_ref.extractall(binaries_dir)
            
            # Find extracted binaries
            for root, dirs, files in os.walk(binaries_dir):
                for file in files:
                    if file in ['ffmpeg', 'ffmpeg.exe']:
                        self.ffmpeg_path = os.path.join(root, file)
                    elif file in ['ffprobe', 'ffprobe.exe']:
                        self.ffprobe_path = os.path.join(root, file)
                        
                    # Make executable on Unix systems
                    if system != "Windows" and file in ['ffmpeg', 'ffprobe']:
                        os.chmod(os.path.join(root, file), 0o755)
            
            # Clean up
            os.unlink(tmp_path)
            
            return self.ffmpeg_path is not None
            
        except Exception as e:
            print(f"Failed to download static binaries: {e}")
            return False
    
    def get_ffmpeg_paths(self):
        """Get FFmpeg and FFprobe paths, installing if necessary"""
        # Check if already available
        if self.ffmpeg_path and os.path.exists(self.ffmpeg_path):
            return self.ffmpeg_path, self.ffprobe_path
        
        # Try imageio-ffmpeg first (most reliable)
        if self.install_imageio_ffmpeg():
            print("✓ FFmpeg installed via imageio-ffmpeg")
            return self.ffmpeg_path, self.ffprobe_path
        
        # Try ffmpeg-python
        if self.install_ffmpeg_python():
            print("✓ FFmpeg found via system installation")
            return self.ffmpeg_path, self.ffprobe_path
        
        # Download static binaries as fallback
        if self.download_static_binaries():
            print("✓ FFmpeg installed via static binaries")
            return self.ffmpeg_path, self.ffprobe_path
        
        print("✗ Failed to install FFmpeg automatically")
        return None, None

# Global instance
_bundled_ffmpeg = BundledFFmpeg()

def get_ffmpeg_executable():
    """Get FFmpeg executable path, installing automatically if needed"""
    ffmpeg_path, _ = _bundled_ffmpeg.get_ffmpeg_paths()
    return ffmpeg_path

def get_ffprobe_executable():
    """Get FFprobe executable path, installing automatically if needed"""
    _, ffprobe_path = _bundled_ffmpeg.get_ffmpeg_paths()
    return ffprobe_path

def ensure_ffmpeg_available():
    """Ensure FFmpeg is available, installing if necessary"""
    ffmpeg_path, ffprobe_path = _bundled_ffmpeg.get_ffmpeg_paths()
    return ffmpeg_path is not None

if __name__ == "__main__":
    if ensure_ffmpeg_available():
        ffmpeg = get_ffmpeg_executable()
        ffprobe = get_ffprobe_executable()
        print(f"FFmpeg: {ffmpeg}")
        print(f"FFprobe: {ffprobe}")
    else:
        print("Failed to install FFmpeg")
        sys.exit(1)