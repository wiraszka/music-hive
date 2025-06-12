#!/usr/bin/env python3
"""
Diagnose GUI display issue by testing components individually
"""

from search_youtube import YouTubeSearch
from search_spotify import SpotifySearch
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)

def test_youtube_search():
    """Test YouTube search directly"""
    print("=== Testing YouTube Search for 'Flume' ===")
    youtube = YouTubeSearch()
    results = youtube.search("Flume", limit=3)
    
    print(f"Results count: {len(results) if results else 0}")
    if results:
        for i, result in enumerate(results):
            print(f"Result {i+1}:")
            print(f"  ID: {result.get('id')}")
            print(f"  Title: {result.get('title')}")
            print(f"  Channel: {result.get('channel')}")
            print(f"  Duration: {result.get('duration')}")
            print(f"  URL: {result.get('url')}")
    
    return results

def test_spotify_search():
    """Test Spotify search"""
    print("\n=== Testing Spotify Search ===")
    try:
        spotify = SpotifySearch()
        if spotify.is_available:
            results = spotify.search_track("Flume Never Be Like You", limit=2)
            print(f"Spotify results count: {len(results) if results else 0}")
            if results:
                for i, result in enumerate(results):
                    print(f"Spotify Result {i+1}: {result.get('name', 'No name')}")
        else:
            print("Spotify not available")
    except Exception as e:
        print(f"Spotify error: {e}")

def test_gui_layout_creation():
    """Test if GUI layout components can be created"""
    print("\n=== Testing GUI Layout Creation ===")
    try:
        from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
        
        # Test basic widget creation
        widget = QWidget()
        layout = QVBoxLayout(widget)
        label = QLabel("Test Label")
        layout.addWidget(label)
        
        print("Basic widget creation: SUCCESS")
        print(f"Widget has layout: {widget.layout() is not None}")
        print(f"Layout has 1 item: {layout.count() == 1}")
        
    except Exception as e:
        print(f"GUI creation error: {e}")
        return False
    
    return True

def main():
    print("Diagnosing GUI display issue for Flume search...\n")
    
    # Test YouTube search
    youtube_results = test_youtube_search()
    
    # Test Spotify search  
    test_spotify_search()
    
    # Test GUI component creation
    gui_works = test_gui_layout_creation()
    
    print(f"\n=== DIAGNOSIS SUMMARY ===")
    print(f"YouTube search working: {len(youtube_results) > 0 if youtube_results else False}")
    print(f"GUI components can be created: {gui_works}")
    
    if youtube_results and len(youtube_results) > 0:
        print("\nYouTube search is working correctly.")
        print("Issue is likely in the GUI display logic or widget visibility.")
        print("\nSuggested fixes:")
        print("1. Check if results container is properly shown")
        print("2. Verify layout is correctly adding widgets")
        print("3. Ensure widget heights/visibility are set correctly")

if __name__ == "__main__":
    main()