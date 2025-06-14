"""
Spotify Search Module
Handles searching for tracks on Spotify and retrieving metadata
"""

import os
import logging
from typing import Dict, Any, Optional, List
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from utils.spotify_cache import get_spotify_cache

logger = logging.getLogger(__name__)

class SpotifySearch:
    """Class to handle Spotify searches and metadata retrieval"""
    
    def __init__(self):
        """Initialize Spotify search with API credentials"""
        # Get Spotify API credentials from environment variables or use defaults
        client_id = os.getenv('SPOTIFY_CLIENT_ID', 'd8d22be2095f480591ce7de628699e26')
        client_secret = os.getenv('SPOTIFY_CLIENT_SECRET', '71fbff9545254217b40e800f222cba84')
        
        # Initialize cache
        self.cache = get_spotify_cache()
        
        self.is_available = bool(client_id and client_secret)
        
        if self.is_available:
            try:
                # Set up Spotify client
                auth_manager = SpotifyClientCredentials(
                    client_id=client_id,
                    client_secret=client_secret
                )
                self.spotify = spotipy.Spotify(auth_manager=auth_manager)
                logger.info("Spotify API initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Spotify API: {str(e)}")
                self.is_available = False
                self.spotify = None
        else:
            logger.warning("Spotify API credentials not found. Spotify search will be unavailable.")
            self.spotify = None
    
    def search_track(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for tracks on Spotify
        
        Args:
            query: Search query (song name, artist, etc.)
            limit: Maximum number of results to return
            
        Returns:
            List of dictionaries with track info
        """
        if not self.is_available:
            logger.warning("Spotify search unavailable: API not initialized")
            return []
            
        # Check cache first
        cached_results = self.cache.get(query, limit)
        if cached_results is not None:
            return cached_results
            
        try:
            if not self.spotify:
                logger.warning("Spotify client not initialized")
                return []
                
            print(f"[API CALL] Making Spotify search for: {query}")
            results = self.spotify.search(q=query, type='track', limit=limit)
            if not results:
                # Cache empty result to avoid repeated API calls
                self.cache.put(query, [], limit)
                return []
                
            tracks = results.get('tracks', {}).get('items', []) if results else []
            
            formatted_results = []
            for track in tracks:
                # Extract artists
                artists = [artist['name'] for artist in track.get('artists', [])]
                artist_names = ', '.join(artists)
                
                # Get album art (smallest version for preview)
                album_art = None
                images = track.get('album', {}).get('images', [])
                if images:
                    # Sort by size and get the smallest for preview
                    sorted_images = sorted(images, key=lambda x: x.get('width', 0))
                    album_art = sorted_images[0]['url'] if sorted_images else None
                
                # Format track info
                track_info = {
                    'id': track['id'],
                    'title': track['name'],
                    'artist': artist_names,
                    'album': track.get('album', {}).get('name', ''),
                    'album_art': album_art,
                    'preview_url': track.get('preview_url'),
                    'release_date': track.get('album', {}).get('release_date', ''),
                    'duration_ms': track.get('duration_ms', 0),
                    'artists': [{'name': artist['name']} for artist in track.get('artists', [])]
                }
                
                formatted_results.append(track_info)
            
            # Cache the results
            self.cache.put(query, formatted_results, limit)
            return formatted_results
            
        except Exception as e:
            logger.error(f"Spotify search error: {str(e)}")
            return []
            
    def get_track_metadata(self, track_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed metadata for a specific track
        
        Args:
            track_id: Spotify track ID
            
        Returns:
            Dictionary with track metadata or None if failed
        """
        if not self.is_available:
            logger.warning("Spotify metadata unavailable: API not initialized")
            return None
            
        try:
            track = self.spotify.track(track_id)
            
            # Extract artists
            artists = [artist['name'] for artist in track.get('artists', [])]
            artist_names = ', '.join(artists)
            
            # Get highest quality album art for final metadata
            album_art = None
            images = track.get('album', {}).get('images', [])
            if images:
                # Sort by size and get the largest
                sorted_images = sorted(images, key=lambda x: x.get('width', 0), reverse=True)
                album_art = sorted_images[0]['url'] if sorted_images else None
            
            # Get release year
            release_date = track.get('album', {}).get('release_date', '')
            release_year = release_date.split('-')[0] if release_date else ''
            
            # Format track metadata
            metadata = {
                'title': track['name'],
                'artist': artist_names,
                'album': track.get('album', {}).get('name', ''),
                'album_art_url': album_art,
                'year': release_year,
                'track_number': track.get('track_number'),
                'disc_number': track.get('disc_number'),
                'duration_ms': track.get('duration_ms'),
                'explicit': track.get('explicit', False),
                'isrc': track.get('external_ids', {}).get('isrc')
            }
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error getting track metadata: {str(e)}")
            return None

def search_track_on_spotify(query: str) -> Optional[Dict[str, Any]]:
    """
    Convenience function to search for a track on Spotify and return the best match
    
    Args:
        query: Search query (song name, artist, etc.)
        
    Returns:
        Dictionary with track metadata or None if no match found
    """
    spotify = SpotifySearch()
    
    if not spotify.is_available:
        return None
        
    # Search for the track
    results = spotify.search_track(query, limit=1)
    
    if not results:
        return None
        
    # Get full metadata for the top result
    track_id = results[0]['id']
    return spotify.get_track_metadata(track_id)
