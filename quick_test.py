#!/usr/bin/env python3
"""Quick test of YouTube search fix"""

from search_youtube import YouTubeSearch
import logging

# Disable yt-dlp logging for cleaner output
logging.getLogger('yt_dlp').setLevel(logging.ERROR)

def test_search():
    youtube = YouTubeSearch()
    print("Testing YouTube search with yt-dlp...")
    
    try:
        results = youtube.search("Beatles Hey Jude", limit=2)
        if results:
            print(f"✓ Found {len(results)} results:")
            for i, result in enumerate(results):
                print(f"{i+1}. {result['title'][:50]}...")
                print(f"   Channel: {result['channel']}")
                print(f"   Duration: {result.get('duration', 'Unknown')}")
        else:
            print("No results found")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_search()