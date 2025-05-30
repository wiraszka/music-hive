"""
Downloader module
Handles downloading music from YouTube using yt-dlp
"""

import os
import re
import logging
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
        self.ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',
            }],
            'outtmpl': os.path.join(download_dir, '%(title)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
            'noprogress': True,
            'progress_hooks': [],
        }
    
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
            # Configure yt-dlp options
            self.ydl_opts['postprocessors'][0]['preferredquality'] = quality.value.replace('k', '')
            
            # Set up progress hook
            def progress_hook(d):
                if d['status'] == 'downloading':
                    if progress_callback and 'downloaded_bytes' in d and 'total_bytes_estimate' in d:
                        percent = d['downloaded_bytes'] / d['total_bytes_estimate'] * 70.0  # 70% of progress for download
                        progress_callback(percent, "Downloading...")
                elif d['status'] == 'finished':
                    if progress_callback:
                        progress_callback(70.0, "Download complete. Processing audio...")
            
            if progress_callback:
                self.ydl_opts['progress_hooks'] = [progress_hook]
            
            # Download the file
            file_path = None
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=True)
                if 'entries' in info:  # In case it's a playlist
                    info = info['entries'][0]
                
                # Get the output filename
                filename = ydl.prepare_filename(info)
                base_filename = os.path.splitext(filename)[0]
                file_path = f"{base_filename}.mp3"
            
            # Apply metadata if available
            if song_info and file_path and os.path.exists(file_path):
                if progress_callback:
                    progress_callback(80.0, "Applying metadata...")
                    
                self._apply_metadata(file_path, song_info)
                
                if progress_callback:
                    progress_callback(100.0, "Download complete!")
                
                return True, file_path
            else:
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
