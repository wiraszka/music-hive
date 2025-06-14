"""
Downloader module
Handles downloading music from YouTube using yt-dlp
"""

import os
import re
import logging
import subprocess
import platform
from enum import Enum
from typing import Optional, Dict, Any, Tuple, Callable
import yt_dlp
import mutagen
from mutagen.id3 import ID3, TIT2, TPE1, TALB, APIC, TDRC
from mutagen.mp3 import MP3
import requests
from io import BytesIO

from search_spotify import search_track_on_spotify

logger = logging.getLogger(__name__)

class AudioQuality(Enum):
    """Audio quality options for downloads"""
    LOW = "128k"
    MEDIUM = "192k"
    HIGH = "256k"
    BEST = "320k"

class Downloader:
    """Class to handle downloading songs from YouTube"""
    
    def __init__(self, download_dir: str):
        """
        Initialize the downloader
        
        Args:
            download_dir: Directory where downloaded files will be saved
        """
        self.download_dir = download_dir
        
        # Create download directory if it doesn't exist
        if not os.path.exists(download_dir):
            os.makedirs(download_dir)
            
        # Set up yt-dlp options
        # Check for FFmpeg availability
        ffmpeg_path = self._find_ffmpeg()
        
        self.ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(download_dir, '%(title)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
            'noprogress': True,
            'progress_hooks': [],
            'prefer_ffmpeg': True,
            'keepvideo': False,
            'extract_flat': False,
        }
        
        # Set FFmpeg location for manual conversion
        self.ffmpeg_exe, self.ffprobe_exe = self._get_ffmpeg_executables()
        if self.ffmpeg_exe:
            ffmpeg_dir = os.path.dirname(self.ffmpeg_exe)
            self.ydl_opts['ffmpeg_location'] = ffmpeg_dir
            
            # Ensure ffprobe can be found by setting PATH
            current_path = os.environ.get('PATH', '')
            if ffmpeg_dir not in current_path:
                os.environ['PATH'] = f"{ffmpeg_dir}{os.pathsep}{current_path}"
                
        elif ffmpeg_path:
            self.ydl_opts['ffmpeg_location'] = ffmpeg_path
            self.ffmpeg_exe = None
    
    def _find_ffmpeg(self) -> Optional[str]:
        """
        Find FFmpeg executable path with automatic fallback to bundled version
        
        Returns:
            Path to FFmpeg directory or None to use system default
        """
        import shutil
        
        # Try imageio-ffmpeg first (bundled with the application)
        try:
            import imageio_ffmpeg
            ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
            if os.path.exists(ffmpeg_exe):
                return os.path.dirname(ffmpeg_exe)
        except ImportError:
            pass
        
        # Check if ffmpeg is available in system PATH
        ffmpeg_path = shutil.which('ffmpeg')
        if ffmpeg_path:
            return os.path.dirname(ffmpeg_path)
        
        # Try common installation locations
        possible_paths = [
            # User local installations
            os.path.expanduser('~/.local/bin/ffmpeg'),
            
            # System installations
            '/usr/bin/ffmpeg',
            '/usr/local/bin/ffmpeg', 
            '/opt/homebrew/bin/ffmpeg',  # macOS ARM
            
            # Windows paths
            'C:\\ffmpeg\\bin\\ffmpeg.exe',
            'C:\\Program Files\\ffmpeg\\bin\\ffmpeg.exe',
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                try:
                    subprocess.check_output([path, "-version"], stderr=subprocess.DEVNULL)
                    return os.path.dirname(path)
                except (subprocess.CalledProcessError, FileNotFoundError):
                    continue
        
        return None
    
    def _get_ffmpeg_executables(self) -> tuple[Optional[str], Optional[str]]:
        """
        Get specific paths to ffmpeg and ffprobe executables
        
        Returns:
            Tuple of (ffmpeg_path, ffprobe_path) or (None, None) if not found
        """
        # Try imageio-ffmpeg first
        try:
            import imageio_ffmpeg
            import shutil
            
            ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
            if os.path.exists(ffmpeg_exe):
                # imageio-ffmpeg only provides ffmpeg, create ffprobe
                ffmpeg_dir = os.path.dirname(ffmpeg_exe)
                ffprobe_exe = os.path.join(ffmpeg_dir, "ffprobe")
                
                # If ffprobe doesn't exist, create it by copying ffmpeg
                if not os.path.exists(ffprobe_exe):
                    try:
                        shutil.copy2(ffmpeg_exe, ffprobe_exe)
                        os.chmod(ffprobe_exe, 0o755)
                    except (OSError, PermissionError):
                        # If we can't create ffprobe, ffmpeg can still work alone
                        pass
                
                return ffmpeg_exe, ffprobe_exe
        except ImportError:
            pass
        
        # Try system PATH
        import shutil
        ffmpeg_exe = shutil.which('ffmpeg')
        ffprobe_exe = shutil.which('ffprobe')
        
        if ffmpeg_exe and ffprobe_exe:
            return ffmpeg_exe, ffprobe_exe
        elif ffmpeg_exe:
            # If only ffmpeg is found, ffprobe might be in the same directory
            ffmpeg_dir = os.path.dirname(ffmpeg_exe)
            ffprobe_exe = os.path.join(ffmpeg_dir, "ffprobe")
            if platform.system() == "Windows":
                ffprobe_exe += ".exe"
            
            if os.path.exists(ffprobe_exe):
                return ffmpeg_exe, ffprobe_exe
        
        return None, None
    
    def _convert_to_mp3(self, input_file: str, output_file: str, quality: AudioQuality) -> bool:
        """
        Convert audio file to MP3 using FFmpeg directly
        Bypasses ffprobe codec detection issues
        """
        if not self.ffmpeg_exe:
            return False
            
        try:
            quality_map = {
                AudioQuality.LOW: "128k",
                AudioQuality.MEDIUM: "192k", 
                AudioQuality.HIGH: "256k",
                AudioQuality.BEST: "320k"
            }
            
            bitrate = quality_map.get(quality, "320k")
            
            cmd = [
                self.ffmpeg_exe,
                '-i', input_file,
                '-acodec', 'libmp3lame',
                '-ab', bitrate,
                '-y',  # Overwrite output
                '-hide_banner',
                '-loglevel', 'error',
                output_file
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            return result.returncode == 0
            
        except Exception as e:
            logging.error(f"MP3 conversion failed: {e}")
            return False

    def download(self, 
                 video_url: str, 
                 song_info: Optional[Dict[str, Any]] = None,
                 quality: AudioQuality = AudioQuality.BEST,
                 progress_callback: Optional[Callable[[float, str], None]] = None) -> Tuple[bool, str]:
        """
        Download a song from YouTube
        
        Args:
            video_url: YouTube video URL
            song_info: Optional metadata to apply (from Spotify)
            quality: Audio quality for the download
            progress_callback: Optional callback for download progress updates
                               Function(progress_percent, status_message)
        
        Returns:
            Tuple of (success: bool, file_path or error_message: str)
        """
        try:
            # Set up progress hook
            def progress_hook(d):
                if d['status'] == 'downloading':
                    if progress_callback and 'downloaded_bytes' in d and 'total_bytes_estimate' in d:
                        percent = d['downloaded_bytes'] / d['total_bytes_estimate'] * 50.0  # 50% of progress for download
                        progress_callback(percent, "Downloading...")
                elif d['status'] == 'finished':
                    if progress_callback:
                        progress_callback(50.0, "Download complete. Converting to MP3...")
            
            if progress_callback:
                self.ydl_opts['progress_hooks'] = [progress_hook]
            
            # Download the raw audio file (no postprocessing)
            temp_file_path = None
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=True)
                if 'entries' in info:  # In case it's a playlist
                    info = info['entries'][0]
                
                # Get the downloaded filename
                temp_file_path = ydl.prepare_filename(info)
            
            if not temp_file_path or not os.path.exists(temp_file_path):
                return False, "Download failed - no file created"
            
            # Convert to MP3 manually to bypass ffprobe codec detection
            if progress_callback:
                progress_callback(60.0, "Converting to MP3...")
            
            base_filename = os.path.splitext(temp_file_path)[0]
            mp3_file_path = f"{base_filename}.mp3"
            
            # Perform manual conversion
            conversion_success = self._convert_to_mp3(temp_file_path, mp3_file_path, quality)
            
            if not conversion_success:
                return False, "MP3 conversion failed"
            
            # Clean up temporary file if it's different from MP3 file
            if temp_file_path != mp3_file_path and os.path.exists(temp_file_path):
                try:
                    os.remove(temp_file_path)
                    if progress_callback:
                        progress_callback(70.0, "Cleaning up temporary files...")
                except Exception as e:
                    # Log but don't fail the download for cleanup issues
                    logging.warning(f"Could not remove temporary file {temp_file_path}: {e}")
            
            # Clean up any temporary audio files that might have been downloaded
            temp_extensions = ['.webm', '.m4a', '.opus', '.ogg', '.aac']
            for ext in temp_extensions:
                temp_audio_file = f"{base_filename}{ext}"
                if os.path.exists(temp_audio_file) and temp_audio_file != mp3_file_path:
                    try:
                        os.remove(temp_audio_file)
                    except Exception as e:
                        logging.warning(f"Could not remove temporary audio file {temp_audio_file}: {e}")
            
            file_path = mp3_file_path
            
            # Apply metadata if available (Spotify or YouTube-extracted)
            if song_info and file_path and os.path.exists(file_path):
                metadata_source = song_info.get('source', 'spotify')
                
                if metadata_source == 'youtube_extracted':
                    if progress_callback:
                        progress_callback(80.0, "Applying extracted metadata...")
                    print(f"[DOWNLOAD DEBUG] Applying YouTube-extracted metadata to: {os.path.basename(file_path)}")
                elif metadata_source == 'youtube_fallback':
                    if progress_callback:
                        progress_callback(80.0, "Applying basic metadata...")
                    print(f"[DOWNLOAD DEBUG] Applying YouTube-fallback metadata to: {os.path.basename(file_path)}")
                else:
                    if progress_callback:
                        progress_callback(80.0, "Applying Spotify metadata...")
                    print(f"[DOWNLOAD DEBUG] Applying Spotify metadata to: {os.path.basename(file_path)}")
                
                success = self._apply_metadata(file_path, song_info)
                
                if success:
                    print(f"[DOWNLOAD DEBUG] Metadata successfully applied")
                else:
                    print(f"[DOWNLOAD DEBUG] Metadata application failed")
                
                if progress_callback:
                    progress_callback(100.0, "Download complete with metadata!")
                
                return True, file_path
            else:
                print(f"[DOWNLOAD DEBUG] Downloading without metadata")
                if progress_callback:
                    progress_callback(100.0, "Download complete!")
                return True, file_path
            
        except Exception as e:
            logger.error(f"Download error: {str(e)}")
            if progress_callback:
                progress_callback(0, f"Error: {str(e)}")
            return False, str(e)
            
    def _apply_metadata(self, file_path: str, metadata: Dict[str, Any]) -> bool:
        """
        Apply metadata to a downloaded MP3 file
        
        Args:
            file_path: Path to the MP3 file
            metadata: Dictionary with metadata fields
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Load the audio file
            audio = MP3(file_path, ID3=ID3)
            
            # Create ID3 tag if it doesn't exist
            if audio.tags is None:
                audio.add_tags()
            
            # Apply the metadata
            if 'title' in metadata:
                audio.tags.add(TIT2(encoding=3, text=metadata['title']))
            
            if 'artist' in metadata:
                audio.tags.add(TPE1(encoding=3, text=metadata['artist']))
                
            if 'album' in metadata:
                audio.tags.add(TALB(encoding=3, text=metadata['album']))
                
            if 'year' in metadata:
                audio.tags.add(TDRC(encoding=3, text=metadata['year']))
                
            # Add album art if available
            if 'album_art_url' in metadata and metadata['album_art_url']:
                try:
                    response = requests.get(metadata['album_art_url'])
                    if response.status_code == 200:
                        album_art_data = response.content
                        audio.tags.add(
                            APIC(
                                encoding=3,
                                mime='image/jpeg',
                                type=3,  # Cover (front)
                                desc='Cover',
                                data=album_art_data
                            )
                        )
                except Exception as e:
                    logger.error(f"Failed to add album art: {str(e)}")
            
            # Save the changes
            audio.save()
            return True
            
        except Exception as e:
            logger.error(f"Failed to apply metadata: {str(e)}")
            return False
