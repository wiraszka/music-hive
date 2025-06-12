#!/usr/bin/env python3
"""
Test YouTube search functionality directly
"""

from search_youtube import YouTubeSearch
import logging

# Set up logging to see what's happening
logging.basicConfig(level=logging.INFO)

def test_search():
    print("Testing YouTube search...")
    
    try:
        youtube = YouTubeSearch()
        results = youtube.search("Flume", limit=5)
        
        print(f"Search returned {len(results) if results else 0} results")
        
        if results:
            for i, result in enumerate(results):
                print(f"\nResult {i+1}:")
                print(f"  Title: {result.get('title', 'No title')}")
                print(f"  Channel: {result.get('channel', 'No channel')}")
                print(f"  Duration: {result.get('duration', 'No duration')}")
                print(f"  URL: {result.get('url', 'No URL')}")
        else:
            print("No results returned from search")
            
    except Exception as e:
        print(f"Error during search: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_search()