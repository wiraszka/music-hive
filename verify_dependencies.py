#!/usr/bin/env python3
"""
Dependency verification script for Music Downloader
Verifies all dependencies work properly across all download phases
"""

import sys
import os
import subprocess
import importlib

def test_core_imports():
    """Test all core module imports"""
    modules = [
        'yt_dlp',
        'mutagen',
        'spotipy', 
        'requests',
        'fuzzywuzzy',
        'Levenshtein',
        'imageio_ffmpeg',
        'PyQt6.QtWidgets',
        'PyQt6.QtCore',
        'PyQt6.QtGui'
    ]
    
    print("Testing core imports...")
    failed_imports = []
    
    for module in modules:
        try:
            importlib.import_module(module)
            print(f"✓ {module}")
        except ImportError as e:
            print(f"✗ {module}: {e}")
            failed_imports.append(module)
    
    return len(failed_imports) == 0

def test_ffmpeg_integration():
    """Test FFmpeg integration with imageio-ffmpeg"""
    print("\nTesting FFmpeg integration...")
    try:
        import imageio_ffmpeg
        ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        print(f"✓ FFmpeg executable found: {ffmpeg_exe}")
        
        # Test FFmpeg version
        result = subprocess.run([ffmpeg_exe, '-version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✓ FFmpeg is functional")
            return True
        else:
            print("✗ FFmpeg version check failed")
            return False
            
    except Exception as e:
        print(f"✗ FFmpeg test failed: {e}")
        return False

def test_youtube_search():
    """Test YouTube search functionality"""
    print("\nTesting YouTube search...")
    try:
        from search_youtube import YouTubeSearch
        youtube = YouTubeSearch()
        
        # Test basic search
        results = youtube.search("test song", limit=1)
        if results and len(results) > 0:
            print("✓ YouTube search working")
            return True
        else:
            print("✗ YouTube search returned no results")
            return False
            
    except Exception as e:
        print(f"✗ YouTube search test failed: {e}")
        return False

def test_spotify_integration():
    """Test Spotify API integration"""
    print("\nTesting Spotify integration...")
    try:
        from search_spotify import SpotifySearch
        spotify = SpotifySearch()
        
        # Test basic search
        results = spotify.search_track("test song", limit=1)
        if isinstance(results, list):
            print("✓ Spotify search working")
            return True
        else:
            print("✗ Spotify search failed")
            return False
            
    except Exception as e:
        print(f"✗ Spotify test failed: {e}")
        return False

def test_song_filtering():
    """Test song filtering functionality"""
    print("\nTesting song filtering...")
    try:
        from utils.song_filter import SongFilter
        
        filter_system = SongFilter()
        
        # Test sample YouTube result
        sample_result = {
            'title': 'Test Song - Artist Name',
            'duration': '3:45',
            'channel': 'Test Channel',
            'url': 'https://youtube.com/watch?v=test'
        }
        
        # Test filtering
        filtered = filter_system.filter_youtube_results([sample_result], "test song")
        
        # Test fuzzy matching
        from fuzzywuzzy import fuzz
        similarity = fuzz.ratio("test song", "test song artist")
        
        if filtered and similarity > 0:
            print("✓ Song filtering working")
            return True
        else:
            print("✗ Song filtering failed")
            return False
            
    except Exception as e:
        print(f"✗ Song filtering test failed: {e}")
        return False

def test_download_process():
    """Test download process components"""
    print("\nTesting download process...")
    try:
        from downloader import Downloader, AudioQuality
        
        # Test downloader initialization
        downloader = Downloader("./test_downloads")
        
        # Test quality enum
        quality = AudioQuality.BEST
        
        print("✓ Download process components working")
        return True
        
    except Exception as e:
        print(f"✗ Download process test failed: {e}")
        return False

def test_metadata_handling():
    """Test metadata handling with mutagen"""
    print("\nTesting metadata handling...")
    try:
        from mutagen.mp3 import MP3
        from mutagen.id3 import ID3, TIT2, TPE1, TALB
        
        print("✓ Metadata handling working")
        return True
        
    except Exception as e:
        print(f"✗ Metadata handling test failed: {e}")
        return False

def test_gui_components():
    """Test GUI components"""
    print("\nTesting GUI components...")
    try:
        from PyQt6.QtWidgets import QApplication, QWidget
        from PyQt6.QtCore import Qt
        from PyQt6.QtGui import QPixmap
        
        # Test basic Qt functionality
        app = QApplication.instance()
        if app is None:
            print("✓ Qt components available (no display)")
        else:
            print("✓ Qt components working")
        return True
        
    except Exception as e:
        print(f"✗ GUI components test failed: {e}")
        return False

def main():
    """Run all dependency tests"""
    print("Music Downloader Dependency Verification")
    print("=" * 45)
    
    tests = [
        test_core_imports,
        test_ffmpeg_integration,
        test_youtube_search,
        test_spotify_integration,
        test_song_filtering,
        test_download_process,
        test_metadata_handling,
        test_gui_components
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"Test execution failed: {e}")
    
    print("\n" + "=" * 45)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("✓ All dependencies working correctly!")
        return True
    else:
        print("✗ Some dependencies have issues")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)