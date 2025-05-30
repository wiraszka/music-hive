"""
YouTube Search Module
Handles searching for videos on YouTube
"""

import re
import logging
from typing import List, Dict, Any, Tuple, Optional
from urllib.parse import quote
import requests

logger = logging.getLogger(__name__)

class YouTubeSearch:
    """Class to handle YouTube searches"""
    
    def __init__(self):
        """Initialize YouTube search"""
        self.base_url = "https://www.youtube.com"
        self.search_url = f"{self.base_url}/results?search_query="
        
    def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search YouTube for the given query
        
        Args:
            query: The search query
            limit: Maximum number of results to return
            
        Returns:
            List of dictionaries with video info
        """
        try:
            # Clean up the query
            encoded_query = quote(query)
            url = f"{self.search_url}{encoded_query}"
            
            # Make the request
            response = requests.get(url)
            
            if response.status_code != 200:
                logger.error(f"YouTube search request failed: {response.status_code}")
                return []
            
            # Extract video IDs and details using regex
            video_ids = re.findall(r'watch\?v=(\S{11})', response.text)
            
            # Remove duplicate IDs
            unique_video_ids = []
            for vid in video_ids:
                if vid not in unique_video_ids:
                    unique_video_ids.append(vid)
            
            # Limit results
            unique_video_ids = unique_video_ids[:limit]
            
            # Get video details
            results = []
            for video_id in unique_video_ids:
                # Extract basic information using regex patterns
                title_pattern = f'title=".*?" aria-label=".*? by .+?" href="/watch\\?v={video_id}"'
                title_match = re.search(title_pattern, response.text)
                
                if title_match:
                    title_text = title_match.group(0)
                    title = re.search(r'aria-label="(.*?) by', title_text)
                    channel = re.search(r'by (.+?)"', title_text)
                    
                    title_str = title.group(1) if title else "Unknown Title"
                    channel_str = channel.group(1) if channel else "Unknown Channel"
                    
                    results.append({
                        'id': video_id,
                        'title': title_str,
                        'channel': channel_str,
                        'url': f"https://www.youtube.com/watch?v={video_id}"
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
            url = f"{self.base_url}/watch?v={video_id}"
            response = requests.get(url)
            
            if response.status_code != 200:
                logger.error(f"Failed to get video details: {response.status_code}")
                return None
                
            # Extract title
            title_match = re.search(r'<title>(.*?) - YouTube</title>', response.text)
            title = title_match.group(1) if title_match else "Unknown Title"
            
            # Extract channel
            channel_match = re.search(r'"channelName":"(.*?)"', response.text)
            channel = channel_match.group(1) if channel_match else "Unknown Channel"
            
            # Extract duration
            duration_match = re.search(r'"lengthSeconds":"(\d+)"', response.text)
            duration = int(duration_match.group(1)) if duration_match else 0
            
            return {
                'id': video_id,
                'title': title,
                'channel': channel,
                'duration': duration,
                'url': url
            }
            
        except Exception as e:
            logger.error(f"Error getting video details: {str(e)}")
            return None
