#!/usr/bin/env python3
"""
Automatic FFmpeg installer that works without user intervention
Downloads and sets up FFmpeg binaries automatically for any system
"""

import os
import sys
import subprocess
import urllib.request
import zipfile
import tarfile
import platform
import tempfile
import shutil
import json

class AutoFFmpegInstaller:
    def __init__(self):
        self.system = platform.system()
        self.machine = platform.machine().lower()
        self.app_dir = os.path.dirname(os.path.abspath(__file__))
        self.ffmpeg_dir = os.path.join(self.app_dir, "ffmpeg_binaries")
        
    def get_download_url(self):
        """Get the appropriate download URL for the current system"""
        urls = {
            "Darwin": {
                "arm64": "https://github.com/eugeneware/ffmpeg-static/releases/download/b6.0/darwin-arm64",
                "x86_64": "https://github.com/eugeneware/ffmpeg-static/releases/download/b6.0/darwin-x64"
            },
            "Windows": {
                "amd64": "https://github.com/eugeneware/ffmpeg-static/releases/download/b6.0/win32-x64.exe",
                "x86_64": "https://github.com/eugeneware/ffmpeg-static/releases/download/b6.0/win32-x64.exe"
            },
            "Linux": {
                "x86_64": "https://github.com/eugeneware/ffmpeg-static/releases/download/b6.0/linux-x64",
                "aarch64": "https://github.com/eugeneware/ffmpeg-static/releases/download/b6.0/linux-arm64"
            }
        }
        
        if self.system in urls and self.machine in urls[self.system]:
            return urls[self.system][self.machine]
        
        # Fallback URLs using John Van Sickle's static builds
        if self.system == "Linux":
            if "arm" in self.machine or "aarch64" in self.machine:
                return "https://johnvansickle.com/ffmpeg/builds/ffmpeg-git-arm64-static.tar.xz"
            else:
                return "https://johnvansickle.com/ffmpeg/builds/ffmpeg-git-amd64-static.tar.xz"
        
        return None

    def check_existing_ffmpeg(self):
        """Check if FFmpeg is already available"""
        # Check bundled version first
        bundled_ffmpeg = os.path.join(self.ffmpeg_dir, "ffmpeg")
        if self.system == "Windows":
            bundled_ffmpeg += ".exe"
            
        if os.path.exists(bundled_ffmpeg):
            try:
                subprocess.check_output([bundled_ffmpeg, "-version"], stderr=subprocess.DEVNULL)
                return bundled_ffmpeg
            except:
                pass
        
        # Check system PATH
        try:
            result = subprocess.run(["ffmpeg", "-version"], capture_output=True)
            if result.returncode == 0:
                return "ffmpeg"  # Available in PATH
        except FileNotFoundError:
            pass
            
        return None

    def download_ffmpeg_single_binary(self, url):
        """Download single binary FFmpeg (like from eugeneware)"""
        os.makedirs(self.ffmpeg_dir, exist_ok=True)
        
        ffmpeg_path = os.path.join(self.ffmpeg_dir, "ffmpeg")
        if self.system == "Windows":
            ffmpeg_path += ".exe"
        
        print("Downloading FFmpeg binary...")
        urllib.request.urlretrieve(url, ffmpeg_path)
        
        # Make executable on Unix systems
        if self.system != "Windows":
            os.chmod(ffmpeg_path, 0o755)
        
        # Create ffprobe as a copy of ffmpeg (ffmpeg can act as ffprobe with -f ffprobe)
        ffprobe_path = os.path.join(self.ffmpeg_dir, "ffprobe")
        if self.system == "Windows":
            ffprobe_path += ".exe"
        
        shutil.copy2(ffmpeg_path, ffprobe_path)
        
        return ffmpeg_path

    def download_ffmpeg_archive(self, url):
        """Download and extract FFmpeg from archive"""
        os.makedirs(self.ffmpeg_dir, exist_ok=True)
        
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_path = tmp_file.name
        
        try:
            print("Downloading FFmpeg archive...")
            urllib.request.urlretrieve(url, tmp_path)
            
            # Extract based on file type
            extract_dir = tempfile.mkdtemp()
            
            if url.endswith('.tar.xz'):
                with tarfile.open(tmp_path, 'r:xz') as tar:
                    tar.extractall(extract_dir)
            elif url.endswith('.zip'):
                with zipfile.ZipFile(tmp_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_dir)
            
            # Find and copy binaries
            for root, dirs, files in os.walk(extract_dir):
                for file in files:
                    if file in ['ffmpeg', 'ffprobe'] or file in ['ffmpeg.exe', 'ffprobe.exe']:
                        src_path = os.path.join(root, file)
                        dst_path = os.path.join(self.ffmpeg_dir, file)
                        shutil.copy2(src_path, dst_path)
                        
                        if self.system != "Windows":
                            os.chmod(dst_path, 0o755)
            
            # Clean up
            shutil.rmtree(extract_dir, ignore_errors=True)
            
        finally:
            os.unlink(tmp_path)
        
        ffmpeg_path = os.path.join(self.ffmpeg_dir, "ffmpeg")
        if self.system == "Windows":
            ffmpeg_path += ".exe"
            
        return ffmpeg_path if os.path.exists(ffmpeg_path) else None

    def install_ffmpeg_embedded(self):
        """Install FFmpeg using embedded Python approach"""
        try:
            # Try installing ffmpeg-python which includes binaries
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "ffmpeg-python"
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # ffmpeg-python doesn't include binaries, so try imageio-ffmpeg
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "imageio-ffmpeg"
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # Try to get ffmpeg path from imageio
            try:
                import imageio_ffmpeg
                ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
                if os.path.exists(ffmpeg_path):
                    return ffmpeg_path
            except:
                pass
                
        except:
            pass
        
        return None

    def install(self):
        """Main installation method"""
        print("Checking for FFmpeg...")
        
        # Check if already available
        existing = self.check_existing_ffmpeg()
        if existing:
            print(f"✓ FFmpeg found: {existing}")
            return existing
        
        print("FFmpeg not found, installing automatically...")
        
        # Try embedded Python package first
        embedded_path = self.install_ffmpeg_embedded()
        if embedded_path:
            print(f"✓ FFmpeg installed via Python package: {embedded_path}")
            return embedded_path
        
        # Try downloading static binary
        download_url = self.get_download_url()
        if not download_url:
            print(f"No automatic installation available for {self.system} {self.machine}")
            return None
        
        try:
            if download_url.endswith(('.tar.xz', '.zip')):
                ffmpeg_path = self.download_ffmpeg_archive(download_url)
            else:
                ffmpeg_path = self.download_ffmpeg_single_binary(download_url)
            
            if ffmpeg_path and os.path.exists(ffmpeg_path):
                # Verify it works
                try:
                    subprocess.check_output([ffmpeg_path, "-version"], stderr=subprocess.DEVNULL)
                    print(f"✓ FFmpeg installed successfully: {ffmpeg_path}")
                    return ffmpeg_path
                except:
                    print("Downloaded FFmpeg binary is not functional")
                    return None
            else:
                print("Failed to download FFmpeg binary")
                return None
                
        except Exception as e:
            print(f"Installation failed: {e}")
            return None

def install_ffmpeg_automatically():
    """Convenience function to install FFmpeg automatically"""
    installer = AutoFFmpegInstaller()
    return installer.install()

if __name__ == "__main__":
    ffmpeg_path = install_ffmpeg_automatically()
    if ffmpeg_path:
        print(f"FFmpeg is ready at: {ffmpeg_path}")
        sys.exit(0)
    else:
        print("Failed to install FFmpeg automatically")
        sys.exit(1)