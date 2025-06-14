"""
Spotify Search Cache
Implements intelligent caching to reduce API calls
"""

import hashlib
import json
import time
from typing import Dict, List, Optional, Any
from pathlib import Path

class SpotifyCache:
    """Cache for Spotify search results to reduce API calls"""
    
    def __init__(self, cache_dir: str = "temp", cache_duration: int = 3600):
        """
        Initialize cache
        
        Args:
            cache_dir: Directory to store cache files
            cache_duration: Cache expiration time in seconds (default: 1 hour)
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.cache_duration = cache_duration
        self.memory_cache = {}  # In-memory cache for current session
        
        # Load existing cache file
        self.cache_file = self.cache_dir / "spotify_search_cache.json"
        self._load_cache()
    
    def _load_cache(self):
        """Load cache from disk"""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    disk_cache = json.load(f)
                    
                # Only load non-expired entries
                current_time = time.time()
                for key, entry in disk_cache.items():
                    if current_time - entry.get('timestamp', 0) < self.cache_duration:
                        self.memory_cache[key] = entry
                        
                print(f"[CACHE] Loaded {len(self.memory_cache)} cached entries")
        except Exception as e:
            print(f"[CACHE] Error loading cache: {e}")
            self.memory_cache = {}
    
    def _save_cache(self):
        """Save cache to disk"""
        try:
            # Only save non-expired entries
            current_time = time.time()
            valid_cache = {
                key: entry for key, entry in self.memory_cache.items()
                if current_time - entry.get('timestamp', 0) < self.cache_duration
            }
            
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(valid_cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[CACHE] Error saving cache: {e}")
    
    def _normalize_query(self, query: str) -> str:
        """Normalize search query for consistent caching"""
        return query.lower().strip()
    
    def _get_cache_key(self, query: str, limit: int = 5) -> str:
        """Generate cache key for a search query"""
        normalized = self._normalize_query(query)
        key_data = f"{normalized}|limit={limit}"
        return hashlib.md5(key_data.encode('utf-8')).hexdigest()
    
    def get(self, query: str, limit: int = 5) -> Optional[List[Dict[str, Any]]]:
        """
        Get cached search results
        
        Args:
            query: Search query
            limit: Result limit
            
        Returns:
            Cached results or None if not found/expired
        """
        cache_key = self._get_cache_key(query, limit)
        
        if cache_key in self.memory_cache:
            entry = self.memory_cache[cache_key]
            
            # Check if entry is still valid
            if time.time() - entry.get('timestamp', 0) < self.cache_duration:
                print(f"[CACHE HIT] Found cached results for: {query}")
                return entry.get('results', [])
            else:
                # Remove expired entry
                del self.memory_cache[cache_key]
                print(f"[CACHE EXPIRED] Removed expired entry for: {query}")
        
        print(f"[CACHE MISS] No cached results for: {query}")
        return None
    
    def put(self, query: str, results: List[Dict[str, Any]], limit: int = 5):
        """
        Cache search results
        
        Args:
            query: Search query
            results: Search results to cache
            limit: Result limit used
        """
        cache_key = self._get_cache_key(query, limit)
        
        entry = {
            'query': query,
            'results': results,
            'timestamp': time.time(),
            'limit': limit
        }
        
        self.memory_cache[cache_key] = entry
        print(f"[CACHE STORE] Cached {len(results)} results for: {query}")
        
        # Periodically save to disk (every 10 entries)
        if len(self.memory_cache) % 10 == 0:
            self._save_cache()
    
    def clear_expired(self):
        """Remove all expired entries from cache"""
        current_time = time.time()
        expired_keys = [
            key for key, entry in self.memory_cache.items()
            if current_time - entry.get('timestamp', 0) >= self.cache_duration
        ]
        
        for key in expired_keys:
            del self.memory_cache[key]
        
        if expired_keys:
            print(f"[CACHE] Cleared {len(expired_keys)} expired entries")
            self._save_cache()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        current_time = time.time()
        valid_entries = sum(
            1 for entry in self.memory_cache.values()
            if current_time - entry.get('timestamp', 0) < self.cache_duration
        )
        
        return {
            'total_entries': len(self.memory_cache),
            'valid_entries': valid_entries,
            'cache_duration': self.cache_duration,
            'cache_file': str(self.cache_file)
        }
    
    def __del__(self):
        """Save cache when object is destroyed"""
        try:
            self._save_cache()
        except:
            pass

# Global cache instance
_spotify_cache = None

def get_spotify_cache() -> SpotifyCache:
    """Get global Spotify cache instance"""
    global _spotify_cache
    if _spotify_cache is None:
        _spotify_cache = SpotifyCache()
    return _spotify_cache