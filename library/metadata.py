"""
Metadata manager module
Handles updating metadata for music files
"""

import os
import logging
from typing import Dict, Any, Optional
import requests
from io import BytesIO
import mutagen
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TDRC, APIC
from mutagen.mp3 import MP3
from mutagen.flac import FLAC, Picture
from mutagen.mp4 import MP4, MP4Cover

logger = logging.getLogger(__name__)

class MetadataManager:
    """Class to handle music metadata updates"""
    
    def __init__(self):
        """Initialize the metadata manager"""
        pass
    
    def update_metadata(self, file_path: str, metadata: Dict[str, Any]) -> bool:
        """
        Update metadata for a music file
        
        Args:
            file_path: Path to the music file
            metadata: Dictionary with metadata to apply
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Determine file type
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext == '.mp3':
                return self._update_mp3_metadata(file_path, metadata)
            elif file_ext == '.flac':
                return self._update_flac_metadata(file_path, metadata)
            elif file_ext == '.m4a':
                return self._update_m4a_metadata(file_path, metadata)
            else:
                logger.warning(f"Unsupported file format for metadata update: {file_ext}")
                return False
                
        except Exception as e:
            logger.error(f"Error updating metadata for {file_path}: {str(e)}")
            return False
    
    def _update_mp3_metadata(self, file_path: str, metadata: Dict[str, Any]) -> bool:
        """
        Update metadata for an MP3 file
        
        Args:
            file_path: Path to MP3 file
            metadata: Dictionary with metadata to apply
            
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
                album_art_data = self._download_album_art(metadata['album_art_url'])
                if album_art_data:
                    audio.tags.add(
                        APIC(
                            encoding=3,
                            mime='image/jpeg',
                            type=3,  # Cover (front)
                            desc='Cover',
                            data=album_art_data
                        )
                    )
            
            # Save the changes
            audio.save()
            return True
            
        except Exception as e:
            logger.error(f"Failed to update MP3 metadata: {str(e)}")
            return False
    
    def _update_flac_metadata(self, file_path: str, metadata: Dict[str, Any]) -> bool:
        """
        Update metadata for a FLAC file
        
        Args:
            file_path: Path to FLAC file
            metadata: Dictionary with metadata to apply
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Load the audio file
            audio = FLAC(file_path)
            
            # Apply the metadata
            if 'title' in metadata:
                audio['title'] = metadata['title']
            
            if 'artist' in metadata:
                audio['artist'] = metadata['artist']
                
            if 'album' in metadata:
                audio['album'] = metadata['album']
                
            if 'year' in metadata:
                audio['date'] = metadata['year']
            
            # Add album art if available
            if 'album_art_url' in metadata and metadata['album_art_url']:
                album_art_data = self._download_album_art(metadata['album_art_url'])
                if album_art_data:
                    # Remove existing pictures
                    audio.clear_pictures()
                    
                    # Add new picture
                    picture = Picture()
                    picture.type = 3  # Cover (front)
                    picture.mime = 'image/jpeg'
                    picture.desc = 'Cover'
                    picture.data = album_art_data
                    
                    audio.add_picture(picture)
            
            # Save the changes
            audio.save()
            return True
            
        except Exception as e:
            logger.error(f"Failed to update FLAC metadata: {str(e)}")
            return False
    
    def _update_m4a_metadata(self, file_path: str, metadata: Dict[str, Any]) -> bool:
        """
        Update metadata for an M4A file
        
        Args:
            file_path: Path to M4A file
            metadata: Dictionary with metadata to apply
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Load the audio file
            audio = MP4(file_path)
            
            # Apply the metadata
            if 'title' in metadata:
                audio['\xa9nam'] = [metadata['title']]
            
            if 'artist' in metadata:
                audio['\xa9ART'] = [metadata['artist']]
                
            if 'album' in metadata:
                audio['\xa9alb'] = [metadata['album']]
                
            if 'year' in metadata:
                audio['\xa9day'] = [metadata['year']]
            
            # Add album art if available
            if 'album_art_url' in metadata and metadata['album_art_url']:
                album_art_data = self._download_album_art(metadata['album_art_url'])
                if album_art_data:
                    audio['covr'] = [MP4Cover(album_art_data, imageformat=MP4Cover.FORMAT_JPEG)]
            
            # Save the changes
            audio.save()
            return True
            
        except Exception as e:
            logger.error(f"Failed to update M4A metadata: {str(e)}")
            return False
    
    def _download_album_art(self, url: str) -> Optional[bytes]:
        """
        Download album art from URL
        
        Args:
            url: URL of the album art
            
        Returns:
            Binary data of the album art or None if failed
        """
        try:
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                return response.content
            else:
                logger.error(f"Failed to download album art: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error downloading album art: {str(e)}")
            return None
