#!/usr/bin/env python3
"""
Test script to verify the fixes for search functionality and styling issues
"""

import sys
import os
from search_youtube import YouTubeSearch
from search_spotify import SpotifySearch

def test_youtube_search():
    """Test YouTube search functionality"""
    print("Testing YouTube search...")
    
    try:
        youtube = YouTubeSearch()
        results = youtube.search("The Beatles - Hey Jude", limit=3)
        
        if results:
            print(f"✓ YouTube search returned {len(results)} results")
            for i, result in enumerate(results):
                print(f"  {i+1}. {result['title']} by {result['channel']}")
                print(f"     Duration: {result.get('duration', 'Unknown')}")
                print(f"     URL: {result['url']}")
        else:
            print("✗ YouTube search returned no results")
            
    except Exception as e:
        print(f"✗ YouTube search failed: {e}")

def test_spotify_search():
    """Test Spotify search functionality"""
    print("\nTesting Spotify search...")
    
    try:
        spotify = SpotifySearch()
        results = spotify.search_track("The Beatles Hey Jude", limit=3)
        
        if results:
            print(f"✓ Spotify search returned {len(results)} results")
            for i, result in enumerate(results):
                print(f"  {i+1}. {result['name']} by {', '.join([artist['name'] for artist in result['artists']])}")
                print(f"     Album: {result['album']['name']}")
                print(f"     Duration: {result.get('duration_ms', 0) // 1000}s")
        else:
            print("✗ Spotify search returned no results")
            
    except Exception as e:
        print(f"✗ Spotify search failed: {e}")

def test_styling_fixes():
    """Test that styling fixes are in place"""
    print("\nTesting styling fixes...")
    
    try:
        from gui.style import get_stylesheet, Theme
        stylesheet = get_stylesheet(Theme.DARK)
        
        # Check for text color fixes
        if "color: #333333;" in stylesheet:
            print("✓ ComboBox text color fix applied")
        else:
            print("✗ ComboBox text color fix missing")
            
        if "QTableView {" in stylesheet and "color: #333333;" in stylesheet:
            print("✓ Table text color fix applied")
        else:
            print("✗ Table text color fix missing")
            
    except Exception as e:
        print(f"✗ Styling test failed: {e}")

def main():
    """Run all tests"""
    print("Running fix verification tests...\n")
    
    test_youtube_search()
    test_spotify_search()
    test_styling_fixes()
    
    print("\nTest completed!")

if __name__ == "__main__":
    main()