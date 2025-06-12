"""
YouTube Search Module
Handles searching for videos on YouTube using yt-dlp
"""

import logging
from typing import List, Dict, Any, Optional
import yt_dlp
import subprocess
import json

logger = logging.getLogger(__name__)

class YouTubeSearch:
    """Class to handle YouTube searches"""
    
    def __init__(self):
        """Initialize YouTube search"""
        self.ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
            'default_search': 'ytsearch',
        }
        
    def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search YouTube for the given query using yt-dlp
        
        Args:
            query: The search query
            limit: Maximum number of results to return
            
        Returns:
            List of dictionaries with video info
        """
        try:
            search_query = f"ytsearch{limit}:{query}"
            
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                search_results = ydl.extract_info(search_query, download=False)
                
                if not search_results or 'entries' not in search_results:
                    logger.warning(f"No results found for query: {query}")
                    return []
                
                results = []
                for entry in search_results['entries']:
                    if entry and entry.get('id'):
                        # Use basic info from search results - much faster and more reliable
                        duration_str = "Unknown"
                        if entry.get('duration'):
                            try:
                                duration = int(float(entry['duration']))  # Convert to int, handling floats
                                mins, secs = divmod(duration, 60)
                                duration_str = f"{mins:02d}:{secs:02d}"
                            except (ValueError, TypeError):
                                duration_str = "Unknown"
                        
                        results.append({
                            'id': entry['id'],
                            'title': entry.get('title', 'Unknown Title'),
                            'channel': entry.get('uploader', 'Unknown Channel'), 
                            'url': f"https://www.youtube.com/watch?v={entry['id']}",
                            'duration': duration_str,
                            'view_count': entry.get('view_count', 0),
                            'upload_date': entry.get('upload_date', ''),
                            'description': entry.get('description', '')[:200] + '...' if entry.get('description') else ''
                        })
                
                return results
                
        except Exception as e:
            logger.error(f"YouTube search error: {str(e)}")
            return []
    
    def get_video_details(self, video_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific video
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            Dictionary with video details or None if failed
        """
        try:
            url = f"https://www.youtube.com/watch?v={video_id}"
            
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                if not info:
                    return None
                
                duration_str = "Unknown"
                if info.get('duration'):
                    try:
                        duration = int(float(info['duration']))  # Convert to int, handling floats
                        mins, secs = divmod(duration, 60)
                        duration_str = f"{mins:02d}:{secs:02d}"
                    except (ValueError, TypeError):
                        duration_str = "Unknown"
                
                return {
                    'id': video_id,
                    'title': info.get('title', 'Unknown Title'),
                    'channel': info.get('uploader', 'Unknown Channel'),
                    'duration': duration_str,
                    'url': url,
                    'view_count': info.get('view_count', 0),
                    'upload_date': info.get('upload_date', ''),
                    'description': info.get('description', '')[:200] + '...' if info.get('description') else ''
                }
            
        except Exception as e:
            logger.error(f"Error getting video details: {str(e)}")
            return None
