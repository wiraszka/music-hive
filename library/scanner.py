"""
Library scanner module
Handles scanning the music library directory and retrieving track information
"""

import os
import logging
from typing import List, Dict, Any, Callable, Tuple
import mutagen
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TDRC, APIC
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from mutagen.mp4 import MP4

logger = logging.getLogger(__name__)

class LibraryScanner:
    """Class to handle music library scanning"""
    
    def __init__(self):
        """Initialize the library scanner"""
        # Supported file extensions
        self.supported_extensions = ('.mp3', '.flac', '.m4a', '.ogg', '.wav')
    
    def scan_directory(self, directory: str, 
                       progress_callback: Callable[[int, int, str], None] = None) -> List[Dict[str, Any]]:
        """
        Scan a directory for music files
        
        Args:
            directory: Directory to scan
            progress_callback: Optional callback function for progress updates
                              Function(current_count, total_count, current_file)
                              
        Returns:
            List of dictionaries with track information
        """
        tracks = []
        
        try:
            # Find all music files recursively
            all_files = []
            for root, _, files in os.walk(directory):
                for file in files:
                    if file.lower().endswith(self.supported_extensions):
                        all_files.append(os.path.join(root, file))
            
            # Sort files by name for consistent ordering
            all_files.sort()
            
            # Scan each file
            for i, file_path in enumerate(all_files):
                if progress_callback:
                    progress_callback(i, len(all_files), file_path)
                
                try:
                    track_info = self._extract_track_info(file_path)
                    if track_info:
                        tracks.append(track_info)
                except Exception as e:
                    logger.error(f"Error scanning file {file_path}: {str(e)}")
            
            if progress_callback:
                progress_callback(len(all_files), len(all_files), "Complete")
                
            return tracks
            
        except Exception as e:
            logger.error(f"Error scanning directory {directory}: {str(e)}")
            return tracks
    
    def _extract_track_info(self, file_path: str) -> Dict[str, Any]:
        """
        Extract track information from a music file
        
        Args:
            file_path: Path to the music file
            
        Returns:
            Dictionary with track information
        """
        try:
            # Initialize basic track info
            track_info = {
                'file_path': file_path,
                'filename': os.path.basename(file_path),
                'size': os.path.getsize(file_path),
                'title': '',
                'artist': '',
                'album': '',
                'year': '',
                'has_cover': False
            }
            
            # Use mutagen to extract metadata based on file type
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext == '.mp3':
                self._extract_mp3_info(file_path, track_info)
            elif file_ext == '.flac':
                self._extract_flac_info(file_path, track_info)
            elif file_ext == '.m4a':
                self._extract_m4a_info(file_path, track_info)
            else:
                # For other formats, just use basic mutagen
                audio = mutagen.File(file_path)
                if audio:
                    if 'title' in audio:
                        track_info['title'] = str(audio['title'][0])
                    if 'artist' in audio:
                        track_info['artist'] = str(audio['artist'][0])
                    if 'album' in audio:
                        track_info['album'] = str(audio['album'][0])
            
            # Use filename as fallback title if missing
            if not track_info['title']:
                track_info['title'] = os.path.splitext(track_info['filename'])[0]
            
            return track_info
            
        except Exception as e:
            logger.error(f"Error extracting track info from {file_path}: {str(e)}")
            return {
                'file_path': file_path,
                'filename': os.path.basename(file_path),
                'size': os.path.getsize(file_path),
                'title': os.path.splitext(os.path.basename(file_path))[0],
                'artist': '',
                'album': '',
                'year': '',
                'has_cover': False
            }
    
    def _extract_mp3_info(self, file_path: str, track_info: Dict[str, Any]):
        """
        Extract metadata from MP3 file
        
        Args:
            file_path: Path to MP3 file
            track_info: Track info dictionary to update
        """
        try:
            audio = MP3(file_path, ID3=ID3)
            
            if audio.tags:
                # Title
                if 'TIT2' in audio.tags:
                    track_info['title'] = str(audio.tags['TIT2'])
                
                # Artist
                if 'TPE1' in audio.tags:
                    track_info['artist'] = str(audio.tags['TPE1'])
                
                # Album
                if 'TALB' in audio.tags:
                    track_info['album'] = str(audio.tags['TALB'])
                
                # Year
                if 'TDRC' in audio.tags:
                    track_info['year'] = str(audio.tags['TDRC'])
                
                # Check for cover art
                if 'APIC:' in audio.tags or 'APIC:Cover' in audio.tags:
                    track_info['has_cover'] = True
        except Exception as e:
            logger.error(f"Error reading MP3 metadata from {file_path}: {str(e)}")
    
    def _extract_flac_info(self, file_path: str, track_info: Dict[str, Any]):
        """
        Extract metadata from FLAC file
        
        Args:
            file_path: Path to FLAC file
            track_info: Track info dictionary to update
        """
        try:
            audio = FLAC(file_path)
            
            # Title
            if 'title' in audio:
                track_info['title'] = str(audio['title'][0])
            
            # Artist
            if 'artist' in audio:
                track_info['artist'] = str(audio['artist'][0])
            
            # Album
            if 'album' in audio:
                track_info['album'] = str(audio['album'][0])
            
            # Year
            if 'date' in audio:
                track_info['year'] = str(audio['date'][0])
            
            # Check for cover art
            if audio.pictures:
                track_info['has_cover'] = True
        except Exception as e:
            logger.error(f"Error reading FLAC metadata from {file_path}: {str(e)}")
    
    def _extract_m4a_info(self, file_path: str, track_info: Dict[str, Any]):
        """
        Extract metadata from M4A file
        
        Args:
            file_path: Path to M4A file
            track_info: Track info dictionary to update
        """
        try:
            audio = MP4(file_path)
            
            # Title
            if '\xa9nam' in audio:
                track_info['title'] = str(audio['\xa9nam'][0])
            
            # Artist
            if '\xa9ART' in audio:
                track_info['artist'] = str(audio['\xa9ART'][0])
            
            # Album
            if '\xa9alb' in audio:
                track_info['album'] = str(audio['\xa9alb'][0])
            
            # Year
            if '\xa9day' in audio:
                track_info['year'] = str(audio['\xa9day'][0])
            
            # Check for cover art
            if 'covr' in audio:
                track_info['has_cover'] = True
        except Exception as e:
            logger.error(f"Error reading M4A metadata from {file_path}: {str(e)}")
